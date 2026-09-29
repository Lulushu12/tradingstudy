"""Walk-forward step 1: monthly P&L matrix.

For every config = (signal variant, HTF trend filter, exit) on a given execution timeframe, record the
monthly sum of R and trade count, pooled over all 6 symbols, for every month Jan 2020 .. Sep 2026.
Costs: 0.04%/side fee, 0.02% slippage on market fills, 0.033% swap per position open at 00:00 UTC.
The walk-forward selector (wf_select.py) only ever looks at months BEFORE the quarter it trades.
"""
import itertools
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import numpy as np
import pandas as pd

from data import SYMBOLS

N_MONTHS = 81  # 2020-01 .. 2026-09
BIAS = {"15m": ["1h", "4h", "12h", "1d"], "30m": ["1h", "4h", "12h", "1d"], "1h": ["1h", "4h", "12h", "1d"]}
KINDS = ["ema50", "ema200", "st", "macd", "donch"]
# exits: (sl_atr, tp_r, flat_before_midnight, max_hold_hours)
EXITS = [(sl, tp, flat, hold) for sl in (1.5, 3.0) for tp in (1.5, 3.0, 0.0)
         for flat, hold in ((True, 24), (False, 48))]


def sym_task(args):
    sym, tf = args
    from engine2 import simulate2, SWAP
    from engine import FEE, SLIP
    from lab import ctx
    from data import TF_MIN
    import features as fx
    import signals as sg
    t0 = time.time()
    cx = ctx(sym, tf)
    idx = cx.df.index
    per_h = 60 // TF_MIN[tf]
    day_open = np.asarray(idx.hour * 60 + idx.minute == 0).astype(np.int8)
    ct = idx + pd.Timedelta(minutes=TF_MIN[tf])
    flat_flag = np.asarray(ct.hour * 60 + ct.minute == 0).astype(np.int8)
    bm = ((idx.year - 2020) * 12 + idx.month - 1).values.astype(np.int64)
    biases = [("none", "none", None)] + [(h, k, fx.htf_bias(cx, h, k).astype(np.int64)) for h in BIAS[tf] for k in KINDS]
    keys, mons, cnts = [], [], []
    for fam in sg.FAMILIES:
        try:
            gen = list(fam(cx))
        except Exception as e:
            print("family failed", fam.__name__, sym, tf, e, flush=True)
            continue
        for family, variant, sig, sl in gen:
            sig = np.asarray(sig, np.int64)
            for htf, kind, b in biases:
                s = sig if b is None else np.where(b == sig, sig, 0)
                if np.count_nonzero(s) < 30:
                    continue
                for sl_atr, tp, flat, hold in EXITS:
                    if sl is not None and sl_atr != 1.5:
                        continue  # structural stop variants: run once
                    sd = np.maximum(sl, 0.5 * cx.atr) if sl is not None else sl_atr * cx.atr
                    tr = simulate2(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sd, cx.atr, cx.c,
                                   tp, 0.0, 0, 0.0, hold * per_h, False, 0.0, 0.0, FEE, SLIP,
                                   day_open, flat_flag, flat, SWAP)
                    mo = bm[tr[:, 0].astype(np.int64) + 1]
                    keys.append((family, variant, htf, kind, sl_atr if sl is None else -1.0, tp, flat, hold))
                    mons.append(np.bincount(mo, weights=tr[:, 6], minlength=N_MONTHS)[:N_MONTHS].astype(np.float32))
                    cnts.append(np.bincount(mo, minlength=N_MONTHS)[:N_MONTHS].astype(np.int16))
        print(f"{sym} {tf} {fam.__name__} configs={len(keys)} t={time.time()-t0:.0f}s", flush=True)
    return sym, keys, np.vstack(mons), np.vstack(cnts)


if __name__ == "__main__":
    tf = sys.argv[1]
    total_m = total_c = None
    keys0 = None
    with ProcessPoolExecutor(3, mp_context=mp.get_context("spawn")) as ex:
        for sym, keys, M, C in ex.map(sym_task, [(s, tf) for s in SYMBOLS]):
            # align on keys (some configs may be skipped on some symbols)
            df_m = pd.DataFrame(M, index=pd.MultiIndex.from_tuples(keys))
            df_c = pd.DataFrame(C.astype(np.int32), index=pd.MultiIndex.from_tuples(keys))
            total_m = df_m if total_m is None else total_m.add(df_m, fill_value=0)
            total_c = df_c if total_c is None else total_c.add(df_c, fill_value=0)
            print("merged", sym, tf, total_m.shape, flush=True)
    names = ["family", "variant", "htf", "bias", "sl_atr", "tp_r", "flat", "hold_h"]
    total_m.index.names = names
    total_c.index.names = names
    total_m.columns = [str(c) for c in total_m.columns]
    total_c.columns = [str(c) for c in total_c.columns]
    total_m.astype(np.float32).to_parquet(f"../results/wf_monthly_R_{tf}.parquet")
    total_c.astype(np.int32).to_parquet(f"../results/wf_monthly_n_{tf}.parquet")
    print("saved", tf, total_m.shape, flush=True)
