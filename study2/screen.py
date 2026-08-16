"""Single-feature edge screen on the TRAIN period only (pre-2025).

For every feature: bucket it (deciles if continuous, distinct values if
discrete <= 12 values), and for each bucket x {long,short} x {1:1, 2:1}
compute n, winrate, net expectancy per trade, breakeven WR.

Ranked output -> data/screen_{ival}.csv. Buckets with n < MIN_N dropped.
This tells us WHERE the information lives before any ML.
"""
import sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import core

MIN_N = 400

def screen(ival):
    M = pd.read_parquet(f"{core.DATA}/matrix_{ival}.parquet")
    M = M[M["dt"] < core.TEST_START]
    meta = {"sym", "dt", "entry", "stop_dist", "feeR",
            "long_y_11", "short_y_11", "long_y_21", "short_y_21"}
    feats = [c for c in M.columns if c not in meta]
    rows = []
    for f in feats:
        s = M[f]
        if s.notna().sum() < 5000:
            continue
        nun = s.nunique(dropna=True)
        if nun <= 12:
            M["_b"] = s.astype("object")
        else:
            try:
                M["_b"] = pd.qcut(s, 10, duplicates="drop")
            except Exception:
                continue
        for (b,), g in M.groupby(["_b"], observed=True):
            if len(g) < MIN_N:
                continue
            for side in ("long", "short"):
                for rr, tag in ((1.0, "11"), (2.0, "21")):
                    y = g[f"{side}_y_{tag}"].values
                    m = ~np.isnan(y)
                    if m.sum() < MIN_N:
                        continue
                    w = float(np.mean(y[m]))
                    fee = g["feeR"].values[m]
                    exp = float(np.mean(np.where(y[m] == 1, rr, -1.0) - fee))
                    be = float((1 + np.median(fee)) / (1 + rr))
                    rows.append({"feature": f, "bucket": str(b), "side": side,
                                 "rr": tag, "n": int(m.sum()), "wr": round(w, 4),
                                 "be_wr": round(be, 4), "edge_wr": round(w - be, 4),
                                 "expR": round(exp, 4)})
        M.drop(columns="_b", inplace=True)
    out = pd.DataFrame(rows).sort_values("expR", ascending=False)
    out.to_csv(f"{core.DATA}/screen_{ival}.csv", index=False)
    print(f"{ival}: {len(out)} bucket-tests, top edge:")
    print(out.head(25).to_string(index=False))
    return out

if __name__ == "__main__":
    for ival in (sys.argv[1:] or ["1h", "4h"]):
        screen(ival)
