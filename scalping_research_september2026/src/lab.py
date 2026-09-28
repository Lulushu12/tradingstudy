"""Research harness: build per-symbol context, run a signal through the engine, score it."""
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import pandas as pd

from data import bars, load_1m, minute_map, IS_END, OOS_END, TF_MIN
from engine import simulate, FEE, SLIP
import ind


@dataclass
class Ctx:
    sym: str
    tf: str
    df: pd.DataFrame
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    v: np.ndarray
    h1: np.ndarray
    l1: np.ndarray
    mm: np.ndarray
    atr: np.ndarray
    cache: dict = field(default_factory=dict)


@lru_cache(maxsize=32)
def ctx(sym, tf="5m"):
    df = bars(sym, tf)
    m = load_1m(sym)
    o, h, l, c, v = (df[k].values.astype(np.float64) for k in ("open", "high", "low", "close", "volume"))
    return Ctx(sym, tf, df, o, h, l, c, v, m.high.values, m.low.values, minute_map(sym, tf),
               ind.atr(h, l, c, 14))


@dataclass
class Exit:
    sl_atr: float = 1.5          # stop distance in ATR (used when no explicit sl array given)
    tp_r: float = 2.0            # target in R (0 = none)
    be_r: float = 0.0            # move to breakeven after +be_r R (0 = off)
    trail: int = 0               # 0 none, 1 ATR chandelier, 2 prev-bar, 3 close through trail_src
    trail_mult: float = 0.0
    max_bars: int = 0            # time stop (0 = off)
    exit_opp: bool = False
    partial_r: float = 0.0
    partial_frac: float = 0.0

    def key(self):
        return (self.sl_atr, self.tp_r, self.be_r, self.trail, self.trail_mult, self.max_bars,
                self.exit_opp, self.partial_r, self.partial_frac)


def run(cx, sig, ex, sl_dist=None, trail_src=None, fee=FEE, slip=SLIP, min_sl_pct=0.0):
    sig = np.asarray(sig, dtype=np.int64)
    if sl_dist is None:
        sl_dist = ex.sl_atr * cx.atr
    sl_dist = np.asarray(sl_dist, dtype=np.float64)
    if min_sl_pct > 0:
        sl_dist = np.maximum(sl_dist, min_sl_pct * cx.c)
    if trail_src is None:
        trail_src = cx.c
    tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, sig, sl_dist, cx.atr,
                  np.asarray(trail_src, dtype=np.float64),
                  ex.tp_r, ex.be_r, ex.trail, ex.trail_mult, ex.max_bars, ex.exit_opp,
                  ex.partial_r, ex.partial_frac, fee, slip)
    t = pd.DataFrame(tr, columns=["ebar", "xbar", "dir", "entry", "exit", "sl_pct", "r", "reason"])
    t["time"] = cx.df.index.values[t.ebar.astype(int) + 1]
    t["xtime"] = cx.df.index.values[t.xbar.astype(int)] + np.timedelta64(TF_MIN[cx.tf], "m")
    t["sym"] = cx.sym
    return t


def split(t):
    tt = pd.to_datetime(t.time, utc=True)
    return t[tt < IS_END], t[(tt >= IS_END) & (tt < OOS_END)], t[tt >= OOS_END]


def stats(t, months=None):
    if len(t) == 0:
        return dict(n=0, wr=np.nan, avg_r=np.nan, pf=np.nan, sum_r=0.0, tpm=0.0, sl_pct=np.nan)
    r = t.r.values
    if months is None:
        tt = pd.to_datetime(t.time, utc=True)
        months = max((tt.max() - tt.min()).days / 30.44, 1)
    gp = r[r > 0].sum()
    gl = -r[r < 0].sum()
    return dict(n=len(r), wr=(r > 0).mean(), avg_r=r.mean(), pf=gp / gl if gl > 0 else np.inf,
                sum_r=r.sum(), tpm=len(r) / months, sl_pct=np.median(t.sl_pct.values) * 100)


IS_MONTHS = 48.0
OOS_MONTHS = 21.0


def period_stats(t):
    a, b, _ = split(t)
    s1 = stats(a, IS_MONTHS)
    s2 = stats(b, OOS_MONTHS)
    return {**{f"is_{k}": v for k, v in s1.items()}, **{f"oos_{k}": v for k, v in s2.items()}}
