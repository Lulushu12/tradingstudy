"""Stage-1 mass scan: every signal variant x every HTF bias x 4 exit templates, per symbol.
Records per-year sums so we can check time-stability. Holdout (>= OOS_END) is discarded."""
import sys
import time
import multiprocessing as mp

import numpy as np
import pandas as pd

from data import SYMBOLS, IS_END, OOS_END, TF_MIN
from engine import simulate, FEE, SLIP
from lab import ctx
import features as fx
import signals as sg

HTFS = {"5m": ["15m", "30m", "1h", "2h", "4h", "12h", "1d"],
        "15m": ["1h", "2h", "4h", "12h", "1d"],
        "1m": ["5m", "15m", "1h", "4h"]}

# (name, sl_atr, tp_r, be_r, trail, trail_mult, max_bars)
EXITS = [("x1", 1.0, 1.5, 0.0, 0, 0.0, 0),
         ("x2", 1.5, 2.0, 0.0, 0, 0.0, 48),
         ("x3", 2.5, 2.0, 0.0, 0, 0.0, 0),
         ("x4", 2.0, 0.0, 0.0, 1, 3.0, 0)]
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
MIN_TRADES_IS = 40


def run_task(args):
    sym, tf, wave = args
    fams = sg.WAVE2 if wave == "w2" else sg.FAMILIES
    t0 = time.time()
    cx = ctx(sym, tf)
    idx = cx.df.index
    year = idx.year.values
    cut_oos = np.searchsorted(idx.values, OOS_END.to_datetime64())
    cut_is = np.searchsorted(idx.values, IS_END.to_datetime64())
    biases = [("none", "none", None)]
    for htf in HTFS[tf]:
        for kind in fx.BIAS_TYPES:
            biases.append((htf, kind, fx.htf_bias(cx, htf, kind)))
    rows = []
    zero_trail = cx.c
    for fam in fams:
        try:
            gen = list(fam(cx))
        except Exception as e:
            print("family failed", fam.__name__, sym, e, flush=True)
            continue
        for family, variant, sig, sl in gen:
            sig = np.asarray(sig, np.int64)
            sig[cut_oos:] = 0
            for htf, kind, b in biases:
                s = sig if b is None else np.where(b == sig, sig, 0)
                if np.count_nonzero(s[:cut_is]) < MIN_TRADES_IS:
                    continue
                for xn, sl_atr, tp_r, be_r, tr, tm, mb in EXITS:
                    sd = sl_atr * cx.atr if sl is None else np.maximum(sl, 0.5 * cx.atr)
                    tr_ = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sd, cx.atr, zero_trail,
                                   tp_r, be_r, tr, tm, mb, False, 0.0, 0.0, FEE, SLIP)
                    if tr_.shape[0] == 0:
                        continue
                    eb = tr_[:, 0].astype(np.int64) + 1
                    r = tr_[:, 6]
                    keep = eb < cut_oos
                    eb, r = eb[keep], r[keep]
                    yi = year[eb] - 2020
                    isb = eb < cut_is
                    row = dict(sym=sym, tf=tf, family=family, variant=variant, htf=htf, bias=kind, exit=xn,
                               is_n=int(isb.sum()), is_sum=float(r[isb].sum()), is_sq=float((r[isb] ** 2).sum()),
                               is_win=int((r[isb] > 0).sum()),
                               oos_n=int((~isb).sum()), oos_sum=float(r[~isb].sum()),
                               oos_sq=float((r[~isb] ** 2).sum()), oos_win=int((r[~isb] > 0).sum()),
                               sl_pct=float(np.median(tr_[:, 5])) * 100)
                    ys = np.bincount(yi, weights=r, minlength=6)
                    for k, y in enumerate(YEARS):
                        row[f"y{y}"] = float(ys[k])
                    rows.append(row)
        print(f"{sym} {tf} {fam.__name__} done, rows={len(rows)} t={time.time()-t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    df.to_parquet(f"../results/scan1_{sym}_{tf}{'' if wave == 'w1' else '_' + wave}.parquet")
    return sym, tf, len(rows), time.time() - t0


if __name__ == "__main__":
    tfs = sys.argv[1].split(",") if len(sys.argv) > 1 else ["5m"]
    syms = sys.argv[2].split(",") if len(sys.argv) > 2 else SYMBOLS
    wave = sys.argv[3] if len(sys.argv) > 3 else "w1"
    tasks = [(s, t, wave) for t in tfs for s in syms]
    with mp.get_context("spawn").Pool(min(4, len(tasks))) as p:
        for res in p.imap_unordered(run_task, tasks):
            print("DONE", res, flush=True)
