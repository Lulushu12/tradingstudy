"""Exit-agnostic gross edge: mean signed forward return (entry next open -> close H bars later), in %.
Compare against ~0.12% round-trip cost. Signals within H bars of a previous counted signal are
dropped (non-overlapping), so counts and t-stats aren't inflated by clustering."""
import sys
import time
import multiprocessing as mp

import numpy as np
import pandas as pd
from numba import njit

from data import SYMBOLS, IS_END, OOS_END
from lab import ctx
import features as fx
import signals as sg
from scan import HTFS

HOR = [3, 6, 12, 24, 48, 96, 288]


@njit(cache=True)
def fwd_stats(sig, o, c, H, cut_is, cut_oos):
    n = sig.size
    s_is = s_oos = q_is = q_oos = 0.0
    n_is = n_oos = 0
    last = -10**9
    for i in range(n - H - 1):
        if i >= cut_oos:
            break
        d = sig[i]
        if d == 0 or i - last < H:
            continue
        last = i
        r = d * (c[i + H] / o[i + 1] - 1.0) * 100.0
        if i < cut_is:
            s_is += r; q_is += r * r; n_is += 1
        else:
            s_oos += r; q_oos += r * r; n_oos += 1
    return n_is, s_is, q_is, n_oos, s_oos, q_oos


def run_task(args):
    sym, tf, wave = args
    t0 = time.time()
    cx = ctx(sym, tf)
    idx = cx.df.index.values
    cut_oos = np.searchsorted(idx, OOS_END.to_datetime64())
    cut_is = np.searchsorted(idx, IS_END.to_datetime64())
    biases = [("none", "none", None)] + [(h, k, fx.htf_bias(cx, h, k)) for h in HTFS[tf] for k in fx.BIAS_TYPES]
    rows = []
    fams = sg.WAVE2 if wave == "w2" else sg.FAMILIES
    for fam in fams:
        for family, variant, sig, _ in fam(cx):
            if variant.endswith("structsl") or variant.endswith("midsl") or variant.endswith("atrsl"):
                continue  # same entries as the base variant
            sig = np.asarray(sig, np.int64)
            for htf, kind, b in biases:
                s = sig if b is None else np.where(b == sig, sig, 0)
                for H in HOR:
                    ni, si, qi, no, so, qo = fwd_stats(s, cx.o, cx.c, H, cut_is, cut_oos)
                    if ni < 30:
                        continue
                    rows.append((sym, tf, family, variant, htf, kind, H, ni, si, qi, no, so, qo))
    df = pd.DataFrame(rows, columns=["sym", "tf", "family", "variant", "htf", "bias", "H",
                                     "is_n", "is_sum", "is_sq", "oos_n", "oos_sum", "oos_sq"])
    df.to_parquet(f"../results/edge_{sym}_{tf}_{wave}.parquet")
    return sym, tf, len(df), time.time() - t0


if __name__ == "__main__":
    tfs = sys.argv[1].split(",") if len(sys.argv) > 1 else ["5m"]
    wave = sys.argv[2] if len(sys.argv) > 2 else "w1"
    syms = sys.argv[3].split(",") if len(sys.argv) > 3 else SYMBOLS
    tasks = [(s, t, wave) for t in tfs for s in syms]
    with mp.get_context("spawn").Pool(4) as p:
        for r in p.imap_unordered(run_task, tasks):
            print("DONE", r, flush=True)
