"""Indicators implemented to match TradingView's ta.* definitions, so every one
can be reproduced 1:1 in Pine Script."""
import numpy as np
from numba import njit


@njit(cache=True)
def ema(x, n):
    # ta.ema: alpha = 2/(n+1), seeded with SMA of first n values
    out = np.full(x.size, np.nan)
    a = 2.0 / (n + 1)
    s = 0.0
    cnt = 0
    started = False
    for i in range(x.size):
        v = x[i]
        if np.isnan(v):
            continue
        if not started:
            s += v
            cnt += 1
            if cnt == n:
                out[i] = s / n
                started = True
        else:
            prev = out[i - 1] if not np.isnan(out[i - 1]) else v
            out[i] = a * v + (1 - a) * prev
    return out


@njit(cache=True)
def rma(x, n):
    # ta.rma: alpha = 1/n, seeded with SMA
    out = np.full(x.size, np.nan)
    a = 1.0 / n
    s = 0.0
    cnt = 0
    started = False
    for i in range(x.size):
        v = x[i]
        if np.isnan(v):
            continue
        if not started:
            s += v
            cnt += 1
            if cnt == n:
                out[i] = s / n
                started = True
        else:
            out[i] = a * v + (1 - a) * out[i - 1]
    return out


@njit(cache=True)
def sma(x, n):
    out = np.full(x.size, np.nan)
    s = 0.0
    for i in range(x.size):
        s += x[i]
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


@njit(cache=True)
def rolling_std(x, n):
    # ta.stdev (population std, biased)
    out = np.full(x.size, np.nan)
    for i in range(n - 1, x.size):
        w = x[i - n + 1:i + 1]
        m = w.mean()
        out[i] = np.sqrt(((w - m) ** 2).mean())
    return out


@njit(cache=True)
def rolling_max(x, n):
    out = np.full(x.size, np.nan)
    for i in range(n - 1, x.size):
        out[i] = x[i - n + 1:i + 1].max()
    return out


@njit(cache=True)
def rolling_min(x, n):
    out = np.full(x.size, np.nan)
    for i in range(n - 1, x.size):
        out[i] = x[i - n + 1:i + 1].min()
    return out


def true_range(h, l, c):
    pc = np.roll(c, 1)
    pc[0] = c[0]
    return np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))


