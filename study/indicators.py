"""Causal indicator library. Every function uses only past/current-bar data.

Signals are evaluated at bar CLOSE; the engine enters at the NEXT bar open,
so no look-ahead. Higher-timeframe context is merged with merge_asof(backward)
using only the last CLOSED higher-TF bar.
"""
import numpy as np
import pandas as pd

# ---------- basic ----------
def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def sma(s, n):
    return s.rolling(n).mean()

def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0)
    dn = -d.clip(upper=0)
    rs = up.ewm(alpha=1/n, adjust=False).mean() / dn.ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1+rs)

def atr(df, n=14):
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h-l), (h-pc).abs(), (l-pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()

def macd(close, fast=12, slow=26, sig=9):
    m = ema(close, fast) - ema(close, slow)
    s = ema(m, sig)
    return m, s, m - s

def bollinger(close, n=20, k=2.0):
    ma = sma(close, n)
    sd = close.rolling(n).std(ddof=0)
    return ma, ma + k*sd, ma - k*sd

def wavetrend(df, n1=10, n2=21):
    hlc3 = (df["high"]+df["low"]+df["close"])/3
    esa = ema(hlc3, n1)
    d = ema((hlc3-esa).abs(), n1)
    ci = (hlc3-esa)/(0.015*d.replace(0, np.nan))
    wt1 = ema(ci, n2)
    wt2 = sma(wt1, 4)
    return wt1, wt2

def rolling_vwap(df, n=20):
    tp = (df["high"]+df["low"]+df["close"])/3
    pv = (tp*df["volume"]).rolling(n).sum()
    v = df["volume"].rolling(n).sum()
    return pv/v

def anchored_daily_vwap(df):
    """VWAP reset each UTC day. Causal (cumulative within day)."""
    tp = (df["high"]+df["low"]+df["close"])/3
    day = df["dt"].dt.floor("D")
    pv = (tp*df["volume"]).groupby(day).cumsum()
    v = df["volume"].groupby(day).cumsum()
    return pv/v

# ---------- swing pivots (confirmed, causal) ----------
def pivots(df, left=3, right=3):
    """Fractal pivots. A pivot at bar i is only CONFIRMED at bar i+right.
    Returns (ph, pl) series aligned to CONFIRMATION bar (i+right), value=pivot price,
    NaN otherwise. Using them at their confirmation bar is fully causal.
    """
    h, l = df["high"].values, df["low"].values
    n = len(df)
    ph = np.full(n, np.nan)
    pl = np.full(n, np.nan)
    for i in range(left, n-right):
        wh = h[i-left:i+right+1]
        wl = l[i-left:i+right+1]
        if h[i] == wh.max() and (wh.argmax() == left):
            ph[i+right] = h[i]      # place at confirmation bar
        if l[i] == wl.min() and (wl.argmin() == left):
            pl[i+right] = l[i]
    return pd.Series(ph, index=df.index), pd.Series(pl, index=df.index)

# ---------- candle patterns (single-bar & 2-bar, causal) ----------
def candle_features(df):
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    rng = (h-l).replace(0, np.nan)
    body = (c-o).abs()
    upper = h - c.where(c>=o, o)
    lower = c.where(c<=o, o) - l
    f = pd.DataFrame(index=df.index)
    f["body_frac"] = body/rng
    f["upper_frac"] = upper/rng
    f["lower_frac"] = lower/rng
    f["bull"] = (c > o).astype(int)
    # bullish engulfing: prev bearish, curr bullish, curr body engulfs prev body
    po, pc = o.shift(1), c.shift(1)
    f["bull_engulf"] = ((pc < po) & (c > o) & (c >= po) & (o <= pc)).astype(int)
    f["bear_engulf"] = ((pc > po) & (c < o) & (c <= po) & (o >= pc)).astype(int)
    # hammer / shooting star
    f["hammer"] = ((f["lower_frac"] >= 0.5) & (f["body_frac"] <= 0.35) & (f["upper_frac"] <= 0.2)).astype(int)
    f["shooting_star"] = ((f["upper_frac"] >= 0.5) & (f["body_frac"] <= 0.35) & (f["lower_frac"] <= 0.2)).astype(int)
    f["marubozu_bull"] = ((f["body_frac"] >= 0.85) & (c > o)).astype(int)
    f["marubozu_bear"] = ((f["body_frac"] >= 0.85) & (c < o)).astype(int)
    f["doji"] = (f["body_frac"] <= 0.1).astype(int)
    return f

# ---------- RSI divergence (causal, using confirmed pivot lows/highs) ----------
def rsi_divergence(df, rsi_series, left=3, right=3, lookback=40):
    """Regular bullish/bearish divergence detected at pivot CONFIRMATION bars.
    Bullish: price makes lower pivot-low but RSI makes higher low.
    Returns two 0/1 series aligned to confirmation bar.
    """
    ph, pl = pivots(df, left, right)
    n = len(df)
    bull = np.zeros(n); bear = np.zeros(n)
    low_idx = [i for i in range(n) if not np.isnan(pl.iloc[i])]
    high_idx = [i for i in range(n) if not np.isnan(ph.iloc[i])]
    lows_price = df["low"].values; highs_price = df["high"].values
    rsi_v = rsi_series.values
    # pivot price located at i-right (the actual pivot bar)
    for k in range(1, len(low_idx)):
        i = low_idx[k]; j = low_idx[k-1]
        pi, pj = i-right, j-right
        if i-j > lookback: continue
        if lows_price[pi] < lows_price[pj] and rsi_v[pi] > rsi_v[pj]:
            bull[i] = 1
    for k in range(1, len(high_idx)):
        i = high_idx[k]; j = high_idx[k-1]
        pi, pj = i-right, j-right
        if i-j > lookback: continue
        if highs_price[pi] > highs_price[pj] and rsi_v[pi] < rsi_v[pj]:
            bear[i] = 1
    return pd.Series(bull, index=df.index), pd.Series(bear, index=df.index)

# ---------- assemble a standard indicator set ----------
def enrich(df):
    df = df.copy()
    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["ema200"] = ema(df["close"], 200)
    df["rsi14"] = rsi(df["close"], 14)
    df["atr14"] = atr(df, 14)
    df["atr_pct"] = df["atr14"]/df["close"]
    m, s, hgt = macd(df["close"])
    df["macd"], df["macd_sig"], df["macd_hist"] = m, s, hgt
    bmid, bup, blo = bollinger(df["close"])
    df["bb_mid"], df["bb_up"], df["bb_lo"] = bmid, bup, blo
    df["wt1"], df["wt2"] = wavetrend(df)
    if df["volume"].notna().any():
        df["vwap_d"] = anchored_daily_vwap(df)
        df["vol_ma20"] = sma(df["volume"], 20)
        df["vol_ratio"] = df["volume"]/df["vol_ma20"]
    cf = candle_features(df)
    for col in cf.columns:
        df["c_"+col] = cf[col]
    ph, pl = pivots(df, 3, 3)
    df["piv_h"], df["piv_l"] = ph, pl
    bull, bear = rsi_divergence(df, df["rsi14"], 3, 3, 40)
    df["div_bull"], df["div_bear"] = bull, bear
    return df

if __name__ == "__main__":
    import sys
    tf = sys.argv[1] if len(sys.argv) > 1 else "1h"
    df = pd.read_parquet(f"data/{tf}.parquet")
    df = enrich(df)
    print(tf, "enriched", df.shape)
    print(df[["dt","close","ema200","rsi14","atr_pct","wt1","div_bull","div_bear"]].tail(3).to_string())
