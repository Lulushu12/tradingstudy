"""Fetch the Binance auxiliary series the first study never used.

The original 71 features were built from OHLCV plus taker flow. That is only a
slice of what Binance publishes free, and the omitted series are arguably the
highest-signal ones in crypto:

  metrics/        5-minute open interest (contracts and USD), top-trader
                  long/short ratio BY COUNT and BY POSITION SIZE, overall
                  account long/short ratio, taker buy/sell volume ratio.
                  Real positioning data. From 2021-01-05.
  fundingRate/    8-hourly funding. The most documented crypto anomaly there is:
                  funding is what longs pay shorts to hold, i.e. the price of
                  leveraged positioning. From 2020-01.
  premiumIndex/   perp vs index basis, hourly.
  bookDepth/      resting notional at +/-1..5% from mid. Actual liquidity, not
                  a volume proxy.

Not published: bookTicker and liquidationSnapshot (404 on the public dump).
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
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "aux")

CORE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def _zipcsv(url, **kw):
    try:
        r = requests.get(url, timeout=90)
        if r.status_code != 200:
            return None
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            with z.open(z.namelist()[0]) as fh:
                return pd.read_csv(fh, **kw)
    except Exception:
        return None


def months(a, b):
    out, y, m = [], a[0], a[1]
    while (y, m) <= b:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def days(start="2021-01-01", end="2026-07-30"):
    return [d.strftime("%Y-%m-%d")
            for d in pd.date_range(start, end, freq="D")]


# ---------------------------------------------------------------- funding
def funding(symbol):
    per = months((2021, 1), (2026, 7))
    with ThreadPoolExecutor(max_workers=10) as ex:
        parts = list(ex.map(
            lambda p: _zipcsv(f"{BASE}/monthly/fundingRate/{symbol}/"
                              f"{symbol}-fundingRate-{p}.zip"), per))
    got = [p for p in parts if p is not None and len(p)]
    if not got:
        return None
    d = pd.concat(got, ignore_index=True)
    d.columns = [c.strip() for c in d.columns]
    d["dt"] = pd.to_datetime(d["calc_time"], unit="ms", utc=True)
    d = d[["dt", "last_funding_rate", "funding_interval_hours"]]
    d = d.rename(columns={"last_funding_rate": "funding"})
    return d.drop_duplicates("dt").sort_values("dt").reset_index(drop=True)


# ---------------------------------------------------------------- metrics
def metrics(symbol, workers=16):
    dd = days()
    def one(d):
        return _zipcsv(f"{BASE}/daily/metrics/{symbol}/{symbol}-metrics-{d}.zip")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        parts = list(ex.map(one, dd))
    got = [p for p in parts if p is not None and len(p)]
    if not got:
        return None
    d = pd.concat(got, ignore_index=True)
    d.columns = [c.strip() for c in d.columns]
    d["dt"] = pd.to_datetime(d["create_time"], utc=True)
    keep = ["dt", "sum_open_interest", "sum_open_interest_value",
            "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
            "count_long_short_ratio", "sum_taker_long_short_vol_ratio"]
    d = d[[c for c in keep if c in d.columns]]
    for c in d.columns:
        if c != "dt":
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.drop_duplicates("dt").sort_values("dt").reset_index(drop=True)


# ---------------------------------------------------------------- premium
def premium(symbol):
    per = months((2021, 1), (2026, 7))
    cols = ["open_time", "open", "high", "low", "close", "v", "close_time",
            "qv", "n", "tb", "tq", "ig"]
    def one(p):
        return _zipcsv(f"{BASE}/monthly/premiumIndexKlines/{symbol}/1h/"
                       f"{symbol}-1h-{p}.zip", header=None, names=cols)
    with ThreadPoolExecutor(max_workers=10) as ex:
        parts = list(ex.map(one, per))
    got = [p for p in parts if p is not None and len(p)]
    if not got:
        return None
    d = pd.concat(got, ignore_index=True)
    ot = pd.to_numeric(d["open_time"], errors="coerce")
    ot = np.where(ot > 3e15, ot // 1000, ot)
    d["dt"] = pd.to_datetime(ot, unit="ms", utc=True)
    d = d[["dt", "close"]].rename(columns={"close": "premium"})
    d["premium"] = pd.to_numeric(d["premium"], errors="coerce")
    return d.dropna().drop_duplicates("dt").sort_values("dt").reset_index(drop=True)


def build(symbols=None, what=("funding", "metrics", "premium")):
    symbols = symbols or CORE
    os.makedirs(OUT, exist_ok=True)
    for s in symbols:
        for kind in what:
            path = os.path.join(OUT, f"{s}_{kind}.parquet")
            if os.path.exists(path):
                d = pd.read_parquet(path)
                print(f"  {s:9} {kind:8} cached  {len(d):>8,} rows")
                continue
            fn = {"funding": funding, "metrics": metrics, "premium": premium}[kind]
            d = fn(s)
            if d is None or not len(d):
                print(f"  {s:9} {kind:8} FAILED")
                continue
            d.to_parquet(path, index=False, compression="zstd")
            print(f"  {s:9} {kind:8} {len(d):>8,} rows  "
                  f"{d.dt.min()} -> {d.dt.max()}")


if __name__ == "__main__":
    syms = sys.argv[1:] or CORE
    print(f"fetching auxiliary series for {syms}")
    build(syms)
