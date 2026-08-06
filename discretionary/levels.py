#!/usr/bin/env python3
"""Confluence level map builder.

Stdlib only. Reads a TradingView-exported CSV (time,open,high,low,close,Volume,...)
and produces the objective half of Layer 1 in SYSTEM_SPEC_v1.md: every candidate
level from every method, clustered into zones, graded A/B/C by how many independent
families agree.

    python3 levels.py "../BINANCE_BTCUSDT.P, 240.csv"
    python3 levels.py "../BINANCE_BTCUSDT.P, 240.csv" --lookback 400 --near 8

It does NOT tell you whether the structure is real, whether the range is still the
working range, or whether a level has been respected. That judgment is yours and it
is the part that cannot be automated. This just removes the arithmetic so prep takes
minutes instead of an hour.

Families, one point each (per the spec, max one point per family):
  htf     swing highs and lows on this timeframe
  fib     0.618 to 0.786 golden pocket of the most recent major swing leg
  vp      fixed-range volume profile POC / VAH / VAL over the lookback window
  period  prior day and prior week high / low / close
  ma      EMA21 (trending markets only) and week-anchored VWAP
"""

import argparse
import csv
import datetime as dt
import math
import sys

FAMILIES = ("htf", "fib", "vp", "period", "ma")


# ---------------------------------------------------------------- loading

def load_csv(path):
    """Read a TradingView export. Tolerates duplicate trailing column names."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        index = {}
        for i, name in enumerate(header):
            key = name.strip().lower()
            if key not in index:  # first occurrence wins
                index[key] = i
        for required in ("time", "open", "high", "low", "close"):
            if required not in index:
                raise SystemExit("CSV is missing a %r column. Found: %s"
                                 % (required, ", ".join(header)))
        vol_key = "volume" if "volume" in index else None

        bars = []
        for row in reader:
            if not row or not row[index["time"]].strip():
                continue
            try:
                raw_time = float(row[index["time"]])
                bar = {
                    "t": dt.datetime.fromtimestamp(raw_time, dt.timezone.utc),
                    "o": float(row[index["open"]]),
                    "h": float(row[index["high"]]),
                    "l": float(row[index["low"]]),
                    "c": float(row[index["close"]]),
                    "v": float(row[index[vol_key]]) if vol_key and row[index[vol_key]].strip()
                         else 0.0,
                }
            except (ValueError, IndexError):
                continue
            bars.append(bar)
    bars.sort(key=lambda b: b["t"])
    return bars


# ---------------------------------------------------------------- indicators

def ema(values, length):
    if not values:
        return []
    k = 2.0 / (length + 1.0)
    out = [values[0]]
    for v in values[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def atr_rma(bars, length=14):
    """Wilder / RMA-smoothed ATR, matching the ATR14 used throughout the repo."""
    if len(bars) < 2:
        return [0.0] * len(bars)
    trs = [bars[0]["h"] - bars[0]["l"]]
    for i in range(1, len(bars)):
        prev_close = bars[i - 1]["c"]
        trs.append(max(bars[i]["h"] - bars[i]["l"],
                       abs(bars[i]["h"] - prev_close),
                       abs(bars[i]["l"] - prev_close)))
    out, acc = [], None
    for i, tr in enumerate(trs):
        if i < length:
            acc = tr if acc is None else acc + (tr - acc) / (i + 1)
        else:
            acc = (acc * (length - 1) + tr) / length
        out.append(acc)
    return out


def pivots(bars, strength=3):
    """Fractal swing highs and lows. A pivot at i is only known at i+strength."""
    highs, lows = [], []
    n = len(bars)
    for i in range(strength, n - strength):
        window = bars[i - strength:i + strength + 1]
        if bars[i]["h"] == max(b["h"] for b in window):
            highs.append((i, bars[i]["h"]))
        if bars[i]["l"] == min(b["l"] for b in window):
            lows.append((i, bars[i]["l"]))
    return highs, lows


def volume_profile(bars, bins=120, value_area=0.70):
    """Fixed-range profile. Each bar's volume spread uniformly across its range."""
    if not bars:
        return None
    lo = min(b["l"] for b in bars)
    hi = max(b["h"] for b in bars)
    if hi <= lo:
        return None
    width = (hi - lo) / bins
    buckets = [0.0] * bins

    for b in bars:
        if b["v"] <= 0:
            continue
        first = max(0, min(bins - 1, int((b["l"] - lo) / width)))
        last = max(0, min(bins - 1, int((b["h"] - lo) / width)))
        span = last - first + 1
        share = b["v"] / span
        for j in range(first, last + 1):
            buckets[j] += share

    total = sum(buckets)
    if total <= 0:
        return None
    poc_index = buckets.index(max(buckets))

    low_i = high_i = poc_index
    acc = buckets[poc_index]
    while acc < total * value_area and (low_i > 0 or high_i < bins - 1):
        below = buckets[low_i - 1] if low_i > 0 else -1.0
        above = buckets[high_i + 1] if high_i < bins - 1 else -1.0
        if above >= below:
            high_i += 1
            acc += buckets[high_i]
        else:
            low_i -= 1
            acc += buckets[low_i]

    center = lambda i: lo + (i + 0.5) * width
    return {"poc": center(poc_index), "val": center(low_i), "vah": center(high_i)}


