"""Multi-timeframe cascade: session-anchored levels, HTF gating, LTF entry timing.

Three things the study had not tested, in ascending order of how likely they are
to matter.

1. HTF REGIME GATING (least promising). Daily and weekly state attached causally
   to the signal bar. Already tested twice by other means and it failed both
   times: the prior study found stacking 1D+4H context "added constraints
   without adding edge", and the regime work here raised expectancy from +0.143
   to +0.33R while cutting monthly R from 7.33 to 2.73. Included for
   completeness, expected to pay the same frequency tax.

2. SESSION-ANCHORED CONFLUENCE LEVELS. Every level feature in the study so far
   has been a ROLLING extreme (`to_hi96`, `pos480`). Real levels are anchored to
   sessions - prior day high/low/close, prior week high/low, the weekly open,
   anchored VWAP, the opening range. Those are where resting orders actually
   sit, which is a different object from a rolling maximum.

3. LTF ENTRY REFINEMENT (the real gap). 1-minute data exists for every symbol
   and has only ever been used to RESOLVE trades, never to TIME them. Every
   backtest in this repo entered blind at "next bar open + 1 minute". Here the
   signal is unchanged but the fill is worked: wait up to W minutes for a
   pullback of p x ATR, and enter there.

   Why this is different in kind from filtering: it does not reduce trade count,
   so it does not pay the frequency tax that killed every previous filter. The
   two costs it DOES pay are measured explicitly - cost drag in R rises as the
   stop tightens, and trades that never pull back are skipped, which
   disproportionately removes the big winners. Both are reported.
"""
import os
import sys

import numpy as np
import pandas as pd
from numba import njit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import engine as E        # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


# ------------------------------------------------------- session-anchored levels
def session_levels(bars, m1):
    """Levels anchored to UTC day and ISO week, all strictly causal.

    A level for day D is only usable from the moment day D-1 has closed, so the
    prior-day values are shifted by one session before being broadcast.
    """
    b = bars.copy()
    dt = pd.DatetimeIndex(b["dt"])
    b["_day"] = dt.floor("D")
    b["_week"] = dt.to_period("W").start_time.tz_localize("UTC")

    # ---- prior day / prior week OHLC, computed on completed sessions only
    day = b.groupby("_day").agg(d_hi=("high", "max"), d_lo=("low", "min"),
                                d_cl=("close", "last"), d_op=("open", "first"))
    day[["pd_hi", "pd_lo", "pd_cl"]] = day[["d_hi", "d_lo", "d_cl"]].shift(1)
    wk = b.groupby("_week").agg(w_hi=("high", "max"), w_lo=("low", "min"),
                                w_cl=("close", "last"), w_op=("open", "first"))
    wk[["pw_hi", "pw_lo", "pw_cl"]] = wk[["w_hi", "w_lo", "w_cl"]].shift(1)

    b = b.merge(day[["pd_hi", "pd_lo", "pd_cl", "d_op"]], left_on="_day",
                right_index=True, how="left")
    b = b.merge(wk[["pw_hi", "pw_lo", "pw_cl", "w_op"]], left_on="_week",
                right_index=True, how="left")

    # ---- running session extremes and anchored VWAP, expanding within session
    g = b.groupby("_day")
    b["dsess_hi"] = g["high"].cummax()
    b["dsess_lo"] = g["low"].cummin()
    tp = (b["high"] + b["low"] + b["close"]) / 3.0
    pv = tp * b["volume"]
    b["vwap_d"] = pv.groupby(b["_day"]).cumsum() / \
        b["volume"].groupby(b["_day"]).cumsum().replace(0, np.nan)
    b["vwap_w"] = pv.groupby(b["_week"]).cumsum() / \
        b["volume"].groupby(b["_week"]).cumsum().replace(0, np.nan)

    # ---- opening range: first 4 bars of the UTC day
    idx_in_day = g.cumcount()
    b["_or"] = idx_in_day < 4
    orh = b[b["_or"]].groupby("_day")["high"].max().rename("or_hi")
    orl = b[b["_or"]].groupby("_day")["low"].min().rename("or_lo")
    b = b.merge(orh, left_on="_day", right_index=True, how="left")
    b = b.merge(orl, left_on="_day", right_index=True, how="left")
    # the opening range is only known after those 4 bars close
    b.loc[idx_in_day < 4, ["or_hi", "or_lo"]] = np.nan
    return b


