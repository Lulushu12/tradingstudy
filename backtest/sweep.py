"""Stop-width x target sensitivity on the selective book.

Scored in average R per trade. This study risks a fixed dollar amount per
trade, so position size shrinks as the stop widens and P&L = R x risk_$ -
which makes average R directly proportional to expected profit.

An earlier version scored this grid in average NET % per trade. That is the
correct metric only under constant-NOTIONAL sizing, where the position size is
the same regardless of stop distance and a wider stop simply means holding
through a bigger move. Under constant risk it overstates the value of widening
a stop, and it moved the apparent optimum: net % favoured stop x2.0-3.0, while
average R favours x1.3-1.6 with a far target. Both are recorded per cell.
"""

import csv
import itertools
import json
import os

import numpy as np

import indicators
import simulate
import strategy
from run_backtest import load, WARMUP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

STOP_SCALES = [0.70, 0.85, 1.00, 1.15, 1.30, 1.60, 2.00, 2.50]
TARGET_R = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]

# Configurations whose exit mix gets recorded, to show WHERE the P&L comes from.
EXIT_MIX_CONFIGS = [(1.00, 2.5, "as_traded"), (2.00, 4.0, "sweep_optimum")]


def run(symbol, stop_scale, target_r, selective_only=True, cache={}):
    if symbol not in cache:
        ts, o, h, l, c, v = load(symbol)
        cache[symbol] = (o, h, l, c, indicators.build(o, h, l, c, v))
    o, h, l, c, f = cache[symbol]
    n = len(c)
    nets, rs = [], []
    exits = {}

    for i in range(WARMUP, n - 1):
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue
        setup, direction = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
        conv = strategy.conviction(setup, direction, i, f, c)
        if selective_only and conv < strategy.SELECTIVE_THRESHOLD:
            continue

        entry = c[i] * (1 + direction * simulate.SLIPPAGE)
        stop, _, tstop, _, _, _ = strategy.levels(setup, direction, entry, i, f)
        dist = abs(entry - stop) * stop_scale
        stop = entry - direction * dist
        target = entry + direction * target_r * dist

        res = simulate.simulate(i, direction, entry, stop, target, tstop, o, h, l, c, n)
        if res and res["status"] == "CLOSED":
            nets.append(res["net_pct"])
            rs.append(res["r_multiple"])
            # Group the two gap variants with their parent reason.
            reason = res["exit_reason"].replace("_GAP", "")
            exits.setdefault(reason, []).append(res["net_pct"] * 100)

    nets = np.array(nets)
    rs = np.array(rs)
    wins = rs[rs > 0]
    gl = abs(rs[rs <= 0].sum())
    return {
        "n": len(nets),
        "win_pct": round(100 * len(wins) / len(rs), 1),
        # avg_R is the primary metric: this study risks a fixed $ per trade, so
        # P&L = R x risk and average R is proportional to expected profit.
        # avg_net_pct is retained for reference - it is the correct score only
        # under constant-NOTIONAL sizing, where widening a stop does not shrink
        # the position. The two disagree, and scoring on net % overstates the
        # value of widening a stop when risk is held constant.
        "avg_R": round(float(rs.mean()), 4),
        "avg_net_pct": round(float(nets.mean()) * 100, 4),
        "total_net_pct": round(float(nets.sum()) * 100, 1),
        "PF": round(float(wins.sum() / gl), 3) if gl > 0 else None,
        "exit_mix": {
            k: {"share_pct": round(100 * len(v) / len(nets), 1),
                "avg_net_pct": round(float(np.mean(v)), 3)}
            for k, v in sorted(exits.items())
        },
    }


def main():
    grid, mix = {}, {}
    for symbol in SYMBOLS:
        print("\n" + "=" * 100)
        print(f"{symbol}  selective book: avg R per trade (win rate in brackets)")
        print("=" * 100)
        print(f"{'stop x':<9}" + "".join(f"{'R=' + str(t):>13}" for t in TARGET_R))
        grid[symbol] = {}
        best = (None, -1e9)
        for s in STOP_SCALES:
            cells = []
            for t in TARGET_R:
                r = run(symbol, s, t)
                grid[symbol][f"{s}|{t}"] = r
                if r["avg_R"] > best[1]:
                    best = (f"stop x{s}, {t}R", r["avg_R"])
                cells.append(f"{r['avg_R']:+.3f} ({r['win_pct']:.0f}%)")
            print(f"{s:<9}" + "".join(f"{c:>13}" for c in cells))
        print(f"  best by avg R: {best[0]} at {best[1]:+.3f} R per trade")

        mix[symbol] = {}
        for s, t, tag in EXIT_MIX_CONFIGS:
            mix[symbol][tag] = {"stop_scale": s, "target_r": t,
                                **run(symbol, s, t)["exit_mix"]}

    with open(os.path.join(DATA, "sweep.json"), "w") as fh:
        json.dump(grid, fh, indent=2)
    with open(os.path.join(DATA, "exit_mix.json"), "w") as fh:
        json.dump(mix, fh, indent=2)
    print("\nwrote sweep.json, exit_mix.json")


if __name__ == "__main__":
    main()
