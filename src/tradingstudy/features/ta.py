"""TradingView Pine-equivalent indicator primitives. All are causal: value at index i uses inputs [0..i] only.

Conventions copied from Pine v5/v6 built-ins:
- ta.sma: NaN until `length` valid values; NaN if any value in the window is NaN.
- ta.ema: seeded with the SMA of the first `length` valid values, then alpha = 2 / (length + 1).
- ta.rma: same seeding, alpha = 1 / length (Wilder).
- ta.stdev: population standard deviation (biased=true), NaN until `length` values.
- ta.atr: rma of true range; the first bar's true range is high - low.
"""
from __future__ import annotations

import numba as nb
import numpy as np


@nb.njit(cache=True)
def _ema_seeded(x: np.ndarray, length: int, alpha: float) -> np.ndarray:
    n = x.shape[0]
    out = np.full(n, np.nan)
    s = 0.0
    cnt = 0
    prev = np.nan
    for i in range(n):
        v = x[i]
        if np.isnan(prev):
            if np.isnan(v):
                s = 0.0
                cnt = 0
                continue
            s += v
            cnt += 1
            if cnt == length:
                prev = s / length
                out[i] = prev
        else:
            if np.isnan(v):
                out[i] = prev  # Pine's nz() style hold on a missing input
                continue
            prev = alpha * v + (1.0 - alpha) * prev
            out[i] = prev
    return out


def ema(x, length: int) -> np.ndarray:
    return _ema_seeded(np.asarray(x, dtype=np.float64), length, 2.0 / (length + 1.0))


def rma(x, length: int) -> np.ndarray:
    return _ema_seeded(np.asarray(x, dtype=np.float64), length, 1.0 / length)


@nb.njit(cache=True)
def _sma(x: np.ndarray, length: int) -> np.ndarray:
    n = x.shape[0]
    out = np.full(n, np.nan)
    s = 0.0
    nan_in_win = 0
    for i in range(n):
        v = x[i]
        if np.isnan(v):
            nan_in_win += 1
        else:
            s += v
        if i >= length:
            old = x[i - length]
            if np.isnan(old):
                nan_in_win -= 1
            else:
                s -= old
        if i >= length - 1 and nan_in_win == 0:
            out[i] = s / length
    return out


def sma(x, length: int) -> np.ndarray:
    return _sma(np.asarray(x, dtype=np.float64), length)


@nb.njit(cache=True)
def _stdev(x: np.ndarray, length: int) -> np.ndarray:
    n = x.shape[0]
    out = np.full(n, np.nan)
    for i in range(length - 1, n):
        w = x[i - length + 1: i + 1]
        if np.isnan(w).any():
            continue
        m = w.mean()
        out[i] = np.sqrt(((w - m) ** 2).mean())
    return out


def stdev(x, length: int) -> np.ndarray:
    return _stdev(np.asarray(x, dtype=np.float64), length)


def true_range(high, low, close) -> np.ndarray:
    high, low, close = (np.asarray(a, dtype=np.float64) for a in (high, low, close))
    pc = np.r_[np.nan, close[:-1]]
    tr = np.fmax(high - low, np.fmax(np.abs(high - pc), np.abs(low - pc)))
    tr[0] = high[0] - low[0]
    return tr


def atr(high, low, close, length: int = 14) -> np.ndarray:
    return rma(true_range(high, low, close), length)


def safe_div(a, b) -> np.ndarray:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    out = np.full(a.shape, np.nan)
    ok = (b != 0) & ~np.isnan(b)
    out[ok] = a[ok] / b[ok]
    return out
