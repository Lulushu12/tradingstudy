"""Regime classifiers for the categorical-trading Gate 0 study.

Every function is causal: the value at bar t uses only bars <= t. The Gate 0
harness measures forward behaviour starting at t+1, so there is no look-ahead.

The central object is a single bounded statistic that places each bar on the
consolidation <-> direction spectrum described in VIDEO_EXTRACT.md section 1.
"""
import numpy as np
import pandas as pd


def true_range(df):
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    return pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)


def atr(df, n=14):
    """Wilder ATR, matching study/indicators.py."""
    return true_range(df).ewm(alpha=1 / n, adjust=False).mean()


def efficiency_ratio(close, n=20):
    """Kaufman Efficiency Ratio on [0, 1].

    ER = |net displacement over n| / |total path travelled over n|

    0 means every tick of movement was retraced (pure consolidation).
    1 means every tick went the same way (pure direction).
    This is the video's spectrum expressed as one number.
    """
    net = (close - close.shift(n)).abs()
    path = close.diff().abs().rolling(n).sum()
    return net / path.replace(0, np.nan)


def range_efficiency(df, n=20):
    """Range-based sibling of ER: swing span divided by total true range.

    Uses highs and lows rather than closes, so intrabar excursion counts.
    Bounded (0, 1] in practice.
    """
    span = df["high"].rolling(n).max() - df["low"].rolling(n).min()
    path = true_range(df).rolling(n).sum()
    return span / path.replace(0, np.nan)


def variance_ratio(close, q=8, n=200):
    """Rolling Lo-MacKinlay variance ratio using overlapping q-period returns.

    VR < 1  -> mean reverting (variance grows slower than linearly in time)
    VR = 1  -> random walk
    VR > 1  -> trending

    This is the one classifier with a known null (VR = 1 under a random walk),
    so it is carried as the statistical cross-check on ER.
    """
    lr = np.log(close).diff()
    lrq = np.log(close).diff(q)
    v1 = lr.rolling(n).var(ddof=1)
    vq = lrq.rolling(n).var(ddof=1)
    return vq / (q * v1.replace(0, np.nan))


def adx(df, n=14):
    """Wilder ADX. The conventional trend-strength answer, carried for contrast."""
    h, l = df["high"], df["low"]
    up = h.diff()
    dn = -l.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr_n = true_range(df).ewm(alpha=1 / n, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / tr_n
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / tr_n
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def hurst(close, n=200, max_lag=20):
    """Rolling Hurst exponent via the lagged-variance slope.

    H < 0.5 mean reverting, H = 0.5 random walk, H > 0.5 trending.
    Noisy at these window lengths; carried as a third opinion only.
    """
    lr = np.log(close).diff()
    lags = np.arange(2, max_lag + 1)
    logs = []
    for lag in lags:
        v = lr.rolling(lag).sum().rolling(n).std(ddof=1)
        logs.append(np.log(v.replace(0, np.nan)))
    y = pd.concat(logs, axis=1).to_numpy()
    x = np.log(lags.astype(float))
    xc = x - x.mean()
    denom = (xc ** 2).sum()
    slope = np.einsum("ij,j->i", y - np.nanmean(y, axis=1, keepdims=True), xc) / denom
    return pd.Series(slope, index=close.index)


# Registry so the harness can horse-race them with one loop.
CLASSIFIERS = {
    "ER": lambda df, n: efficiency_ratio(df["close"], n),
    "RangeEff": lambda df, n: range_efficiency(df, n),
    "VR": lambda df, n: variance_ratio(df["close"], q=max(2, n // 3), n=10 * n),
    "ADX": lambda df, n: adx(df, n),
    "Hurst": lambda df, n: hurst(df["close"], n=10 * n),
}
