"""Parameter-neighbourhood test for the Asia opening-range fade (plateau vs spike).
Signal: range = first `or_min` minutes after 00:00 UTC. Within `win_h` hours after the range completes,
a bar that closes back inside after the previous bar closed outside -> fade entry (first per day).
Trend filter: HTF bias must agree with trade direction."""
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import numpy as np
import pandas as pd

from data import SYMBOLS
from stage3_batch import _suff, pool_stats, bar_months, IS_MONTHS, OOS_MONTHS

OR_MIN = [30, 45, 60, 75, 90, 120]
WIN_H = [2, 4, 6]
TRENDS = [(h, k) for h in ("4h", "12h", "1d") for k in ("ema50", "ema200", "st")] + [("none", "none")]
SLS = [3.0, 4.0, 5.0]
BES = [0.0, 0.75, 1.0, 1.5]
HOLD_H = [24, 48, 72]


def asia_fade_signal(cx, or_min, win_h, include_holdout=False):
    from features import shift, local_minute
    from signals import _first_per_group, _sig
    from data import OOS_END, TF_MIN
    lm, lday = local_minute(cx, "UTC")
    tfm = TF_MIN[cx.tf]
    in_or = lm < or_min
    after = (lm >= or_min) & (lm < or_min + win_h * 60)
    df = pd.DataFrame({"h": np.where(in_or, cx.h, np.nan), "l": np.where(in_or, cx.l, np.nan), "d": lday})
    orh = df.groupby("d").h.transform("max").values
    orl = df.groupby("d").l.transform("min").values
    L = after & (shift(cx.c, 1) < orl) & (cx.c > orl)
    S = after & (shift(cx.c, 1) > orh) & (cx.c < orh)
    first = _first_per_group(L | S, lday)
    s = _sig(L & first, S & first)
    if not include_holdout:
        s[np.searchsorted(cx.df.index.values, OOS_END.to_datetime64()):] = 0
    return s


def sym_task(args):
    sym, tf = args
    from engine import simulate, FEE, SLIP
    from lab import ctx
    from data import IS_END, TF_MIN
    import features as fx
    cx = ctx(sym, tf)
    cut = np.searchsorted(cx.df.index.values, IS_END.to_datetime64())
    bm = bar_months(cx)
    per_h = 60 // TF_MIN[tf]
    out = []
    for om, wh in itertools.product(OR_MIN, WIN_H):
        base = asia_fade_signal(cx, om, wh)
        for htf, kind in TRENDS:
            s = base if htf == "none" else np.where(fx.htf_bias(cx, htf, kind).astype(np.int64) == base, base, 0)
            for sl, be, hh in itertools.product(SLS, BES, HOLD_H):
                tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sl * cx.atr, cx.atr, cx.c,
                              0.0, be, 0, 0.0, hh * per_h, False, 0.0, 0.0, FEE, SLIP)
                eb = tr[:, 0].astype(int) + 1
                isb = eb < cut
                rr, d, mo = tr[:, 6], tr[:, 2], bm[eb]
                out.append(((om, wh, htf, kind, sl, be, hh), _suff(rr[isb], d[isb], mo[isb]),
                            _suff(rr[~isb], d[~isb], mo[~isb])))
    print("symbol done", sym, tf, flush=True)
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
    names = ["or_min", "win_h", "htf", "bias", "sl_atr", "be_r", "hold_h"]
    rows = [{**dict(zip(names, k)), **{f"is_{x}": v for x, v in pool_stats(a, IS_MONTHS).items()},
             **{f"oos_{x}": v for x, v in pool_stats(b, OOS_MONTHS).items()}} for k, (a, b) in acc.items()]
    pd.DataFrame(rows).to_parquet(f"../results/asia_lab_{tf}.parquet")
    print("saved", len(rows), flush=True)
