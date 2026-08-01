"""Divergence-driven exits and stop management.

The Part 7 result was that a same-direction divergence appearing AFTER entry
marks the losing cohort: a bullish divergence inside a long requires price to
have made a lower low, so the trade has already gone against you. Confirmed
signals returned -0.43 to +0.09 expR against +0.15 to +0.86 for signals that
never confirmed.

Using that for entry selection is impossible (membership is only known after the
fact, which is look-ahead). Using it for RISK MANAGEMENT is not: you are already
in the trade when the divergence prints, so acting on it is causal and
tradeable. That is the distinction this module rests on.

Variants, all against an identical entry (4h signal, market fill, 2xATR stop,
2R target):

  BASE     fixed stop and target, nothing else
  TIGHTEN  on the first same-direction divergence after entry, move the stop to
           the divergence pivot's own extreme (the swing low that formed a
           bullish divergence in a long), plus a small buffer. Risk falls; the
           original target is unchanged, so realised R:R improves - but a
           tighter stop is hit more often, which is the cost
  REDDOT   on the first adverse trigger-wave cross after entry, exit at market
  BOTH     tighten on divergence, and exit on an adverse cross

R is always measured against the ORIGINAL risk at entry, because that is what
the position was sized on. A tightened stop that gets hit therefore loses less
than 1R, which is precisely the effect being tested.
"""
import os
import sys

import numpy as np
import pandas as pd
from numba import njit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E        # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


@njit(cache=True)
def _walk(entry_i, side, entry_px, stop0, tgt, orig_risk,
          div_i, div_lvl, dot_i,
          hi, lo, cl, max_hold, mode, buf_frac):
    """mode: 0 BASE, 1 TIGHTEN, 2 REDDOT, 3 BOTH,
             4 SEQ (divergence arms, then red dot exits),
             5 SEQ+TIGHTEN (divergence arms and tightens, red dot exits).
    div_i/div_lvl: sorted 1m indices of same-direction divergence confirmations
    and the pivot price of each. dot_i: sorted indices of adverse WT crosses."""
    n = hi.shape[0]
    m = entry_i.shape[0]
    r_out = np.full(m, np.nan)
    kind = np.zeros(m, dtype=np.int64)      # 1 target, -1 stop, 2 signal, 0 time
    moved = np.zeros(m, dtype=np.int64)

    nd = div_i.shape[0]
    ndot = dot_i.shape[0]

    for k in range(m):
        i0 = entry_i[k]
        if i0 < 0 or i0 >= n - 2 or orig_risk[k] <= 0:
            continue
        s = side[k]
        stop = stop0[k]
        t = tgt[k]
        end = i0 + max_hold
        if end > n - 1:
            end = n - 1

        # pointer into the divergence array: first event at or after entry
        dp = 0
        while dp < nd and div_i[dp] < i0:
            dp += 1
        op = 0
        while op < ndot and dot_i[op] < i0:
            op += 1

        res_px = cl[end]
        res_kind = 0
        armed = False
        for j in range(i0, end + 1):
            # ---- a divergence at or before this bar arms the sequential exit
            if mode == 4 or mode == 5:
                while dp < nd and div_i[dp] <= j:
                    if not armed:
                        armed = True
                    if mode == 5 and moved[k] == 0:
                        lv = div_lvl[dp]
                        if lv == lv:
                            cand = lv - s * buf_frac * orig_risk[k]
                            if (s > 0 and cand > stop) or (s < 0 and cand < stop):
                                stop = cand
                                moved[k] = 1
                    dp += 1
            # ---- apply any divergence that confirmed at or before this bar
            if (mode == 1 or mode == 3) and moved[k] == 0:
                while dp < nd and div_i[dp] <= j:
                    lv = div_lvl[dp]
                    if lv == lv:                       # not NaN
                        cand = lv - s * buf_frac * orig_risk[k]
                        # only ever tighten, never widen
                        if (s > 0 and cand > stop) or (s < 0 and cand < stop):
                            stop = cand
                            moved[k] = 1
                    dp += 1
            # ---- adverse trigger-wave cross: exit at market on this bar close
            if mode == 2 or mode == 3 or ((mode == 4 or mode == 5) and armed):
                hit_dot = False
                while op < ndot and dot_i[op] <= j:
                    hit_dot = True
                    op += 1
                if hit_dot and j > i0:
                    res_px = cl[j]
                    res_kind = 2
                    break
            # ---- barriers, stop wins ties
            if s > 0:
                if lo[j] <= stop:
                    res_px = stop
                    res_kind = -1
                    break
                if hi[j] >= t:
                    res_px = t
                    res_kind = 1
                    break
            else:
                if hi[j] >= stop:
                    res_px = stop
                    res_kind = -1
                    break
                if lo[j] <= t:
                    res_px = t
                    res_kind = 1
                    break
        r_out[k] = res_px
        kind[k] = res_kind
    return r_out, kind, moved


