"""Fetch external Binance USDT-M series for research cycle 1, capped at the
holdout cutoff. Files that straddle the cutoff (June 2026 monthlies, the
2026-06-21 daily) are filtered by timestamp at parse time; quarantined rows
are dropped mechanically and never displayed.

Outputs (parquet, in this directory):
  funding.parquet   funding_time_ms, funding_rate         (8h prints)
  premium15.parquet open_time_ms, premium_close           (15m)
  oi5.parquet       ts_ms, sum_open_interest              (5m, from 2021-12)
"""
import csv
import datetime as dt
import io
import os
import time
import urllib.request
import zipfile
import concurrent.futures as cf

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://data.binance.vision/data/futures/um"
CUTOFF_MS = 1782061200000          # 2026-06-21 17:00 UTC, exclusive


def get_zip_rows(url, attempts=5):
    req = urllib.request.Request(url, headers={"User-Agent": "research-cycle1"})
    blob = None
    for k in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if k == attempts - 1:
                raise
            time.sleep(2 ** k)
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if k == attempts - 1:
                raise
            time.sleep(2 ** k)
    zf = zipfile.ZipFile(io.BytesIO(blob))
    with zf.open(zf.namelist()[0]) as f:
        return list(csv.reader(io.TextIOWrapper(f)))


def months(start, end):
    y, m = start
    while (y, m) <= end:
        yield f"{y}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def fetch_funding():
    rows = []
    for ym in months((2021, 1), (2026, 6)):
        got = get_zip_rows(f"{BASE}/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-{ym}.zip")
        if got is None:
            print(f"  funding {ym}: MISSING")
            continue
        for r in got:
            if r[0] in ("calc_time", "calcTime", "fundingTime"):
                continue
            t = int(r[0])
            if t < CUTOFF_MS:
                rows.append((t, float(r[2]) if len(r) > 2 else float(r[1])))
    df = pd.DataFrame(rows, columns=["funding_time_ms", "funding_rate"]).sort_values("funding_time_ms")
    df.to_parquet(os.path.join(HERE, "funding.parquet"))
    print(f"funding: {len(df)} prints, "
          f"{pd.to_datetime(df.funding_time_ms.iloc[0], unit='ms', utc=True)} -> "
          f"{pd.to_datetime(df.funding_time_ms.iloc[-1], unit='ms', utc=True)}")


def fetch_premium():
    rows = []
    for ym in months((2021, 1), (2026, 6)):
        got = get_zip_rows(f"{BASE}/monthly/premiumIndexKlines/BTCUSDT/15m/BTCUSDT-15m-{ym}.zip")
        if got is None:
            print(f"  premium {ym}: MISSING")
            continue
        for r in got:
            if r[0] == "open_time":
                continue
            t = int(r[0])
            if t < CUTOFF_MS:
                rows.append((t, float(r[4])))
    df = pd.DataFrame(rows, columns=["open_time_ms", "premium_close"]).sort_values("open_time_ms")
    df = df.drop_duplicates("open_time_ms")
    df.to_parquet(os.path.join(HERE, "premium15.parquet"))
    print(f"premium: {len(df)} bars, "
          f"{pd.to_datetime(df.open_time_ms.iloc[0], unit='ms', utc=True)} -> "
          f"{pd.to_datetime(df.open_time_ms.iloc[-1], unit='ms', utc=True)}")


def fetch_metrics():
    days = []
    d = dt.date(2021, 12, 1)
    while d <= dt.date(2026, 6, 21):
        days.append(d)
        d += dt.timedelta(days=1)

    def one(day):
        got = get_zip_rows(f"{BASE}/daily/metrics/BTCUSDT/BTCUSDT-metrics-{day.isoformat()}.zip")
        if got is None:
            return day, None
        out = []
        header = got[0]
        try:
            ti = header.index("create_time")
            oi = header.index("sum_open_interest")
            body = got[1:]
        except ValueError:
            ti, oi, body = 0, 2, got
        for r in body:
            try:
                ts = r[ti]
                t = int(pd.Timestamp(ts, tz="UTC").value // 10**6) if not ts.isdigit() else int(ts)
                if t < CUTOFF_MS:
                    out.append((t, float(r[oi])))
            except (ValueError, IndexError):
                continue
        return day, out

    rows, missing = [], []
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for day, out in ex.map(one, days):
            if out is None:
                missing.append(day.isoformat())
            else:
                rows.extend(out)
    df = pd.DataFrame(rows, columns=["ts_ms", "sum_open_interest"]).sort_values("ts_ms")
    df = df.drop_duplicates("ts_ms")
    df.to_parquet(os.path.join(HERE, "oi5.parquet"))
    print(f"metrics: {len(df)} rows, missing days: {len(missing)}"
          + (f" {missing[:5]}..." if missing else ""))
    print(f"  span {pd.to_datetime(df.ts_ms.iloc[0], unit='ms', utc=True)} -> "
          f"{pd.to_datetime(df.ts_ms.iloc[-1], unit='ms', utc=True)}")


if __name__ == "__main__":
    if not os.path.exists(os.path.join(HERE, "funding.parquet")):
        fetch_funding()
    if not os.path.exists(os.path.join(HERE, "premium15.parquet")):
        fetch_premium()
    if not os.path.exists(os.path.join(HERE, "oi5.parquet")):
        fetch_metrics()
