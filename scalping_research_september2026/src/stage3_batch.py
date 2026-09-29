"""Batch stage-3: IS-only candidate selection from the gross-edge scan, robust exit optimisation,
OOS reported for verification only."""
import sys
import multiprocessing as mp

import numpy as np
import pandas as pd

from edge_agg import pooled

MAX_H = {"5m": 96, "15m": 96}


def select_candidates(tf, top=60):
    a = pooled(tf)
    a = a[(a.H <= MAX_H[tf]) & (a.is_mean > 0.12) & (a.is_t > 3) & (a.is_pos >= a.n_sym - 1) & (a.n_sym >= 6)]
    a = a.sort_values("is_t", ascending=False)
    # one row per (family, variant, htf, bias): keep best H
    a = a.drop_duplicates(["family", "variant", "htf", "bias"])
    a = a.groupby(["family", "variant"]).head(3)
    hd = a[a.family.str.startswith("hour_drift")].head(6)
    a = pd.concat([a[~a.family.str.startswith("hour_drift")], hd]).sort_values("is_t", ascending=False)
    return a.head(top)


def work(args):
    tf, family, variant, htf, bias = args
    from stage3b import eval_exits_robust
    try:
        r = eval_exits_robust(family, variant, htf, bias, tf=tf)
    except Exception as e:
        return args, None, str(e)
    r = r.assign(tf=tf, family=family, variant=variant, htf=htf, bias=bias)
    ok = r[(r.is_rob > 0) & (r.is_wr > 0.3) & (r.is_n >= 200)]
    return args, ok.head(5), None


if __name__ == "__main__":
    tf = sys.argv[1]
    cands = select_candidates(tf)
    print(f"{tf}: {len(cands)} candidates", flush=True)
    print(cands[["family", "variant", "htf", "bias", "H", "is_n", "is_mean", "is_t"]].round(3).to_string(), flush=True)
    tasks = [(tf, r.family, r.variant, r.htf, r.bias) for r in cands.itertuples()]
    out = []
    with mp.get_context("spawn").Pool(4) as p:
        for args, df, err in p.imap_unordered(work, tasks):
            if err:
                print("ERR", args, err, flush=True)
                continue
            print("done", args, "passing exits:", len(df), flush=True)
            out.append(df)
    res = pd.concat(out, ignore_index=True)
    res.to_parquet(f"../results/stage3_batch_{tf}.parquet")
    print("saved", len(res))
