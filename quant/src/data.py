"""Data loading with hard holdout enforcement.

1m parquet is the only source. Everything else is resampled from it, so bar
boundaries are identical across timeframes by construction.
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "data", "raw1m")

BLOCKS = {
    "TRAIN":   ("2021-01-01", "2025-01-01"),
    "TEST":    ("2025-01-01", "2026-06-22"),
    "DESIGN":  ("2021-01-01", "2026-06-22"),   # TRAIN+TEST, for final fit after freeze
    "HOLDOUT": ("2026-06-22", "2026-07-30"),
}

_UNLOCK = "I_AM_RUNNING_THE_FINAL_HOLDOUT_TEST"


def _slice(df, block, unlock):
    if block == "HOLDOUT" and unlock != _UNLOCK:
        raise PermissionError(
            "HOLDOUT is quarantined. See quant/HOLDOUT_DO_NOT_TOUCH.md")
    lo, hi = BLOCKS[block]
    m = (df["dt"] >= pd.Timestamp(lo, tz="UTC")) & (df["dt"] < pd.Timestamp(hi, tz="UTC"))
    return df.loc[m].reset_index(drop=True)


def load_1m(symbol="BTCUSDT", block="TRAIN", unlock=None):
    df = pd.read_parquet(os.path.join(RAW, f"{symbol}.parquet"))
    return _slice(df, block, unlock)


AGG = {
    "open": "first", "high": "max", "low": "min", "close": "last",
    "volume": "sum", "quote_volume": "sum", "trades": "sum",
    "taker_buy_base": "sum", "taker_buy_quote": "sum",
}


def resample(m1, tf):
    """tf like '5min','15min','1h','4h','1D'. Left-closed, left-labelled:
    a bar stamped t covers [t, t+tf) and is only complete at t+tf."""
    g = m1.set_index("dt").resample(tf, label="left", closed="left").agg(AGG)
    g = g.dropna(subset=["open"]).reset_index()
    return g


def load(symbol="BTCUSDT", tf="15min", block="TRAIN", unlock=None, pad_bars=400):
    """Return (bars_tf, m1) for a block.

    bars_tf carries `pad_bars` extra warmup bars BEFORE the block start so
    indicators are fully spun up at the first tradeable bar. Those warmup rows
    are flagged tradeable=False and must never produce a signal.
    """
    full = pd.read_parquet(os.path.join(RAW, f"{symbol}.parquet"))
    if block == "HOLDOUT" and unlock != _UNLOCK:
        raise PermissionError(
            "HOLDOUT is quarantined. See quant/HOLDOUT_DO_NOT_TOUCH.md")
    lo, hi = BLOCKS[block]
    lo = pd.Timestamp(lo, tz="UTC")
    hi = pd.Timestamp(hi, tz="UTC")

    step = pd.Timedelta(tf)
    warm = lo - step * pad_bars
    sub = full[(full["dt"] >= warm) & (full["dt"] < hi)]
    bars = resample(sub, tf)
    bars["tradeable"] = bars["dt"] >= lo

    m1 = sub[sub["dt"] >= lo - pd.Timedelta("1D")].reset_index(drop=True)
    return bars, m1


def available():
    return sorted(f[:-8] for f in os.listdir(RAW) if f.endswith(".parquet"))


def integrity(symbol):
    df = pd.read_parquet(os.path.join(RAW, f"{symbol}.parquet"))
    d = df["dt"].diff().dt.total_seconds().div(60)
    bad_ohlc = ((df["high"] < df[["open", "close"]].max(axis=1)) |
                (df["low"] > df[["open", "close"]].min(axis=1)) |
                (df["high"] < df["low"])).sum()
    return {
        "symbol": symbol, "bars": len(df),
        "start": str(df["dt"].iloc[0]), "end": str(df["dt"].iloc[-1]),
        "dupes": int(df["dt"].duplicated().sum()),
        "missing_minutes": int((d - 1).clip(lower=0).sum()),
        "max_gap_min": float(np.nanmax(d.values)) if len(d) > 1 else 0.0,
        "bad_ohlc_bars": int(bad_ohlc),
        "zero_vol_bars": int((df["volume"] == 0).sum()),
    }