def week_anchored_vwap(bars):
    """VWAP re-anchored at the start of each ISO week. Returns the current value."""
    current_week, pv, vol, vwap = None, 0.0, 0.0, None
    for b in bars:
        week = b["t"].isocalendar()[:2]
        if week != current_week:
            current_week, pv, vol = week, 0.0, 0.0
        typical = (b["h"] + b["l"] + b["c"]) / 3.0
        pv += typical * b["v"]
        vol += b["v"]
        if vol > 0:
            vwap = pv / vol
    return vwap


def period_levels(bars):
    """Prior completed day and prior completed ISO week high/low/close."""
    out = {}
    for label, keyfunc in (("day", lambda b: b["t"].date()),
                           ("week", lambda b: b["t"].isocalendar()[:2])):
        groups = {}
        for b in bars:
            groups.setdefault(keyfunc(b), []).append(b)
        keys = sorted(groups)
        if len(keys) < 2:
            continue
        prior = groups[keys[-2]]  # last COMPLETED period
        out["prior %s high" % label] = max(b["h"] for b in prior)
        out["prior %s low" % label] = min(b["l"] for b in prior)
        out["prior %s close" % label] = prior[-1]["c"]
    return out


def golden_pocket(bars, highs, lows):
    """Fib 0.618 to 0.786 of the most recent major swing leg."""
    if not highs or not lows:
        return {}
    last_high, last_low = highs[-1], lows[-1]
    if last_high[0] == last_low[0]:
        return {}
    # The leg runs between the two most recent opposite pivots, in time order.
    if last_high[0] > last_low[0]:
        start, end, direction = last_low[1], last_high[1], "up"
    else:
        start, end, direction = last_high[1], last_low[1], "down"
    span = end - start
    if span == 0:
        return {}
    return {
        "fib 0.618 (%s leg)" % direction: end - span * 0.618,
        "fib 0.705 (%s leg)" % direction: end - span * 0.705,
        "fib 0.786 (%s leg)" % direction: end - span * 0.786,
    }


# ---------------------------------------------------------------- clustering

def cluster(candidates, tolerance):
    """candidates: list of (price, family, label). Group prices within tolerance."""
    candidates = sorted(candidates, key=lambda c: c[0])
    zones, current = [], []
    for item in candidates:
        if current and item[0] - current[-1][0] > tolerance:
            zones.append(current)
            current = []
        current.append(item)
    if current:
        zones.append(current)

    out = []
    for zone in zones:
        prices = [c[0] for c in zone]
        families = sorted({c[1] for c in zone})
        out.append({
            "low": min(prices),
            "high": max(prices),
            "mid": sum(prices) / len(prices),
            "families": families,
            "members": [c[2] for c in zone],
            "grade": "A" if len(families) >= 3 else ("B" if len(families) == 2 else "C"),
        })
    return out


