"""Time-series momentum with scheduled entries: at fixed UTC hours, take the HTF trend direction,
hold with an ATR stop and a time exit. Long and short. Scored on TRUE monthly Sharpe."""
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import numpy as np
import pandas as pd

from data import SYMBOLS
from stage3_batch import _suff, pool_stats, bar_months, IS_MONTHS, OOS_MONTHS

HOURSETS = {"h00": [0], "h21": [21], "h08x3": [0, 8, 16], "h04x6": [0, 4, 8, 12, 16, 20]}
HTFS = ["1h", "2h", "4h", "12h", "1d"]
KINDS = ["ema20", "ema50", "ema200", "slope20", "macd", "st", "donch"]
HOLD_H = [8, 16, 24, 48]
SLS = [2.0, 3.0, 4.0, 6.0]
TPS = [0.0, 3.0]


def sym_task(args):
    sym, tf = args
    from engine import simulate, FEE, SLIP
    from lab import ctx
    from data import IS_END, OOS_END, TF_MIN
    import features as fx
    cx = ctx(sym, tf)
    idx = cx.df.index
    cut = np.searchsorted(idx.values, IS_END.to_datetime64())
    cut_oos = np.searchsorted(idx.values, OOS_END.to_datetime64())
    bm = bar_months(cx)
    per_h = 60 // TF_MIN[tf]
    # signal on the close of the bar that ENDS at hh:00 -> entry at the hh:00 bar open
    close_min = (idx + pd.Timedelta(minutes=TF_MIN[tf])).hour * 60 + (idx + pd.Timedelta(minutes=TF_MIN[tf])).minute
    close_hour = ((idx + pd.Timedelta(minutes=TF_MIN[tf])).hour).values
    on_hour = (np.asarray(close_min) % 60 == 0)
    out = []
    for hs_name, hs in HOURSETS.items():
        when = on_hour & np.isin(close_hour, hs)
        for htf, kind in itertools.product(HTFS, KINDS):
            b = fx.htf_bias(cx, htf, kind).astype(np.int64)
            s = np.where(when, b, 0)
            s[cut_oos:] = 0
            for hh, sl, tp in itertools.product(HOLD_H, SLS, TPS):
                tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sl * cx.atr, cx.atr, cx.c,
                              tp, 0.0, 0, 0.0, hh * per_h, False, 0.0, 0.0, FEE, SLIP)
                eb = tr[:, 0].astype(int) + 1
                isb = eb < cut
                rr, d, mo = tr[:, 6], tr[:, 2], bm[eb]
                out.append(((hs_name, htf, kind, hh, sl, tp), _suff(rr[isb], d[isb], mo[isb]),
                            _suff(rr[~isb], d[~isb], mo[~isb])))
    print("symbol done", sym, tf, len(out), flush=True)
    return out


if __name__ == "__main__":
    tf = sys.argv[1]
    acc = {}
    with ProcessPoolExecutor(2, mp_context=mp.get_context("spawn")) as ex:
        for out in ex.map(sym_task, [(s, tf) for s in SYMBOLS]):
            for key, a, b in out:
                acc.setdefault(key, ([], []))
                acc[key][0].append(a)
                acc[key][1].append(b)
    names = ["hours", "htf", "bias", "hold_h", "sl_atr", "tp_r"]
    rows = [{**dict(zip(names, k)), **{f"is_{x}": v for x, v in pool_stats(a, IS_MONTHS).items()},
             **{f"oos_{x}": v for x, v in pool_stats(b, OOS_MONTHS).items()}} for k, (a, b) in acc.items()]
    pd.DataFrame(rows).to_parquet(f"../results/tsmom_lab_{tf}.parquet")
    print("saved", len(rows), flush=True)
