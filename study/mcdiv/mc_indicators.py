"""
Python port of the "MCB Clone v1" PineScript indicator formulas
(WaveTrend, MFI-clone, ATR14) used by the divergence study.

All functions take a DataFrame with columns open, high, low, close and
return pandas Series aligned to df.index.
"""
import numpy as np
import pandas as pd


def wavetrend(df):
    """
    WaveTrend (channel length 9, average length 12, MA length 3).

    src = hlc3
    esa = EMA(src, 9)
    de  = EMA(abs(src - esa), 9)
    ci  = (src - esa) / (0.015 * de)
    wt1 = EMA(ci, 12)
    wt2 = SMA(wt1, 3)

    EMA uses pandas .ewm(span=n, adjust=False) per spec.
    Returns (wt1, wt2).
    """
    src = (df["high"] + df["low"] + df["close"]) / 3.0
    esa = src.ewm(span=9, adjust=False).mean()
    de = (src - esa).abs().ewm(span=9, adjust=False).mean()
    ci = (src - esa) / (0.015 * de)
    wt1 = ci.ewm(span=12, adjust=False).mean()
    wt2 = wt1.rolling(3).mean()
    return wt1, wt2


def mfi_clone(df, ddof=0):
    """
    MFI-clone oscillator:
      EMA( SMA( (close - open) / stdev(close, 7) * 150, 60 ) - 2.5, 4 )

    stdev = rolling std over 7 bars. ddof selects the rolling-std divisor
    convention:
      ddof=0 -> population std (PineScript's ta.stdev semantics)
      ddof=1 -> sample std (pandas default)

    Validation (see validate_port.py / VALIDATION.md) found ddof=0
    (population stdev, matching PineScript's ta.stdev) reproduces the
    TradingView export with a far lower error than ddof=1. This is the
    shipped default.
    """
    stdev = df["close"].rolling(7).std(ddof=ddof)
    raw = (df["close"] - df["open"]) / stdev * 150.0
    sma = raw.rolling(60).mean()
    mfi = (sma - 2.5).ewm(span=4, adjust=False).mean()
    return mfi


def atr14(df):
    """
    ATR14, Wilder RMA smoothing.
      tr  = max(h-l, abs(h-prev_close), abs(l-prev_close))
      atr = tr.ewm(alpha=1/14, adjust=False).mean()
    """
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / 14.0, adjust=False).mean()
    return atr
