"""Cached features for a context + HTF bias library. Everything is computed on closed bars
only and is reproducible in Pine Script."""
import numpy as np
import pandas as pd

import ind
from data import bars, htf_to_ltf, TF_MIN


def F(cx, name, fn):
    if name not in cx.cache:
        cx.cache[name] = fn()
    return cx.cache[name]


def ema(cx, n):
    return F(cx, f"ema{n}", lambda: ind.ema(cx.c, n))


def rsi(cx, n):
    return F(cx, f"rsi{n}", lambda: ind.rsi(cx.c, n))


def atr(cx, n=14):
    return cx.atr if n == 14 else F(cx, f"atr{n}", lambda: ind.atr(cx.h, cx.l, cx.c, n))


def vol_sma(cx, n=20):
    return F(cx, f"vsma{n}", lambda: ind.sma(cx.v, n))


def bb(cx, n=20, k=2.0):
    return F(cx, f"bb{n}_{k}", lambda: ind.bollinger(cx.c, n, k))


def kc(cx, n=20, k=1.5):
    return F(cx, f"kc{n}_{k}", lambda: ind.keltner(cx.h, cx.l, cx.c, n, k))


def stoch(cx, n=14):
    return F(cx, f"stoch{n}", lambda: ind.stoch(cx.c, cx.h, cx.l, n, 3, 3))


def macd(cx):
    return F(cx, "macd", lambda: ind.macd(cx.c))


def st(cx, n=10, m=3.0):
    return F(cx, f"st{n}_{m}", lambda: ind.supertrend(cx.h, cx.l, cx.c, ind.atr(cx.h, cx.l, cx.c, n), m))


def piv(cx, left, right):
    return F(cx, f"piv{left}_{right}", lambda: ind.pivots(cx.h, cx.l, left, right))


def day_id(cx):
    return F(cx, "day", lambda: (cx.df.index.values.astype("datetime64[D]").astype(np.int64)))


def vwap(cx):
    return F(cx, "vwap", lambda: ind.session_vwap(cx.h, cx.l, cx.c, cx.v, day_id(cx)))


def minute_of_day(cx):
    return F(cx, "mod", lambda: (cx.df.index.hour * 60 + cx.df.index.minute).values)


def local_minute(cx, tz):
    def f():
        t = cx.df.index.tz_convert(tz)
        return (t.hour * 60 + t.minute).values, t.tz_localize(None).values.astype("datetime64[D]").astype(np.int64)
    return F(cx, f"lm_{tz}", f)


def prev_day_hl(cx):
    """Previous UTC day's high/low/close, known from 00:00 UTC."""
    def f():
        d = cx.df.resample("1D").agg({"high": "max", "low": "min", "close": "last", "open": "first"})
        d = d.shift(1)
        idx = cx.df.index.floor("1D")
        return (d.high.reindex(idx).values, d.low.reindex(idx).values, d.close.reindex(idx).values)
    return F(cx, "pdhl", f)


def cross_up(a, b):
    a = np.asarray(a); b = np.asarray(b) if np.ndim(b) else np.full(a.shape, b)
    out = np.zeros(a.size, bool)
    out[1:] = (a[1:] > b[1:]) & (a[:-1] <= b[:-1])
    return out


def cross_dn(a, b):
    a = np.asarray(a); b = np.asarray(b) if np.ndim(b) else np.full(a.shape, b)
    out = np.zeros(a.size, bool)
    out[1:] = (a[1:] < b[1:]) & (a[:-1] >= b[:-1])
    return out


def shift(x, k=1, fill=np.nan):
    x = np.asarray(x, dtype=np.float64)
    out = np.full_like(x, fill)
    if k == 0:
        return x.copy()
    if k > 0:
        out[k:] = x[:-k]
    else:
        out[:k] = x[-k:]
    return out


# ------------------------------------------------------------------ HTF bias
BIAS_TYPES = ["ema20", "ema50", "ema200", "slope20", "slope50", "stack", "st", "macd", "rsi", "donch", "struct", "ha"]


def _bias_on(df, kind):
    o, h, l, c = (df[k].values.astype(np.float64) for k in ("open", "high", "low", "close"))
    if kind in ("ema20", "ema50", "ema200"):
        e = ind.ema(c, int(kind[3:]))
        return np.where(np.isnan(e), 0, np.where(c > e, 1, -1))
    if kind in ("slope20", "slope50"):
        e = ind.ema(c, int(kind[5:]))
        d = np.diff(e, prepend=np.nan)
        return np.where(np.isnan(d), 0, np.sign(d))
    if kind == "stack":
        a, b = ind.ema(c, 20), ind.ema(c, 50)
        return np.where((c > a) & (a > b), 1, np.where((c < a) & (a < b), -1, 0))
    if kind == "st":
        _, d = ind.supertrend(h, l, c, ind.atr(h, l, c, 10), 3.0)
        return -d  # TV: -1 = up
    if kind == "macd":
        m, s, _ = ind.macd(c)
        return np.where(np.isnan(s), 0, np.where(m > s, 1, -1))
    if kind == "rsi":
        r = ind.rsi(c, 14)
        return np.where(r > 50, 1, -1)
    if kind == "donch":
        hh, ll = ind.rolling_max(h, 20), ind.rolling_min(l, 20)
        mid = (hh + ll) / 2
        return np.where(np.isnan(mid), 0, np.where(c > mid, 1, -1))
    if kind == "struct":
        # higher-high & higher-low vs previous confirmed pivots (3,3)
        ph, pl, _, _ = ind.pivots(h, l, 3, 3)
        lph = pd.Series(ph).ffill().values
        pph = pd.Series(np.where(np.isnan(ph), np.nan, shift_valid(ph))).ffill().values
        lpl = pd.Series(pl).ffill().values
        ppl = pd.Series(np.where(np.isnan(pl), np.nan, shift_valid(pl))).ffill().values
        up = (lph > pph) & (lpl > ppl)
        dn = (lph < pph) & (lpl < ppl)
        return np.where(up, 1, np.where(dn, -1, 0))
    if kind == "ha":
        ho, _, _, hc = ind.heikin_ashi(o, h, l, c)
        return np.where(hc > ho, 1, -1)
    raise ValueError(kind)


def shift_valid(x):
    """For each non-nan element, the previous non-nan value."""
    out = np.full_like(x, np.nan)
    prev = np.nan
    for i in range(x.size):
        if not np.isnan(x[i]):
            out[i] = prev
            prev = x[i]
    return out


def htf_bias(cx, htf, kind):
    def f():
        df = bars(cx.sym, htf)
        b = pd.DataFrame({"b": _bias_on(df, kind).astype(np.float64)}, index=df.index)
        return np.nan_to_num(htf_to_ltf(b, htf, cx.df.index, cx.tf).b.values).astype(np.int64)
    return F(cx, f"bias_{htf}_{kind}", f)