# ---------------------------------------------------------------- report

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", help="TradingView CSV export")
    parser.add_argument("--lookback", type=int, default=500,
                        help="bars of history used for the working range and profile")
    parser.add_argument("--strength", type=int, default=3,
                        help="fractal strength for swing pivots")
    parser.add_argument("--swings", type=int, default=6,
                        help="how many recent swing highs/lows to include")
    parser.add_argument("--near", type=int, default=10,
                        help="how many zones nearest to price to print")
    parser.add_argument("--band", type=float, default=0.25,
                        help="tolerance band as a multiple of ATR14")
    args = parser.parse_args()

    bars = load_csv(args.csv)
    if len(bars) < 60:
        raise SystemExit("Only %d usable bars. Need at least 60." % len(bars))

    window = bars[-args.lookback:]
    last = bars[-1]
    price = last["c"]

    atr = atr_rma(bars)[-1]
    tolerance = atr * args.band
    closes = [b["c"] for b in bars]
    ema21 = ema(closes, 21)[-1]
    ema200 = ema(closes, 200)[-1] if len(closes) >= 200 else None
    trend = None
    if ema200 is not None:
        trend = "UPTREND" if price > ema200 else "DOWNTREND"

    highs, lows = pivots(window, args.strength)
    candidates = []

    for _, p in highs[-args.swings:]:
        candidates.append((p, "htf", "swing high"))
    for _, p in lows[-args.swings:]:
        candidates.append((p, "htf", "swing low"))

    for label, p in golden_pocket(window, highs, lows).items():
        candidates.append((p, "fib", label))

    profile = volume_profile(window)
    if profile:
        for key in ("poc", "vah", "val"):
            candidates.append((profile[key], "vp", key.upper()))

    for label, p in period_levels(bars).items():
        candidates.append((p, "period", label))

    if trend is not None:
        # The spec only allows the 21EMA to count as confluence in a trending market.
        candidates.append((ema21, "ma", "21EMA"))
    vwap = week_anchored_vwap(bars)
    if vwap:
        candidates.append((vwap, "ma", "weekly VWAP"))

    # Range extremes of the working window.
    candidates.append((max(b["h"] for b in window), "htf", "range high"))
    candidates.append((min(b["l"] for b in window), "htf", "range low"))

    zones = cluster(candidates, tolerance)
    zones.sort(key=lambda z: abs(z["mid"] - price))

    print("")
    print("=" * 86)
    print("LEVEL MAP  %s" % args.csv)
    print("=" * 86)
    print("last bar   %s UTC    close %.2f" % (last["t"].strftime("%Y-%m-%d %H:%M"), price))
    print("bars       %d loaded, %d in working window" % (len(bars), len(window)))
    print("ATR14      %.2f   tolerance band %.2f (%.2f x ATR)" % (atr, tolerance, args.band))
    if ema200 is not None:
        print("EMA200     %.2f   ->  %s  (context gate: %s allowed at grade B)"
              % (ema200, trend, "longs" if trend == "UPTREND" else "shorts"))
    else:
        print("EMA200     not enough history, context gate cannot be evaluated")
    print("EMA21      %.2f" % ema21)
    if profile:
        print("profile    POC %.2f   VAH %.2f   VAL %.2f"
              % (profile["poc"], profile["vah"], profile["val"]))
    print("")
    print("%d zones found. Nearest %d to price:" % (len(zones), min(args.near, len(zones))))
    print("-" * 86)
    print("%-6s %-24s %-8s %-7s  %s" % ("grade", "zone", "dist%", "distATR", "constituents"))
    print("-" * 86)
    for zone in zones[:args.near]:
        distance = (zone["mid"] - price) / price * 100.0
        dist_atr = (zone["mid"] - price) / atr if atr else 0.0
        span = "%.2f - %.2f" % (zone["low"], zone["high"])
        if zone["high"] - zone["low"] < 1e-9:
            span = "%.2f" % zone["mid"]
        print("%-6s %-24s %+7.2f%% %+7.2f  %s"
              % (zone["grade"], span, distance, dist_atr,
                 ", ".join(sorted(set(zone["members"])))))
    print("-" * 86)

    tradeable = [z for z in zones if z["grade"] in ("A", "B")]
    print("%d tradeable zones (A or B), %d watch-only (C)."
          % (len(tradeable), len(zones) - len(tradeable)))
    print("")
    print("Reminders before this becomes a trade plan:")
    print("  - A zone is only valid if it was on the map BEFORE price arrived.")
    print("  - C grade is not tradeable. It is not 'nearly a B'.")
    print("  - Check >= 2.0R to the next opposing zone in the list above, or skip.")
    print("  - This tool has no opinion on whether the structure is real. That is your job.")
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
