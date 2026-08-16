"""Shared framework: data assembly, ATR, triple-barrier labels, fee math.

Conventions (identical to study/ Phase 1):
  - Features at bar i use ONLY information available at bar i's CLOSE.
  - Entry is the OPEN of bar i+1.
  - Stop distance = STOP_ATR x ATR14 (RMA) computed at bar i.
  - Label rr=K: +1 if target (entry + K*stop_dist, longs) is hit BEFORE the stop,
    0 if stop first, NaN if unresolved within MAX_H bars (excluded from training).
  - Same-bar target+stop collisions are resolved on the 5m path inside that bar;
    if the 5m path is also ambiguous (same 5m bar), the trade counts as a LOSS
    (conservative).
  - Fees: 0.08% round trip taker. In R units: fee_R = 0.0008 * entry / stop_dist.
    Net R of a win = K - fee_R, of a loss = -1 - fee_R.
"""
import os
import numpy as np
import pandas as pd

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "LINKUSDT", "DOTUSDT"]
FEE_RT = 0.0008          # round-trip taker fee, fraction of notional
TEST_START = pd.Timestamp("2025-01-01", tz="UTC")   # untouched holdout
STOP_ATR = 1.5
MAX_H = 400              # bars until label times out

def load(sym, ival):
    return pd.read_parquet(f"{DATA}/klines_{sym}_{ival}.parquet")

def atr(df, n=14):
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    a = pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().values.copy()
    a[:n] = np.nan
    return a

def make_labels(df, df5, rr, stop_atr=STOP_ATR, max_h=MAX_H):
    """Triple-barrier labels for LONG and SHORT at every bar.

    df  : trading-TF klines (dt, o/h/l/c...), df5: 5m klines of same symbol.
    Returns DataFrame indexed like df with columns:
      long_y, short_y (1/0/NaN), stop_dist, entry, long_feeR (== short_feeR).
    """
    n = len(df)
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    a = atr(df)
    entry = np.r_[o[1:], np.nan]                       # open of next bar
    stop_dist = stop_atr * a
    res = {"entry": entry, "stop_dist": stop_dist}

    t5 = df5["dt"].values.astype("datetime64[ns]")
    h5 = df5["high"].values; l5 = df5["low"].values
    tbar = df["dt"].values.astype("datetime64[ns]")

    for side in ("long", "short"):
        y = np.full(n, np.nan)
        if side == "long":
            tgt = entry + rr * stop_dist; stp = entry - stop_dist
        else:
            tgt = entry - rr * stop_dist; stp = entry + stop_dist
        # walk forward bar by bar, vectorized over "signal bars still open"
        open_idx = np.arange(n - 1)
        open_idx = open_idx[~np.isnan(stop_dist[open_idx]) & ~np.isnan(entry[open_idx])]
        cur = open_idx + 1                              # bar being examined
        steps = 0
        pend_same = []                                  # same-bar collisions
        open_mask = np.ones(len(open_idx), bool)
        while open_mask.any() and steps < max_h:
            idx = np.where(open_mask)[0]
            c_ = cur[idx]
            valid = c_ < n
            idx, c_ = idx[valid], c_[valid]
            open_mask[np.where(open_mask)[0][~valid]] = False
            if len(idx) == 0:
                break
            if side == "long":
                hit_t = h[c_] >= tgt[open_idx[idx]]
                hit_s = l[c_] <= stp[open_idx[idx]]
            else:
                hit_t = l[c_] <= tgt[open_idx[idx]]
                hit_s = h[c_] >= stp[open_idx[idx]]
            both = hit_t & hit_s
            only_t = hit_t & ~hit_s
            only_s = hit_s & ~hit_t
            y[open_idx[idx[only_t]]] = 1.0
            y[open_idx[idx[only_s]]] = 0.0
            for j in idx[both]:
                pend_same.append((open_idx[j], c_[np.where(idx == j)[0][0]]))
            done = both | only_t | only_s
            open_mask[idx[done]] = False
            cur[idx[~done]] += 1
            steps += 1
        # same-bar collisions -> 5m path
        for sig_i, bar_i in pend_same:
            s0 = tbar[bar_i]
            s1 = tbar[bar_i + 1] if bar_i + 1 < n else s0 + np.timedelta64(1, "D")
            j0, j1 = np.searchsorted(t5, s0), np.searchsorted(t5, s1)
            lab = 0.0                                   # conservative default: loss
            for j in range(j0, j1):
                if side == "long":
                    ht = h5[j] >= tgt[sig_i]; hs = l5[j] <= stp[sig_i]
                else:
                    ht = l5[j] <= tgt[sig_i]; hs = h5[j] >= stp[sig_i]
                if ht and hs:
                    lab = 0.0; break
                if ht:
                    lab = 1.0; break
                if hs:
                    lab = 0.0; break
            y[sig_i] = lab
        res[f"{side}_y"] = y
    res["feeR"] = FEE_RT * entry / stop_dist
    return pd.DataFrame(res, index=df.index)

def net_R(y, rr, feeR):
    """Realized net R per resolved trade."""
    return np.where(y == 1, rr, -1.0) - feeR

def breakeven_wr(rr, feeR_med):
    return (1 + feeR_med) / (1 + rr)

def summarize(y, rr, feeR, label=""):
    m = ~np.isnan(y)
    if m.sum() == 0:
        return None
    w = np.nanmean(y[m]); n = int(m.sum())
    r = net_R(y[m], rr, feeR[m])
    return {"label": label, "n": n, "wr": round(float(w), 4),
            "expR": round(float(np.mean(r)), 4),
            "be_wr": round(float(breakeven_wr(rr, np.nanmedian(feeR[m]))), 4)}