LEVEL_COLS = ["pd_hi", "pd_lo", "pd_cl", "pw_hi", "pw_lo", "pw_cl",
              "d_op", "w_op", "vwap_d", "vwap_w", "or_hi", "or_lo",
              "dsess_hi", "dsess_lo"]


def level_features(b, atr):
    """Distance to each level in ATR units, plus a confluence count."""
    f = pd.DataFrame(index=b.index)
    c = b["close"]
    dists = []
    for col in LEVEL_COLS:
        if col not in b:
            continue
        d = (c - b[col]) / atr.replace(0, np.nan)
        f[f"d_{col}"] = d
        dists.append(d.abs())
    if dists:
        Dm = pd.concat(dists, axis=1)
        # how many distinct levels sit within 0.25 / 0.5 ATR of price
        f["confl_025"] = (Dm < 0.25).sum(axis=1)
        f["confl_050"] = (Dm < 0.50).sum(axis=1)
        f["nearest_lvl"] = Dm.min(axis=1)
        # is price pinned between two levels, or in open air?
        f["lvl_density"] = (Dm < 1.0).sum(axis=1)
    return f


# ------------------------------------------------------------- HTF regime gating
def htf_state(symbol, block="DESIGN"):
    """Daily and weekly state, returned on its own index for causal merging."""
    out = {}
    for tf, tag in (("1D", "d"), ("1W", "w")):
        bars, _ = D.load(symbol, tf, block, pad_bars=60)
        c, h, l = bars["close"], bars["high"], bars["low"]
        tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()],
                       axis=1).max(axis=1)
        atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
        s = pd.DataFrame({"dt": bars["dt"]})
        s[f"{tag}_disp5"] = (c - c.shift(5)) / atr
        s[f"{tag}_disp20"] = (c - c.shift(20)) / atr
        s[f"{tag}_pos20"] = ((c - l.rolling(20).min())
                             / (h.rolling(20).max() - l.rolling(20).min()).replace(0, np.nan))
        s[f"{tag}_atr_rank"] = (atr / c).rolling(60).rank(pct=True)
        s[f"{tag}_persist20"] = (np.log(c).diff().rolling(20).sum().abs()
                                 / np.log(c).diff().abs().rolling(20).sum().replace(0, np.nan))
        s[f"{tag}_up"] = (c > c.shift(1)).astype(float)
        # a bar stamped t is only complete at t + one period
        step = pd.Timedelta("1D") if tf == "1D" else pd.Timedelta("7D")
        s["_avail"] = (s["dt"] + step).astype("datetime64[ns, UTC]")
        out[tag] = s.drop(columns=["dt"]).sort_values("_avail")
    return out


def attach_htf(bars, states, tf):
    step = pd.Timedelta(tf)
    b = bars.copy()
    b["_cut"] = (b["dt"] + step).astype("datetime64[ns, UTC]")
    b = b.sort_values("_cut")
    for tag, s in states.items():
        b = pd.merge_asof(b, s, left_on="_cut", right_on="_avail",
                          direction="backward")
        b = b.drop(columns=["_avail"])
    return b.sort_values("dt").reset_index(drop=True)


