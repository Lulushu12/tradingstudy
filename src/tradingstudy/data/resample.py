"""Resample cleaned 1m bars to every project timeframe.

Conventions (match TradingView / Binance):
- Bars are labelled by their OPEN time (UTC). A bar labelled t covers [t, t + tf) and is known only at t + tf.
- Intraday timeframes are anchored to UTC midnight (every timeframe here divides 1440 minutes evenly).
- 1W bars are anchored to Monday 00:00 UTC.
- n_1m = number of 1m bars that went into the bar. complete = (n_1m == bar length in minutes).
  Incomplete bars are kept and flagged, never padded.

Usage: uv run python -m tradingstudy.data.resample [SYMBOL ...]
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from tradingstudy.config import CLEAN, SYMBOLS, TIMEFRAMES

MIN_NS = 60 * 10**9
MONDAY_EPOCH_NS = pd.Timestamp("1970-01-05", tz="UTC").value  # first Monday after the Unix epoch


def bucket_starts(ts_ns: np.ndarray, minutes: int) -> np.ndarray:
    width = minutes * MIN_NS
    if minutes == 10080:
        return (ts_ns - MONDAY_EPOCH_NS) // width * width + MONDAY_EPOCH_NS
    # Timeframes that divide a day are UTC-midnight aligned by this formula. Others (e.g. 150m, 600m, 3D) are
    # anchored continuously from the Unix epoch; how TradingView anchors those is not verified.
    return ts_ns // width * width


def resample_1m(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """df: 1m bars indexed by UTC open time, sorted, unique."""
    ts = pd.DatetimeIndex(df.index).as_unit("ns").asi8  # pandas 3 defaults to microseconds; force ns
    b = bucket_starts(ts, minutes)
    starts, idx = np.unique(b, return_index=True)
    ends = np.r_[idx[1:], len(b)] - 1
    o = df["open"].to_numpy()
    out = {
        "open": o[idx],
        "high": np.maximum.reduceat(df["high"].to_numpy(), idx),
        "low": np.minimum.reduceat(df["low"].to_numpy(), idx),
        "close": df["close"].to_numpy()[ends],
    }
    for c in ["volume", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume"]:
        if c in df:
            out[c] = np.add.reduceat(df[c].to_numpy(), idx)
    out["n_1m"] = (ends - idx + 1).astype("int32")
    res = pd.DataFrame(out, index=pd.DatetimeIndex(pd.to_datetime(starts, unit="ns", utc=True), name="ts").as_unit(pd.DatetimeIndex(df.index).unit))
    res["complete"] = res["n_1m"] == minutes
    return res


def main(symbols: list[str]) -> None:
    for sym in symbols:
        m1 = pd.read_parquet(CLEAN / "1m" / f"{sym}.parquet")
        for tf, minutes in TIMEFRAMES.items():
            r = resample_1m(m1, minutes)
            (CLEAN / tf).mkdir(parents=True, exist_ok=True)
            r.to_parquet(CLEAN / tf / f"{sym}.parquet")
        print(f"{sym}: resampled to {list(TIMEFRAMES)}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or SYMBOLS)
