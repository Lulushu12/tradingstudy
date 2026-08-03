"""Fetch the multi-asset universe across all three study windows.

Writes data/<SYM>_1h.csv, _1h_prior.csv and _1h_early.csv for every symbol in
data/_universe.json, skipping any that already exist.
"""

import calendar
import csv
import json
import os
import time
import urllib.request

BASE = "https://data-api.binance.vision/api/v3/klines"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
BARS = 10_000
PAGE = 1000
HOUR = 3_600_000

# (tag, exclusive end instant) - each window ends where the next begins.
WINDOWS = [("", None),
           ("_prior", "2025-06-12T22:00:00Z"),
           ("_early", "2024-04-22T06:00:00Z")]


def get(url, attempts=5):
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(2 ** i)


def end_open(iso):
    if iso is None:
        return ((int(time.time() * 1000) // HOUR) * HOUR) - HOUR
    return int(calendar.timegm(time.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")) * 1000) - HOUR


def fetch(symbol, iso):
    cursor = end_open(iso) + HOUR - 1
    got = {}
    while len(got) < BARS:
        rows = get(f"{BASE}?symbol={symbol}&interval=1h&limit={PAGE}&endTime={cursor}")
        if not rows:
            break
        for r in rows:
            got[int(r[0])] = r
        cursor = int(rows[0][0]) - 1
        time.sleep(0.12)
    return [got[k] for k in sorted(got)][-BARS:]


def main():
    universe = json.load(open(os.path.join(DATA, "_universe.json")))
    for n, sym in enumerate(universe, 1):
        for tag, iso in WINDOWS:
            path = os.path.join(DATA, f"{sym}_1h{tag}.csv")
            if os.path.exists(path):
                continue
            rows = fetch(sym, iso)
            if len(rows) < BARS:
                print(f"  {sym}{tag}: only {len(rows)} bars, SKIPPED")
                continue
            gaps = sum(1 for a, b in zip(rows, rows[1:])
                       if int(b[0]) - int(a[0]) != HOUR)
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["open_time", "open", "high", "low", "close",
                            "volume", "quote_volume", "trades"])
                for r in rows:
                    w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8]])
            print(f"  [{n}/{len(universe)}] {sym}{tag or '_main'}: {len(rows)} bars, {gaps} gaps")
    print("done")


if __name__ == "__main__":
    main()
