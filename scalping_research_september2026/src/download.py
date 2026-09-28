"""Download Binance USD-M futures 1m klines + funding rates from data.binance.vision.

Monthly archives for complete months, daily archives for the current month.
Output: data/{SYM}_1m.parquet, data/{SYM}_funding.parquet
"""
import io
import sys
import zipfile
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

BASE = "https://data.binance.vision/data/futures/um"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT"]
START = dt.date(2020, 1, 1)
DATA = Path(__file__).resolve().parent.parent / "data"
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]

session = requests.Session()


def fetch_zip_csv(url, names=None):
    for attempt in range(5):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                raw = z.read(z.namelist()[0])
            df = pd.read_csv(io.BytesIO(raw), header=None)
            # some files have a header row, some don't
            if isinstance(df.iloc[0, 0], str) and not str(df.iloc[0, 0]).isdigit():
                df = df.iloc[1:]
            if names:
                df.columns = names[: df.shape[1]]
            return df
        except Exception as e:  # network flake
            if attempt == 4:
                print("FAILED", url, e, file=sys.stderr)
                return None
    return None


def months(start, end):
    d = start.replace(day=1)
    while d < end.replace(day=1):
        yield d
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def klines(sym):
    today = dt.date.today()
    urls = [f"{BASE}/monthly/klines/{sym}/1m/{sym}-1m-{m:%Y-%m}.zip" for m in months(START, today)]
    d = today.replace(day=1)
    while d < today:
        urls.append(f"{BASE}/daily/klines/{sym}/1m/{sym}-1m-{d:%Y-%m-%d}.zip")
        d += dt.timedelta(days=1)
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(lambda u: fetch_zip_csv(u, COLS), urls) if p is not None]
    df = pd.concat(parts, ignore_index=True)
    df = df[["open_time", "open", "high", "low", "close", "volume", "count", "taker_buy_volume"]]
    df = df.astype({"open_time": "int64", "open": "float64", "high": "float64", "low": "float64",
                    "close": "float64", "volume": "float64", "count": "int64", "taker_buy_volume": "float64"})
    df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    df.to_parquet(DATA / f"{sym}_1m.parquet")
    print(sym, len(df), pd.to_datetime(df.open_time.iloc[0], unit="ms"), pd.to_datetime(df.open_time.iloc[-1], unit="ms"))


def funding(sym):
    today = dt.date.today()
    urls = [f"{BASE}/monthly/fundingRate/{sym}/{sym}-fundingRate-{m:%Y-%m}.zip" for m in months(START, today)]
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(lambda u: fetch_zip_csv(u, ["calc_time", "interval", "rate"]), urls) if p is not None]
    if not parts:
        return
    df = pd.concat(parts, ignore_index=True).astype({"calc_time": "int64", "rate": "float64"})
    df.drop_duplicates("calc_time").sort_values("calc_time").to_parquet(DATA / f"{sym}_funding.parquet")
    print(sym, "funding rows", len(df))


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    for s in sys.argv[1:] or SYMBOLS:
        klines(s)
        funding(s)
