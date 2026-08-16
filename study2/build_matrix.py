"""Assemble the full ML matrix: features + labels for all symbols on one TF.

Output: data/matrix_{ival}.parquet with columns:
  sym, dt, entry, stop_dist, feeR, long_y_11, short_y_11, long_y_21, short_y_21,
  and every feature column.
"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import core, features

def build(ival):
    kl_cache = {}
    for s in core.SYMS:
        for iv in {ival, "5m"}:
            kl_cache[(s, iv)] = core.load(s, iv)
    rows = []
    for sym in core.SYMS:
        t0 = time.time()
        df, X = features.build_features(sym, ival, kl_cache=kl_cache)
        d5 = kl_cache[(sym, "5m")]
        l11 = core.make_labels(df, d5, rr=1.0)
        l21 = core.make_labels(df, d5, rr=2.0)
        out = X.copy()
        out.insert(0, "sym", sym)
        out["entry"] = l11["entry"]; out["stop_dist"] = l11["stop_dist"]
        out["feeR"] = l11["feeR"]
        out["long_y_11"] = l11["long_y"]; out["short_y_11"] = l11["short_y"]
        out["long_y_21"] = l21["long_y"]; out["short_y_21"] = l21["short_y"]
        rows.append(out)
        print(f"{sym} {ival}: {len(out)} rows, {out.shape[1]} cols, {time.time()-t0:.1f}s", flush=True)
    M = pd.concat(rows, ignore_index=True)
    M.to_parquet(f"{core.DATA}/matrix_{ival}.parquet")
    print(f"matrix_{ival}: {M.shape}", flush=True)

if __name__ == "__main__":
    for ival in (sys.argv[1:] or ["1h", "4h"]):
        build(ival)
