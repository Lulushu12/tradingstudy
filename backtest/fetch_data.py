"""Fetch 10,000 hourly OHLCV candles for ETH, LINK and SOL.

Source: data-api.binance.vision (Binance public market-data mirror, spot klines).
The mirror serves the identical /api/v3/klines payload as api.binance.com but is
not geo-restricted from this environment.

Writes one CSV per symbol into backtest/data/ and reports any gaps in the
hourly series so downstream code never silently assumes continuity.
"""

import csv
import json
import os
import time
import urllib.request

BASE = "https://data-api.binance.vision/api/v3/klines"
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]
BARS = 10_000
PAGE = 1000
HOUR_MS = 3_600_000

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get(url, attempts=5):
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as exc:  # noqa: BLE001 - transient network, retry
            if i == attempts - 1:
                raise
            wait = 2 ** i
            print(f"    retry {i + 1} after {exc} (sleep {wait}s)")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def last_closed_hour_ms():
    """Open time of the most recent *fully closed* hourly candle."""
    now_ms = int(time.time() * 1000)
    current_open = (now_ms // HOUR_MS) * HOUR_MS
    return current_open - HOUR_MS


def fetch_symbol(symbol):
    """Page backwards from the last closed hour until we have BARS candles."""
    end_open = last_closed_hour_ms()
    # endTime is inclusive of the candle whose openTime <= endTime, so target the
    # close of the last complete bar.
    cursor = end_open + HOUR_MS - 1
    collected = {}

    while len(collected) < BARS:
        url = f"{BASE}?symbol={symbol}&interval=1h&limit={PAGE}&endTime={cursor}"
        rows = get(url)
        if not rows:
            print(f"    {symbol}: exchange returned no further history")
            break
        for r in rows:
            collected[int(r[0])] = r
        oldest = int(rows[0][0])
        if oldest <= 0:
            break
        cursor = oldest - 1
        print(f"    {symbol}: {len(collected)}/{BARS}")
        time.sleep(0.25)

    ordered = [collected[k] for k in sorted(collected)]
    # Keep exactly the most recent BARS candles.
    return ordered[-BARS:]


def check_gaps(rows):
    gaps = []
    for prev, cur in zip(rows, rows[1:]):
        step = int(cur[0]) - int(prev[0])
        if step != HOUR_MS:
            gaps.append((int(prev[0]), int(cur[0]), step // HOUR_MS))
    return gaps


def write_csv(symbol, rows):
    path = os.path.join(OUT_DIR, f"{symbol}_1h.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["open_time", "open", "high", "low", "close", "volume", "quote_volume", "trades"]
        )
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8]])
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for symbol in SYMBOLS:
        print(f"[{symbol}] fetching...")
        rows = fetch_symbol(symbol)
        gaps = check_gaps(rows)
        path = write_csv(symbol, rows)
        first = time.strftime("%Y-%m-%d %H:%M", time.gmtime(int(rows[0][0]) / 1000))
        last = time.strftime("%Y-%m-%d %H:%M", time.gmtime(int(rows[-1][0]) / 1000))
        print(f"[{symbol}] {len(rows)} bars  {first} -> {last} UTC  gaps={len(gaps)}")
        for g in gaps[:5]:
            print(f"    gap: missing {g[2] - 1}h after {time.strftime('%Y-%m-%d %H:%M', time.gmtime(g[0] / 1000))}")
        print(f"[{symbol}] wrote {path}")


if __name__ == "__main__":
    main()
