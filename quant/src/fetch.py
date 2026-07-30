"""Download 1m futures klines from data.binance.vision and store as parquet.

1m is the single source of truth; every other timeframe is resampled from it so
bar boundaries are guaranteed consistent and stop/target hits can be resolved on
the real intrabar path.

Binance kline columns:
  open_time, open, high, low, close, volume, close_time, quote_volume,
  trades, taker_buy_base, taker_buy_quote, ignore

taker_buy_base is genuine aggressor-side flow, not an OHLCV derivative. Kept.
"""
import io
import os
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

BASE = "https://data.binance.vision/data/futures/um"
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"]
KEEP = ["open", "high", "low", "close", "volume", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote"]

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw1m")


def months(start, end):
    out = []
    y, m = start
    while (y, m) <= end:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def fetch_one(symbol, period, kind="monthly"):
    url = f"{BASE}/{kind}/klines/{symbol}/1m/{symbol}-1m-{period}.zip"
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                name = z.namelist()[0]
                with z.open(name) as fh:
                    head = fh.read(64)
                skip = 1 if head[:9].lower().startswith(b"open_time") else 0
                with z.open(name) as fh:
                    df = pd.read_csv(fh, header=None, names=COLS, skiprows=skip)
            return df
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                print(f"  FAIL {symbol} {period}: {e}", file=sys.stderr)
                return None
    return None


def build(symbol, start=(2021, 1), end=(2026, 7), daily_tail=None):
    periods = months(start, end)
    with ThreadPoolExecutor(max_workers=8) as ex:
        parts = list(ex.map(lambda p: fetch_one(symbol, p), periods))
    got = [p for p in parts if p is not None]
    missing = [p for p, d in zip(periods, parts) if d is None]

    if daily_tail:
        with ThreadPoolExecutor(max_workers=8) as ex:
            dparts = list(ex.map(lambda p: fetch_one(symbol, p, "daily"), daily_tail))
        got += [p for p in dparts if p is not None]

    if not got:
        print(f"{symbol}: NO DATA", file=sys.stderr)
        return None

    df = pd.concat(got, ignore_index=True)
    # open_time is ms for recent files, us for some 2025+ files. Normalise.
    ot = df["open_time"].astype("int64")
    ot = np.where(ot > 3e15, ot // 1000, ot)
    df["dt"] = pd.to_datetime(ot, unit="ms", utc=True)
    df = df[["dt"] + KEEP].drop_duplicates("dt").sort_values("dt").reset_index(drop=True)
    for c in KEEP:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"])

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{symbol}.parquet")
    df.to_parquet(path, index=False, compression="zstd")

    gaps = df["dt"].diff().dt.total_seconds().div(60).fillna(1)
    print(f"{symbol}: {len(df):,} bars  {df.dt.iloc[0]} -> {df.dt.iloc[-1]}  "
          f"missing_months={len(missing)}  gap_bars={int((gaps - 1).clip(lower=0).sum()):,}")
    return df


if __name__ == "__main__":
    syms = sys.argv[1:] or ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]
    tail = [f"2026-07-{d:02d}" for d in range(1, 32)]
    for s in syms:
        build(s, daily_tail=tail)
