"""Gate 0 step 4: fetch the most recent unstudied span and quarantine it.

Fetches Binance USDT-M perp BTCUSDT 15m klines from the first bar AFTER the
studied span (bars opening 2026-06-21 17:00:00 UTC onward) to now, and writes
them to holdout/holdout_15m.csv WITHOUT printing, plotting, or describing a
single row. Only metadata (bar count, span endpoints, integrity counts) is
ever printed.

Separately fetches the two final STUDIED bars (16:15 and 16:45 opens) to
cross-check the TV export partial-bar suspicion. Those two bars are studied
data and may be shown.
"""
import csv
import datetime as dt
import io
import os
import time
import urllib.request
import zipfile

HOLDOUT_START_MS = 1782061200000   # 2026-06-21 17:00:00 UTC, first unstudied bar open
BOUNDARY_START_MS = 1782058500000  # 2026-06-21 16:15:00 UTC (studied, for cross-check)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "holdout")
OUT = os.path.join(OUT_DIR, "holdout_15m.csv")

# Binance USDT-M futures public archive (fapi.binance.com is geo-blocked here)
BASE = "https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/15m"


def fetch_day(day: dt.date):
    url = f"{BASE}/BTCUSDT-15m-{day.isoformat()}.zip"
    req = urllib.request.Request(url, headers={"User-Agent": "gate0-audit"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    zf = zipfile.ZipFile(io.BytesIO(blob))
    with zf.open(zf.namelist()[0]) as f:
        rows = []
        for row in csv.reader(io.TextIOWrapper(f)):
            if row[0] == "open_time":
                continue
            rows.append(row)
    return rows


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    start_day = dt.date(2026, 6, 21)
    today = dt.datetime.now(dt.timezone.utc).date()
    rows = []
    missing_days = []
    day = start_day
    while day < today:  # daily dumps exist up to yesterday
        got = fetch_day(day)
        if got is None:
            missing_days.append(day.isoformat())
        else:
            rows.extend(got)
        day += dt.timedelta(days=1)
        time.sleep(0.2)

    # boundary cross-check: last two studied bars, allowed to display
    print("BOUNDARY BARS (studied span, shown for partial-bar cross-check):")
    for b in rows:
        if BOUNDARY_START_MS <= int(b[0]) < HOLDOUT_START_MS:
            print(f"  open_time={int(b[0])//1000} o={b[1]} h={b[2]} l={b[3]} c={b[4]} vol={b[5]}")

    rows = [r for r in rows if int(r[0]) >= HOLDOUT_START_MS]

    with open(OUT, "w") as f:
        f.write("open_time_ms,open,high,low,close,volume,close_time_ms,quote_vol,trades\n")
        for r in rows:
            f.write(",".join(r[:9]) + "\n")

    # metadata only, never a row
    n = len(rows)
    first = int(rows[0][0]) // 1000 if rows else None
    last = int(rows[-1][0]) // 1000 if rows else None
    gaps = sum(1 for a, b in zip(rows, rows[1:]) if int(b[0]) - int(a[0]) != 900000)
    if missing_days:
        print(f"  WARNING missing daily files: {missing_days}")
    print("\nHOLDOUT METADATA (no row content):")
    print(f"  bars: {n}")
    print(f"  first bar open (unix): {first}")
    print(f"  last bar open (unix): {last}")
    print(f"  non-contiguous steps: {gaps}")
    print(f"  saved to: {OUT}")


if __name__ == "__main__":
    main()
