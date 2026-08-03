"""Indicators, computed from scratch. Nothing is read from the TradingView export columns.

Every function returns a series aligned to the input index where the value at position i uses
only bars 0..i. No centring, no forward fill from the future.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, period: int) -> pd.Series:
    return s.ewm(span=period, adjust=False, min_periods=period).mean()


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return line, sig


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder (RMA) smoothing, the TradingView default."""
    return true_range(df).ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def donchian(df: pd.DataFrame, period: int, exclude_current: bool = True):
    """Channel high/low. exclude_current shifts the window back one bar (spec S2, invented 1)."""
    h, l = df["high"], df["low"]
    if exclude_current:
        h, l = h.shift(1), l.shift(1)
    return h.rolling(period).max(), l.rolling(period).min()


def mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    raw = tp * df["volume"]
    up = raw.where(tp > tp.shift(1), 0.0)
    dn = raw.where(tp < tp.shift(1), 0.0)
    pos = up.rolling(period).sum()
    neg = dn.rolling(period).sum()
    # neg == 0 means no negative flow in the window, i.e. a saturated 100 reading
    out = 100.0 - (100.0 / (1.0 + pos / neg.replace(0.0, np.nan)))
    return out.where(neg != 0, 100.0).where(pos.notna())


def crossed_above(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a > b) & (a.shift(1) <= b.shift(1))


def crossed_below(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a < b) & (a.shift(1) >= b.shift(1))


def monotonic_run(s: pd.Series, n: int, up: bool) -> pd.Series:
    """True where s has moved strictly one way on each of the last n bars.

    Spec S4, invented 1: the operational reading of "sloping cleanly, not flat or tangled".
    """
    d = s.diff()
    step = (d > 0) if up else (d < 0)
    return step.rolling(n).sum() == n


def fractal_pivots(df: pd.DataFrame, left: int = 2, right: int = 2):
    """5-bar fractal pivots. A pivot at bar p is only CONFIRMED at bar p+right.

    Returns (swing_low, swing_high) series carrying the most recent *confirmed* pivot price
    as of each bar, so a backtest reading them at bar t never sees an unconfirmed future pivot.
    Spec S4, invented 2.
    """
    h, l = df["high"].values, df["low"].values
    n = len(df)
    lo = np.full(n, np.nan)
    hi = np.full(n, np.nan)
    for p in range(left, n - right):
        w_l = l[p - left:p + right + 1]
        w_h = h[p - left:p + right + 1]
        if l[p] == w_l.min() and (w_l == l[p]).sum() == 1:
            lo[p + right] = l[p]        # published only once confirmed
        if h[p] == w_h.max() and (w_h == h[p]).sum() == 1:
            hi[p + right] = h[p]
    return (pd.Series(lo, index=df.index).ffill(),
            pd.Series(hi, index=df.index).ffill())