# --------------------------------------------------------- LTF entry refinement
@njit(cache=True)
def _refine(sig_i, side, ref_px, atr, pull_mult, stop_mult, rr,
            wait_min, hi, lo, op, cl, max_hold):
    """For each signal: walk 1m bars from sig_i looking for a pullback of
    pull_mult*ATR against the signal direction within wait_min minutes. If found,
    enter there. Then resolve stop/target on the same 1m path, stop wins ties.

    Returns entry index, entry price, exit price, outcome, and a filled flag.
    """
    n = hi.shape[0]
    m = sig_i.shape[0]
    e_i = np.full(m, -1, dtype=np.int64)
    e_p = np.zeros(m)
    x_p = np.zeros(m)
    outc = np.zeros(m, dtype=np.int64)
    filled = np.zeros(m, dtype=np.int64)

    for k in range(m):
        i0 = sig_i[k]
        if i0 < 0 or i0 >= n - 2 or atr[k] <= 0:
            continue
        s = side[k]
        trig = ref_px[k] - s * pull_mult * atr[k]      # better price than signal
        end_wait = i0 + wait_min
        if end_wait > n - 2:
            end_wait = n - 2
        ent = -1
        for j in range(i0, end_wait + 1):
            if s > 0:
                if lo[j] <= trig:
                    ent = j
                    break
            else:
                if hi[j] >= trig:
                    ent = j
                    break
        if ent < 0:
            continue                                   # never pulled back: skip
        filled[k] = 1
        px = trig
        stop = px - s * stop_mult * atr[k]
        tgt = px + s * rr * stop_mult * atr[k]
        e_i[k] = ent
        e_p[k] = px
        jend = ent + max_hold
        if jend > n - 1:
            jend = n - 1
        res = 0
        xp = cl[jend]
        for j in range(ent, jend + 1):
            if s > 0:
                if lo[j] <= stop:
                    res, xp = -1, stop
                    break
                if hi[j] >= tgt:
                    res, xp = 1, tgt
                    break
            else:
                if hi[j] >= stop:
                    res, xp = -1, stop
                    break
                if lo[j] <= tgt:
                    res, xp = 1, tgt
                    break
        outc[k] = res
        x_p[k] = xp
    return e_i, e_p, x_p, outc, filled


def refine_entries(signals, m1, pull_mult, stop_mult=2.0, rr=2.0,
                   wait_min=240, max_hold_min=60 * 24 * 10,
                   taker=E.TAKER, slip=E.SLIP):
    """signals: close_dt, side, ref_px, atr. Returns a trade frame plus the
    fill rate, so the cost of the skipped no-pullback trades is visible."""
    m1 = m1.reset_index(drop=True)
    t = m1["dt"].values.astype("datetime64[ns]")
    hi = m1["high"].to_numpy(np.float64)
    lo = m1["low"].to_numpy(np.float64)
    op = m1["open"].to_numpy(np.float64)
    cl = m1["close"].to_numpy(np.float64)

    s = signals.reset_index(drop=True)
    want = (s["close_dt"] + pd.Timedelta(minutes=1)).values.astype("datetime64[ns]")
    i0 = np.searchsorted(t, want, side="left")
    ok = (i0 < len(t) - 2)
    s, i0 = s[ok].reset_index(drop=True), i0[ok]

    e_i, e_p, x_p, outc, filled = _refine(
        i0.astype(np.int64), s["side"].to_numpy(np.int64),
        s["ref_px"].to_numpy(np.float64), s["atr"].to_numpy(np.float64),
        float(pull_mult), float(stop_mult), float(rr), int(wait_min),
        hi, lo, op, cl, int(max_hold_min))

    f = filled.astype(bool)
    if f.sum() == 0:
        return pd.DataFrame(), 0.0
    side = s["side"].to_numpy(np.int64)[f]
    entry = e_p[f] * (1.0 + slip * side)
    exitp = x_p[f] * (1.0 - slip * side)
    risk = np.abs(entry - (e_p[f] - side * stop_mult * s["atr"].to_numpy()[f]))
    gross = (exitp - entry) * side
    fee = (entry + exitp) * taker
    r = (gross - fee) / np.where(risk > 0, risk, np.nan)

    out = pd.DataFrame({
        "close_dt": s["close_dt"].values[f],
        "entry_dt": t[e_i[f]],
        "side": side, "entry_px": entry, "exit_px": exitp,
        "outcome": outc[f], "r": r,
        "stop_pct": risk / entry,
    })
    return out, float(f.mean())
