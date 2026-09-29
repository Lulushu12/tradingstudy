"""Load 1m data and build OHLCV bars at any timeframe (UTC-aligned, like TradingView)."""
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT"]
TF_MIN = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120,
          "4h": 240, "6h": 360, "12h": 720, "1d": 1440}

# research periods
IS_END = pd.Timestamp("2024-01-01", tz="UTC")       # in-sample: 2020-01 .. 2023-12
OOS_END = pd.Timestamp("2025-10-01", tz="UTC")      # out-of-sample: 2024-01 .. 2025-09
# holdout: 2025-10 .. present (locked until final evaluation)


@lru_cache(maxsize=1)
def load_1m(sym):
    df = pd.read_parquet(DATA / f"{sym}_1m.parquet")
    df.index = pd.to_datetime(df.pop("open_time"), unit="ms", utc=True)
    df.index.name = "time"
    return df


@lru_cache(maxsize=12)
def bars(sym, tf):
    """OHLCV bars for tf. Index = bar open time. Includes taker buy volume and trade count."""
    m = load_1m(sym)
    if tf == "1m":
        return m
    rule = {"1d": "1D"}.get(tf, f"{TF_MIN[tf]}min")
    agg = m.resample(rule, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last",
         "volume": "sum", "count": "sum", "taker_buy_volume": "sum"})
    return agg.dropna(subset=["open"])


def htf_to_ltf(htf_df, htf, ltf_index, ltf):
    """Align HTF values to LTF bars with NO lookahead.

    A value computed on an HTF bar is known only once that bar has closed.
    For an LTF bar whose close time is t, we use the latest HTF bar with close time <= t.
    Returns DataFrame indexed like ltf_index.
    """
    htf_close_time = htf_df.index + pd.Timedelta(minutes=TF_MIN[htf])
    src = htf_df.copy()
    src.index = htf_close_time
    ltf_close_time = ltf_index + pd.Timedelta(minutes=TF_MIN[ltf])
    out = src.reindex(src.index.union(ltf_close_time)).ffill().reindex(ltf_close_time)
    out.index = ltf_index
    return out


def minute_map(sym, tf):
    """For each tf bar, start index into the 1m array (for intrabar resolution)."""
    m = load_1m(sym)
    b = bars(sym, tf)
    return np.searchsorted(m.index.values, b.index.values).astype(np.int64)