def run(signals, m1, div_dt, div_level, dot_dt, mode, stop_mult=2.0, rr=2.0,
        max_hold_min=60 * 24 * 10, buf_frac=0.05,
        taker=E.TAKER, slip=E.SLIP):
    """signals: close_dt, side, atr. Returns a trade frame with net R."""
    m1 = m1.reset_index(drop=True)
    t = m1["dt"].values.astype("datetime64[ns]")
    hi = m1["high"].to_numpy(np.float64)
    lo = m1["low"].to_numpy(np.float64)
    op = m1["open"].to_numpy(np.float64)
    cl = m1["close"].to_numpy(np.float64)

    s = signals.reset_index(drop=True)
    want = (s["close_dt"] + pd.Timedelta(minutes=1)).values.astype("datetime64[ns]")
    i0 = np.searchsorted(t, want, side="left")
    keep = i0 < len(t) - 2
    s, i0 = s[keep].reset_index(drop=True), i0[keep]

    side = s["side"].to_numpy(np.int64)
    atr = s["atr"].to_numpy(np.float64)
    entry = op[i0] * (1.0 + slip * side)
    stop0 = entry - side * stop_mult * atr
    tgt = entry + side * rr * stop_mult * atr
    orig_risk = np.abs(entry - stop0)

    def _idx(dts):
        if dts is None or len(dts) == 0:
            return np.zeros(0, np.int64)
        a = np.sort(np.asarray(dts, dtype="datetime64[ns]"))
        return np.searchsorted(t, a, side="left").astype(np.int64)

    di = _idx(div_dt)
    dl = (np.asarray(div_level, np.float64)[np.argsort(
        np.asarray(div_dt, dtype="datetime64[ns]"))]
        if div_dt is not None and len(div_dt) else np.zeros(0, np.float64))
    oi = _idx(dot_dt)

    exit_px, kind, moved = _walk(
        i0.astype(np.int64), side, entry, stop0, tgt, orig_risk,
        di, dl, oi, hi, lo, cl, int(max_hold_min), int(mode), float(buf_frac))

    ok = np.isfinite(exit_px)
    xp = exit_px[ok] * (1.0 - slip * side[ok])
    e = entry[ok]
    r = ((xp - e) * side[ok] - (e + xp) * taker) / orig_risk[ok]
    return pd.DataFrame({
        "close_dt": s["close_dt"].values[ok],
        "side": side[ok], "r": r, "kind": kind[ok],
        "stop_moved": moved[ok].astype(bool),
    })


def summarise(df, months, label):
    if len(df) < 50:
        return None
    r = df["r"].values
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(cum) - cum))
    moR = float(r.sum()) / months
    k = df["kind"].values
    return {"variant": label, "n": len(df), "expR": float(r.mean()),
            "moR": moR, "maxDD_R": dd,
            "monthly_ret": min(0.06 / dd, 0.02) * moR if dd > 0 else 0.0,
            "pct_target": float((k == 1).mean()),
            "pct_stop": float((k == -1).mean()),
            "pct_signal_exit": float((k == 2).mean()),
            "pct_stop_moved": float(df["stop_moved"].mean()),
            "avg_loss": float(r[r < 0].mean()) if (r < 0).any() else np.nan,
            "avg_win": float(r[r > 0].mean()) if (r > 0).any() else np.nan}
