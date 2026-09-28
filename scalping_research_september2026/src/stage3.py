"""Stage-3: exit optimisation for a given signal config, IS-selected, OOS-verified."""
import itertools

import numpy as np
import pandas as pd

from data import SYMBOLS, IS_END, OOS_END
from engine import simulate, FEE, SLIP
from lab import ctx
import features as fx
import signals as sg

FAM_BY_NAME = {}


def _fams_for(family):
    # map family name -> generator function (lazy, by probing names in source)
    import inspect
    out = []
    for f in sg.FAMILIES:
        src = inspect.getsource(f)
        if f'"{family}"' in src:
            out.append(f)
    return out


def get_signal(cx, family, variant, htf, bias, include_holdout=False):
    key = ("sig", family, variant, htf, bias)
    if key in cx.cache:
        s, sl = cx.cache[key]
    else:
        s = sl = None
        for f in _fams_for(family):
            for fam, var, sig, sld in f(cx):
                if fam == family and var == variant:
                    s, sl = np.asarray(sig, np.int64), sld
                    break
            if s is not None:
                break
        if s is None:
            raise KeyError((family, variant))
        if htf != "none":
            b = fx.htf_bias(cx, htf, bias)
            s = np.where(b == s, s, 0)
        cx.cache[key] = (s, sl)
    s = s.copy()
    if not include_holdout:
        cut = np.searchsorted(cx.df.index.values, OOS_END.to_datetime64())
        s[cut:] = 0
    return s, sl


EXIT_GRID = dict(sl_atr=[1.0, 1.5, 2.0, 3.0, 4.0], tp_r=[0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 0.0],
                 be_r=[0.0, 1.0], trail=[(0, 0.0), (1, 2.0), (1, 3.0), (2, 1.0)], max_bars=[0, 24, 96, 288])


def exit_grid():
    for sl_atr, tp_r, be_r, (tr, tm), mb in itertools.product(*EXIT_GRID.values()):
        if tp_r == 0 and tr == 0 and mb == 0:
            continue  # no way out except stop
        yield dict(sl_atr=sl_atr, tp_r=tp_r, be_r=be_r, trail=tr, trail_mult=tm, max_bars=mb)


def eval_exits(family, variant, htf, bias, tf="5m", syms=SYMBOLS, use_struct_sl=True):
    rows = []
    for sym in syms:
        cx = ctx(sym, tf)
        s, sl = get_signal(cx, family, variant, htf, bias)
        eb_cut_is = np.searchsorted(cx.df.index.values, IS_END.to_datetime64())
        for ex in exit_grid():
            sd = (np.maximum(sl, 0.5 * cx.atr) if (sl is not None and use_struct_sl) else ex["sl_atr"] * cx.atr)
            if sl is not None and use_struct_sl and ex["sl_atr"] != 1.0:
                continue  # structural stop: sl_atr irrelevant, evaluate once
            tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sd, cx.atr, cx.c,
                          ex["tp_r"], ex["be_r"], ex["trail"], ex["trail_mult"], ex["max_bars"], False,
                          0.0, 0.0, FEE, SLIP)
            eb = tr[:, 0].astype(int) + 1
            r = tr[:, 6]
            isb = eb < eb_cut_is
            rows.append(dict(sym=sym, **ex, is_n=isb.sum(), is_sum=r[isb].sum(), oos_n=(~isb).sum(),
                             oos_sum=r[~isb].sum()))
    df = pd.DataFrame(rows)
    k = list(EXIT_GRID.keys())
    k = ["sl_atr", "tp_r", "be_r", "trail", "trail_mult", "max_bars"]
    g = df.groupby(k)
    a = g[["is_n", "is_sum", "oos_n", "oos_sum"]].sum()
    a["is_pos"] = g.apply(lambda x: (x.is_sum > 0).sum())
    a["oos_pos"] = g.apply(lambda x: (x.oos_sum > 0).sum())
    a["is_avg"] = a.is_sum / a.is_n
    a["oos_avg"] = a.oos_sum / a.oos_n
    return a.reset_index().sort_values("is_avg", ascending=False)
