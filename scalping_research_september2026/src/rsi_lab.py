"""Deep dive: RSI pullback in HTF trend with Connors-style exits (close back across SMA(n)).
Per-symbol worker tasks, pooled sufficient stats (see stage3_batch)."""
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import numpy as np
import pandas as pd

from data import SYMBOLS
from stage3_batch import _suff, pool_stats, bar_months, IS_MONTHS, OOS_MONTHS

HTFS = ["1h", "2h", "4h", "12h"]
KINDS = ["ema50", "ema200", "macd", "rsi", "st"]
LENS = [2, 3, 4]
LOS = [5, 10, 15, 20, 25, 30]
STYLES = ["level", "hook"]
EXITS = [dict(sma=n, sl_atr=k, max_bars=mb) for n, k, mb in itertools.product([5, 10, 20], [2.0, 3.0, 4.0, 6.0], [48, 96, 288])]


def sym_task(args):
    sym, tf = args
    from engine import simulate, FEE, SLIP
    from lab import ctx
    from data import IS_END, OOS_END
    import features as fx
    import ind
    from features import cross_up, cross_dn
    cx = ctx(sym, tf)
    idx = cx.df.index.values
    cut = np.searchsorted(idx, IS_END.to_datetime64())
    cut_oos = np.searchsorted(idx, OOS_END.to_datetime64())
    smas = {n: ind.sma(cx.c, n) for n in (5, 10, 20)}
    bm = bar_months(cx)
    trends = [("none", "none", None), ("ltf", "ema200", np.where(cx.c > fx.ema(cx, 200), 1, -1))]
    trends += [(h, k, fx.htf_bias(cx, h, k).astype(np.int64)) for h in HTFS for k in KINDS]
    out = []
    for ln, lo, style in itertools.product(LENS, LOS, STYLES):
        r = fx.rsi(cx, ln)
        if style == "level":
            L, S = r < lo, r > 100 - lo
        else:
            L, S = cross_up(r, lo), cross_dn(r, 100 - lo)
        base = np.zeros(cx.c.size, np.int64)
        base[L] = 1
        base[S] = -1
        base[cut_oos:] = 0
        for htf, kind, b in trends:
            s = base if b is None else np.where(b == base, base, 0)
            if np.count_nonzero(s[:cut]) < 100:
                continue
            for ex in EXITS:
                tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, ex["sl_atr"] * cx.atr, cx.atr,
                              smas[ex["sma"]], 0.0, 0.0, 4, 0.0, ex["max_bars"], False, 0.0, 0.0, FEE, SLIP)
                eb = tr[:, 0].astype(int) + 1
                isb = eb < cut
                rr, d, mo = tr[:, 6], tr[:, 2], bm[eb]
                key = (ln, lo, style, htf, kind, ex["sma"], ex["sl_atr"], ex["max_bars"])
                out.append((key, _suff(rr[isb], d[isb], mo[isb]), _suff(rr[~isb], d[~isb], mo[~isb])))
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
    rows = []
    names = ["rsi_len", "lo", "style", "htf", "bias", "sma", "sl_atr", "max_bars"]
    for key, (a, b) in acc.items():
        pi, po = pool_stats(a, IS_MONTHS), pool_stats(b, OOS_MONTHS)
        rows.append({**dict(zip(names, key)), "n_sym": len(a),
                     **{f"is_{k}": v for k, v in pi.items()}, **{f"oos_{k}": v for k, v in po.items()}})
    res = pd.DataFrame(rows)
    res.to_parquet(f"../results/rsi_lab_{tf}.parquet")
    print("saved", len(res), flush=True)
