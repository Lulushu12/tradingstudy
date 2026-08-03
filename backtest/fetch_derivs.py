"""Fetch Binance USD-M perpetual history from the bulk archive.

Three products, all from data.binance.vision (static files, not the geo-blocked
API):

  perp 1h klines   monthly, back to 2020 - includes taker_buy_volume, so
                   aggressive-flow imbalance is available per bar
  fundingRate      monthly, back to 2020 - 8h settlement rate
  metrics          DAILY only, ~2022 onward - 5-minute open interest and
                   long/short ratios. One file per symbol per day, so it is
                   fetched separately and only for a subset.

Writes data/deriv/<SYM>_perp1h.csv and <SYM>_funding.csv.
"""

import csv
import io
import os
import sys
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://data.binance.vision/data/futures/um"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "deriv")
UA = {"User-Agent": "Mozilla/5.0"}

START_YEAR, START_MONTH = 2021, 1
WORKERS = 8


def months(end_y, end_m):
    y, m = START_YEAR, START_MONTH
    out = []
    while (y, m) <= (end_y, end_m):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def grab(url, attempts=3):
    """Return list of CSV rows, or None if the file does not exist."""
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = r.read()
            zf = zipfile.ZipFile(io.BytesIO(blob))
            name = zf.namelist()[0]
            text = zf.read(name).decode()
            rows = list(csv.reader(io.StringIO(text)))
            # Some archives carry a header row, some do not.
            if rows and not rows[0][0].replace(".", "").isdigit():
                rows = rows[1:]
            return rows
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == attempts - 1:
                return None
            time.sleep(1.5 ** i)
        except Exception:
            if i == attempts - 1:
                return None
            time.sleep(1.5 ** i)
    return None


def fetch_symbol(sym, month_list):
    kl_path = os.path.join(OUT, f"{sym}_perp1h.csv")
    fr_path = os.path.join(OUT, f"{sym}_funding.csv")
    if os.path.exists(kl_path) and os.path.exists(fr_path):
        return sym, "cached", 0, 0

    klines, funding = [], []
    for mo in month_list:
        k = grab(f"{BASE}/monthly/klines/{sym}/1h/{sym}-1h-{mo}.zip")
        if k:
            klines += k
        f = grab(f"{BASE}/monthly/fundingRate/{sym}/{sym}-fundingRate-{mo}.zip")
        if f:
            funding += f

    if len(klines) < 5000:
        return sym, "insufficient", len(klines), len(funding)

    klines.sort(key=lambda r: int(r[0]))
    funding.sort(key=lambda r: int(r[0]))

    with open(kl_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["open_time", "open", "high", "low", "close", "volume",
                    "quote_volume", "trades", "taker_buy_volume",
                    "taker_buy_quote_volume"])
        for r in klines:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8], r[9], r[10]])

    with open(fr_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["calc_time", "interval_hours", "funding_rate"])
        for r in funding:
            w.writerow([r[0], r[1], r[2]])

    return sym, "ok", len(klines), len(funding)


def main():
    os.makedirs(OUT, exist_ok=True)
    import json
    universe = json.load(open(os.path.join(HERE, "data", "_universe.json")))
    if len(sys.argv) > 1:
        universe = sys.argv[1].split(",")

    now = time.gmtime()
    ml = months(now.tm_year, now.tm_mon - 1 if now.tm_mon > 1 else 12)
    print(f"{len(universe)} symbols x {len(ml)} months, {WORKERS} workers")

    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch_symbol, s, ml): s for s in universe}
        for fut in as_completed(futs):
            sym, status, nk, nf = fut.result()
            done += 1
            print(f"  [{done}/{len(universe)}] {sym:<12} {status:<13} "
                  f"klines={nk:>6} funding={nf:>5}", flush=True)
    print("done")


if __name__ == "__main__":
    main()
