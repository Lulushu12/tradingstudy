"""Re-run the identical system on a different candle size.

    python3 run_timeframe.py 15m

Every strategy parameter is expressed in BARS, so nothing is retuned: EMA200
becomes 200 fifteen-minute bars (50 hours) instead of 200 hourly ones, and a
48-bar time stop becomes 12 hours instead of 48. That is the literal reading of
"run the same system on 15m candles", and it is the interesting one - it asks
whether the edge is a property of the rules or of the hourly timeframe.

Reports the full book, the selective book, and the 6-8 conviction band, with a
time split and a block bootstrap on the band.
"""

import csv
import os
import sys

import numpy as np

import run_backtest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

rng = np.random.default_rng(11)


def stats(rows):
    if not rows:
        return None
    rs = np.array([float(r["r_multiple"]) for r in rows])
    w = rs[rs > 0]
    losses = rs[rs <= 0]
    gl = abs(losses.sum())
    aw = w.mean() if len(w) else 0.0
    al = abs(losses.mean()) if len(losses) else 0.0
    gross = np.array([float(r["gross_pct"]) / float(r["stop_pct"]) for r in rows])
    cost = np.array([float(r["cost_pct"]) / float(r["stop_pct"]) for r in rows])
    return {
        "n": len(rs), "win": 100 * len(w) / len(rs), "avg": rs.mean(),
        "gross": gross.mean(), "tot": rs.sum(),
        "pf": (w.sum() / gl) if gl > 0 else np.nan,
        "be": 100 * al / (aw + al) if (aw + al) > 0 else np.nan,
        "cost_share": 100 * cost.mean(),
        "stop_pct": np.mean([float(r["stop_pct"]) for r in rows]),
        "bars": np.mean([int(r["bars_held"]) for r in rows]),
    }


def line(tag, s):
    if not s:
        print(f"{tag:<22} (no trades)")
        return
    print(f"{tag:<22}{s['n']:>7}{s['win']:>8.1f}{s['be']:>7.1f}{s['avg']:>9.3f}"
          f"{s['gross']:>9.3f}{s['tot']:>10.1f}{s['pf']:>7.2f}{s['cost_share']:>8.1f}"
          f"{s['stop_pct']:>9.2f}{s['bars']:>8.1f}")


HDR = (f"{'book':<22}{'n':>7}{'win%':>8}{'BE%':>7}{'avgR':>9}{'grossR':>9}"
       f"{'totR':>10}{'PF':>7}{'cost%R':>8}{'stop%':>9}{'bars':>8}")


def boot(rows, block):
    rs = np.array([float(r["r_multiple"]) for r in rows])
    bars = np.array([int(r["bar_index"]) for r in rows])
    blk = bars // block
    ub = np.unique(blk)
    by = {b: np.flatnonzero(blk == b) for b in ub}
    means = np.empty(4000)
    wins = np.empty(4000)
    won = (rs > 0).astype(float)
    for i in range(4000):
        sel = np.concatenate([by[p] for p in rng.choice(ub, size=len(ub), replace=True)])
        means[i] = rs[sel].mean()
        wins[i] = 100 * won[sel].mean()
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)),
            100 * float((means > 0).mean()),
            float(np.percentile(wins, 2.5)), float(np.percentile(wins, 97.5)))


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else "15m"
    run_backtest.SUFFIX = suffix
    bars_per_week = {"15m": 672, "1h": 168}[suffix]

    print(f"Running the unchanged system on {suffix} candles\n")
    all_band = []
    for symbol in SYMBOLS:
        trades = run_backtest.run_symbol(symbol)
        out = os.path.join(DATA, f"{symbol}_{suffix}_trades.csv")
        with open(out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=run_backtest.FIELDS)
            w.writeheader()
            w.writerows(trades)

        closed = [t for t in trades if t["status"] == "CLOSED"]
        closed = [{k: str(v) for k, v in t.items()} for t in closed]
        sel = [t for t in closed if float(t["conviction"]) >= 6.0]
        band = [t for t in closed if 6.0 <= float(t["conviction"]) < 8.0]
        hi = [t for t in closed if float(t["conviction"]) >= 8.0]
        all_band += band

        print("=" * 110)
        print(f"{symbol}  ({suffix})")
        print("=" * 110)
        print(HDR)
        line("all trades", stats(closed))
        line("selective >=6", stats(sel))
        line("6-8 band", stats(band))
        line("8-10 band", stats(hi))

        idx = [int(t["bar_index"]) for t in band]
        if idx:
            mid = (min(idx) + max(idx)) // 2
            line("  6-8 first half", stats([t for t in band if int(t["bar_index"]) <= mid]))
            line("  6-8 second half", stats([t for t in band if int(t["bar_index"]) > mid]))
        print()

    print("=" * 110)
    print(f"POOLED 6-8 band across all three symbols ({suffix})")
    print("=" * 110)
    print(HDR)
    line("6-8 pooled", stats(all_band))
    lo, hi_, p, wlo, whi = boot(all_band, bars_per_week)
    s = stats(all_band)
    print(f"\n  block bootstrap (1 week = {bars_per_week} bars, 4000 resamples):")
    print(f"    avg R    {s['avg']:+.3f}   95% CI [{lo:+.3f}, {hi_:+.3f}]   P(>0) = {p:.1f}%")
    print(f"    win rate {s['win']:.1f}%   95% CI [{wlo:.1f}%, {whi:.1f}%]   breakeven {s['be']:.1f}%")
    print(f"    verdict: {'CLEARS the bar' if lo > 0 else 'does NOT clear the bar'}")


if __name__ == "__main__":
    main()
