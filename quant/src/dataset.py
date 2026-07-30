"""Master bar-level dataset: features + precomputed trade outcomes, all assets.

One row per (symbol, bar). Columns: the 71 causal features, plus r_long/r_short
and their outcome codes for a given trade template. With this in memory, any
strategy is a row selection plus a side choice, and any ML model is a fit on
X -> r. That makes the whole search fast enough to be exhaustive.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import features as F      # noqa: E402
import labels as L        # noqa: E402

SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sets")


def build(tf="4h", atr_mult=2.0, rr=2.0, hold=60, block="DESIGN", syms=None,
          unlock=None, force=False):
    syms = syms or SYMS
    os.makedirs(CACHE, exist_ok=True)
    key = f"ds_{tf}_a{atr_mult}_rr{rr}_h{hold}_{block}_{len(syms)}"
    path = os.path.join(CACHE, key + ".parquet")
    if os.path.exists(path) and not force:
        return pd.read_parquet(path)

    frames = []
    for s in syms:
        bars, m1 = D.load(s, tf, block, unlock=unlock)
        f = F.build(bars, m1, tf)
        lb = L.make(s, tf, block, atr_mult=atr_mult, rr=rr,
                    max_hold_bars=hold, unlock=unlock)
        f = f[f["tradeable"]].reset_index(drop=True)
        kf = f["dt"].astype("int64").values
        kl = lb["dt"].astype("int64").values
        common = np.intersect1d(kf, kl)
        f = f[np.isin(kf, common)].reset_index(drop=True)
        lb = lb[np.isin(kl, common)].reset_index(drop=True)
        for c in ("r_long", "r_short", "out_long", "out_short",
                  "hold_long", "hold_short", "stoppct_long", "stoppct_short",
                  "exit_long", "exit_short"):
            f[c] = lb[c].values
        f["symbol"] = s
        frames.append(f)

    df = pd.concat(frames, ignore_index=True).sort_values(["dt", "symbol"])
    df = df.reset_index(drop=True)
    df.to_parquet(path, index=False, compression="zstd")
    return df


FEATS = None


def feature_list(df):
    global FEATS
    drop = {"dt", "close", "tradeable", "open_next", "atr", "symbol",
            "r_long", "r_short", "out_long", "out_short", "hold_long",
            "hold_short", "stoppct_long", "stoppct_short", "exit_long",
            "exit_short", "ret"}
    FEATS = [c for c in df.columns if c not in drop]
    return FEATS


if __name__ == "__main__":
    for tf, hold in [("4h", 60), ("1h", 96), ("30min", 96)]:
        d = build(tf=tf, hold=hold)
        print(f"{tf}: {d.shape}  {d.dt.min()} -> {d.dt.max()}  "
              f"feats={len(feature_list(d))}  "
              f"baseR long {d.r_long.mean():+.4f} short {d.r_short.mean():+.4f}")
