"""Fetch open-interest history from the Binance daily metrics archive.

Metrics exist only as DAILY files (~2022 onward), one per symbol per day, at
5-minute granularity. That is ~1,300 files per symbol, so this is heavily
parallelised and writes an hourly-aggregated result.

Columns in the source:
  create_time, symbol, sum_open_interest, sum_open_interest_value,
  count_toptrader_long_short_ratio, sum_toptrader_long_short_ratio,
  count_long_short_ratio, sum_taker_long_short_vol_ratio

Aggregation to hourly takes the LAST 5-minute observation inside each hour,
which is the state of the book at the bar close - the only value a decision
taken at that close could have used.
"""

import csv
import datetime as dt
import io
import os
import sys
import time
import urllib.request
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://data.binance.vision/data/futures/um/daily/metrics"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "deriv")
UA = {"User-Agent": "Mozilla/5.0"}

START = dt.date(2022, 1, 1)
WORKERS = 12

DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
                   "DOGEUSDT", "SOLUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT",
                   "DOTUSDT", "NEARUSDT", "TRXUSDT", "UNIUSDT", "FILUSDT"]


def day_list():
    end = dt.date.today() - dt.timedelta(days=1)
    d, out = START, []
    while d <= end:
        out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def grab_day(sym, day):
    url = f"{BASE}/{sym}/{sym}-metrics-{day}.zip"
    for i in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                blob = r.read()
            zf = zipfile.ZipFile(io.BytesIO(blob))
            text = zf.read(zf.namelist()[0]).decode()
            rows = list(csv.reader(io.StringIO(text)))
            return rows[1:] if rows and rows[0][0] == "create_time" else rows
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return []


def fetch_symbol(sym, days):
    path = os.path.join(OUT, f"{sym}_oi1h.csv")
    if os.path.exists(path):
        return sym, "cached", 0

    hourly = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(grab_day, sym, d): d for d in days}
        for fut in as_completed(futs):
            for r in fut.result():
                if len(r) < 8:
                    continue
                try:
                    t = dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                ms = int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
                hour = ms - (ms % 3_600_000)
                # Keep the latest observation inside the hour.
                prev = hourly.get(hour)
                if prev is None or ms > prev[0]:
                    hourly[hour] = (ms, r)

    if len(hourly) < 5000:
        return sym, f"insufficient ({len(hourly)}h)", len(hourly)

    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["hour", "open_interest", "open_interest_value",
                    "toptrader_ls_ratio_count", "toptrader_ls_ratio_pos",
                    "global_ls_ratio", "taker_ls_vol_ratio"])
        for hour in sorted(hourly):
            r = hourly[hour][1]
            w.writerow([hour, r[2], r[3], r[4], r[5], r[6], r[7]])
    return sym, "ok", len(hourly)


def main():
    os.makedirs(OUT, exist_ok=True)
    symbols = sys.argv[1].split(",") if len(sys.argv) > 1 else DEFAULT_SYMBOLS
    days = day_list()
    print(f"{len(symbols)} symbols x {len(days)} days, {WORKERS} workers per symbol")
    for i, sym in enumerate(symbols, 1):
        t0 = time.time()
        s, status, n = fetch_symbol(sym, days)
        print(f"  [{i}/{len(symbols)}] {s:<12} {status:<20} {n:>6} hourly rows "
              f"({time.time() - t0:.0f}s)", flush=True)
    print("done")


if __name__ == "__main__":
    main()
