"""Split entries: half at market on the HTF signal, half on LTF confirmation.

The objection to pure precision entry is that waiting for a retrace skips the
trades that never retrace, and those are disproportionately the winners. The
objection to pure market entry is that the fill is blind. Splitting the risk
answers both: tranche 1 goes on immediately so a runaway move is never missed,
tranche 2 only fills if the lower timeframe confirms.

Accounting, which decides whether the comparison is honest:
  - each tranche risks HALF of the signal's risk budget
  - each tranche carries its own stop and its own 2R target, measured from its
    own entry price
  - combined R per signal = 0.5*r1 + 0.5*r2, with r2 = 0 when tranche 2 never
    fills
  - DEPLOYED risk is tracked separately (1.0 when both fill, 0.5 when only the
    first does), because a variant that quietly risks less per signal would
    otherwise look artificially safe on a per-signal basis

Three variants are compared on identical signals:
  A  100% at market                       (the study's baseline)
  B  100% on LTF confirmation, else skip  (pure precision, pays the miss cost)
  C  50/50 split                          (the proposal under test)
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
def _resolve_from(idx, side, entry_px, stop, tgt, hi, lo, cl, max_hold):
    """Resolve one trade from a 1m index. Stop wins ties, always."""
    n = hi.shape[0]
    end = idx + max_hold
    if end > n - 1:
        end = n - 1
    for j in range(idx, end + 1):
        if side > 0:
            if lo[j] <= stop:
                return -1, stop
            if hi[j] >= tgt:
                return 1, tgt
        else:
            if hi[j] >= stop:
                return -1, stop
            if lo[j] <= tgt:
                return 1, tgt
    return 0, cl[end]


@njit(cache=True)
def _run(sig_i, side, atr, trig_i, stop_mult, rr, hi, lo, op, cl,
         max_hold, slip, taker):
    """For each signal resolve tranche 1 (market, at sig_i) and tranche 2
    (at trig_i, -1 meaning never confirmed). Returns per-tranche R."""
    m = sig_i.shape[0]
    r1 = np.zeros(m)
    r2 = np.zeros(m)
    f2 = np.zeros(m, dtype=np.int64)
    o1 = np.zeros(m, dtype=np.int64)
    o2 = np.zeros(m, dtype=np.int64)
    n = hi.shape[0]

    for k in range(m):
        i0 = sig_i[k]
        s = side[k]
        a = atr[k]
        if i0 < 0 or i0 >= n - 2 or a <= 0:
            r1[k] = np.nan
            r2[k] = np.nan
            continue
        # ---- tranche 1: market at the bar after the signal
        e1 = op[i0] * (1.0 + slip * s)
        st1 = e1 - s * stop_mult * a
        tg1 = e1 + s * rr * stop_mult * a
        oc1, xp1 = _resolve_from(i0, s, e1, st1, tg1, hi, lo, cl, max_hold)
        xp1 = xp1 * (1.0 - slip * s)
        risk1 = abs(e1 - st1)
        r1[k] = ((xp1 - e1) * s - (e1 + xp1) * taker) / risk1
        o1[k] = oc1

        # ---- tranche 2: only if the lower timeframe confirmed in the window
        j0 = trig_i[k]
        if j0 < 0 or j0 >= n - 2:
            r2[k] = np.nan
            continue
        e2 = op[j0] * (1.0 + slip * s)
        st2 = e2 - s * stop_mult * a
        tg2 = e2 + s * rr * stop_mult * a
        oc2, xp2 = _resolve_from(j0, s, e2, st2, tg2, hi, lo, cl, max_hold)
        xp2 = xp2 * (1.0 - slip * s)
        risk2 = abs(e2 - st2)
        r2[k] = ((xp2 - e2) * s - (e2 + xp2) * taker) / risk2
        o2[k] = oc2
        f2[k] = 1
    return r1, r2, f2, o1, o2


def find_trigger_idx(m1_dt, sig_dt, trig_dt, window_min):
    """First LTF trigger at or after each signal, within `window_min`."""
    sig = np.asarray(sig_dt, dtype="datetime64[ns]")
    trg = np.sort(np.asarray(trig_dt, dtype="datetime64[ns]"))
    pos = np.searchsorted(trg, sig, side="left")
    out = np.full(len(sig), np.datetime64("NaT"), dtype="datetime64[ns]")
    ok = pos < len(trg)
    cand = np.where(ok, trg[np.clip(pos, 0, len(trg) - 1)], np.datetime64("NaT"))
    within = ok & ((cand - sig).astype("timedelta64[m]").astype(float) <= window_min)
    out[within] = cand[within]
    idx = np.searchsorted(m1_dt, out, side="left")
    idx = np.where(np.isnat(out), -1, idx)
    return idx.astype(np.int64)


def run(signals, m1, trig_dt, stop_mult=2.0, rr=2.0, window_min=240,
        max_hold_min=60 * 24 * 10, w1=0.5, w2=0.5):
    """signals: close_dt, side, atr. trig_dt: LTF confirmation timestamps."""
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

    ti = find_trigger_idx(t, s["close_dt"].values, trig_dt, window_min)
    r1, r2, f2, o1, o2 = _run(
        i0.astype(np.int64), s["side"].to_numpy(np.int64),
        s["atr"].to_numpy(np.float64), ti,
        float(stop_mult), float(rr), hi, lo, op, cl,
        int(max_hold_min), float(E.SLIP), float(E.TAKER))

    df = pd.DataFrame({
        "close_dt": s["close_dt"].values, "side": s["side"].values,
        "r_market": r1, "r_precision": r2, "confirmed": f2.astype(bool),
        "out_market": o1, "out_precision": o2,
    })
    df = df[np.isfinite(df.r_market)].reset_index(drop=True)

    # variant A: everything at market
    a = df["r_market"]
    # variant B: precision only, unconfirmed signals are simply not traded
    b = df.loc[df.confirmed, "r_precision"]
    # variant C: split, tranche 2 contributes zero when unconfirmed
    c = w1 * df["r_market"] + w2 * df["r_precision"].fillna(0.0)
    deployed = w1 + w2 * df["confirmed"].astype(float)
    return df, a, b, c, deployed


def summarise(a, b, c, deployed, months, label=""):
    def block(x, name, dep=None):
        x = pd.Series(x).dropna()
        if len(x) < 30:
            return None
        cum = x.cumsum()
        dd = float((cum.cummax() - cum).max())
        moR = float(x.sum()) / months
        risk = float(dep.mean()) if dep is not None else 1.0
        return {"variant": name, "n": len(x), "expR": float(x.mean()),
                "expR_per_unit_risk": float(x.mean()) / risk if risk > 0 else np.nan,
                "avg_deployed": risk, "moR": moR, "maxDD_R": dd,
                "ratio": moR / dd if dd > 0 else np.nan,
                "monthly_ret": min(0.06 / dd, 0.02) * moR if dd > 0 else 0.0}
    rows = [block(a, "A market only"),
            block(b, "B precision only"),
            block(c, "C split 50/50", deployed)]
    return pd.DataFrame([r for r in rows if r])