def atr(h, l, c, n=14):
    return rma(true_range(h, l, c), n)


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    up = rma(np.maximum(d, 0.0), n)
    dn = rma(np.maximum(-d, 0.0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + up / dn)
    r = np.where(dn == 0, 100.0, r)
    return r


def stoch(c, h, l, n=14, k_smooth=3, d_smooth=3):
    hh = rolling_max(h, n)
    ll = rolling_min(l, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        k_raw = 100 * (c - ll) / (hh - ll)
    k = sma(np.nan_to_num(k_raw, nan=50.0), k_smooth)
    d = sma(np.nan_to_num(k, nan=50.0), d_smooth)
    return k, d


def macd(c, fast=12, slow=26, sig=9):
    m = ema(c, fast) - ema(c, slow)
    s = ema(m, sig)
    return m, s, m - s


def bollinger(c, n=20, k=2.0):
    mid = sma(c, n)
    sd = rolling_std(c, n)
    return mid, mid + k * sd, mid - k * sd


def keltner(h, l, c, n=20, k=1.5, atr_n=10):
    mid = ema(c, n)
    a = atr(h, l, c, atr_n)
    return mid, mid + k * a, mid - k * a


def cci(h, l, c, n=20):
    tp = (h + l + c) / 3
    m = sma(tp, n)
    md = np.full(tp.size, np.nan)
    for i in range(n - 1, tp.size):
        w = tp[i - n + 1:i + 1]
        md[i] = np.abs(w - m[i]).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        return (tp - m) / (0.015 * md)


def mfi(h, l, c, v, n=14):
    tp = (h + l + c) / 3
    d = np.diff(tp, prepend=tp[0])
    pos = np.where(d > 0, tp * v, 0.0)
    neg = np.where(d < 0, tp * v, 0.0)
    ps = sma(pos, n)
    ns = sma(neg, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + ps / ns)
    return np.where(ns == 0, 100.0, r)


@njit(cache=True)
def supertrend(h, l, c, atr_v, mult):
    # matches ta.supertrend: returns (line, direction) with direction -1 = uptrend (TV convention)
    n = c.size
    up = np.full(n, np.nan)
    dn = np.full(n, np.nan)
    st = np.full(n, np.nan)
    d = np.ones(n)
    for i in range(n):
        if np.isnan(atr_v[i]):
            continue
        src = (h[i] + l[i]) / 2
        u = src + mult * atr_v[i]
        lo = src - mult * atr_v[i]
        if i > 0 and not np.isnan(dn[i - 1]):
            lo = lo if (lo > dn[i - 1] or c[i - 1] < dn[i - 1]) else dn[i - 1]
            u = u if (u < up[i - 1] or c[i - 1] > up[i - 1]) else up[i - 1]
        up[i] = u
        dn[i] = lo
        if i == 0 or np.isnan(st[i - 1]):
            d[i] = 1
        elif st[i - 1] == up[i - 1]:
            d[i] = -1 if c[i] > u else 1
        else:
            d[i] = 1 if c[i] < lo else -1
        st[i] = lo if d[i] == -1 else u
    return st, d


def adx(h, l, c, n=14):
    up = np.diff(h, prepend=h[0])
    dn = -np.diff(l, prepend=l[0])
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = rma(true_range(h, l, c), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = 100 * rma(pdm, n) / tr
        ndi = 100 * rma(ndm, n) / tr
        dx = 100 * np.abs(pdi - ndi) / (pdi + ndi)
    return pdi, ndi, rma(np.nan_to_num(dx), n)


def heikin_ashi(o, h, l, c):
    hc = (o + h + l + c) / 4
    ho = np.empty_like(o)
    ho[0] = (o[0] + c[0]) / 2
    for i in range(1, o.size):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(l, np.minimum(ho, hc))
    return ho, hh, hl, hc


@njit(cache=True)
def pivots(h, l, left, right):
    """ta.pivothigh / ta.pivotlow. Value is placed at the bar where it becomes
    KNOWN (i.e. `right` bars after the pivot), exactly like Pine. Also returns
    the index of the pivot bar itself."""
    n = h.size
    ph = np.full(n, np.nan)
    pl = np.full(n, np.nan)
    ph_idx = np.full(n, -1)
    pl_idx = np.full(n, -1)
    for i in range(left + right, n):
        p = i - right
        v = h[p]
        ok = True
        for j in range(p - left, p + right + 1):
            if j != p and h[j] >= v:
                if j < p and h[j] > v:
                    ok = False
                    break
                if j > p and h[j] >= v:
                    ok = False
                    break
        if ok:
            ph[i] = v
            ph_idx[i] = p
        v = l[p]
        ok = True
        for j in range(p - left, p + right + 1):
            if j != p:
                if j < p and l[j] < v:
                    ok = False
                    break
                if j > p and l[j] <= v:
                    ok = False
                    break
        if ok:
            pl[i] = v
            pl_idx[i] = p
    return ph, pl, ph_idx, pl_idx


def session_vwap(h, l, c, v, day_id):
    """VWAP anchored to UTC day (ta.vwap with 'Session' anchor on 24/7 crypto)."""
    tp = (h + l + c) / 3
    pv = tp * v
    out = np.empty_like(c)
    sd = np.empty_like(c)
    cum_pv = cum_v = cum_pv2 = 0.0
    prev = -1
    for i in range(c.size):
        if day_id[i] != prev:
            cum_pv = cum_v = cum_pv2 = 0.0
            prev = day_id[i]
        cum_pv += pv[i]
        cum_v += v[i]
        cum_pv2 += v[i] * tp[i] ** 2
        out[i] = cum_pv / cum_v if cum_v > 0 else tp[i]
        var = cum_pv2 / cum_v - out[i] ** 2 if cum_v > 0 else 0.0
        sd[i] = np.sqrt(max(var, 0.0))
    return out, sd


def zscore(x, n):
    m = sma(x, n)
    s = rolling_std(x, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (x - m) / s
