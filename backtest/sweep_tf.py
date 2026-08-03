"""Stop-width x target sweep, scored under BOTH sizing conventions.

    python3 sweep_tf.py 15m 6-8

Why two metrics:

  avg R      - correct under constant RISK sizing (a fixed $ risked per trade,
               which is what this study assumes). Position size shrinks as the
               stop widens, and P&L = R x risk_$, so avg R is proportional to
               expected profit.
  avg net %  - correct under constant NOTIONAL sizing (same position size
               regardless of stop). A wider stop then means you simply hold
               through more noise and capture a bigger move.

The original sweep scored only net %, which understates the cost of widening a
stop when risk is held constant. Both are reported here so the two conventions
cannot be confused.
"""

import json
import os
import sys

import numpy as np

import indicators
import run_backtest
import simulate
import strategy

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

STOP_SCALES = [1.0, 1.3, 1.6, 2.0, 2.5, 3.0]
TARGET_R = [1.5, 2.0, 2.5, 3.0, 4.0]

_cache = {}


def prep(symbol, suffix):
    key = (symbol, suffix)
    if key not in _cache:
        run_backtest.SUFFIX = suffix
        ts, o, h, l, c, v = run_backtest.load(symbol)
        _cache[key] = (o, h, l, c, indicators.build(o, h, l, c, v))
    return _cache[key]


def run(symbol, suffix, stop_scale, target_r, lo, hi):
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    rs, nets, costs = [], [], []

    for i in range(run_backtest.WARMUP, n - 1):
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue
        setup, direction = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
        conv = strategy.conviction(setup, direction, i, f, c)
        if not (lo <= conv < hi):
            continue

        entry = c[i] * (1 + direction * simulate.SLIPPAGE)
        stop, _, tstop, _, _, _ = strategy.levels(setup, direction, entry, i, f)
        dist = abs(entry - stop) * stop_scale
        stop = entry - direction * dist
        target = entry + direction * target_r * dist

        res = simulate.simulate(i, direction, entry, stop, target, tstop, o, h, l, c, n)
        if res and res["status"] == "CLOSED":
            rs.append(res["r_multiple"])
            nets.append(res["net_pct"])
            costs.append(res["cost_pct"] / (dist / entry))

    if not rs:
        return None
    rs = np.array(rs)
    w = rs[rs > 0]
    gl = abs(rs[rs <= 0].sum())
    return {
        "n": len(rs),
        "win_pct": round(100 * len(w) / len(rs), 1),
        "avg_R": round(float(rs.mean()), 4),
        "avg_net_pct": round(float(np.mean(nets)) * 100, 4),
        "PF": round(float(w.sum() / gl), 3) if gl > 0 else None,
        "cost_share_pct": round(float(np.mean(costs)) * 100, 1),
    }


def grid(suffix, lo, hi, label):
    out = {}
    for symbol in SYMBOLS:
        print("\n" + "=" * 96)
        print(f"{symbol}  {suffix}  conviction {label}")
        print("=" * 96)
        out[symbol] = {}

        for metric, key, fmt in (("AVG R  (constant-risk sizing - the one that matters here)", "avg_R", "+.3f"),
                                 ("AVG NET %  (constant-notional sizing)", "avg_net_pct", "+.3f")):
            print(f"\n  {metric}")
            print(f"  {'stop x':<9}" + "".join(f"{'R=' + str(t):>13}" for t in TARGET_R))
            for s in STOP_SCALES:
                cells = []
                for t in TARGET_R:
                    r = out[symbol].get(f"{s}|{t}")
                    if r is None:
                        r = run(symbol, suffix, s, t, lo, hi)
                        out[symbol][f"{s}|{t}"] = r
                    cells.append("n/a" if not r else format(r[key], fmt))
                print(f"  {s:<9}" + "".join(f"{c:>13}" for c in cells))

        base = out[symbol]["1.0|2.5"]
        print(f"\n  friction as share of 1R:  stop x1.0 -> {base['cost_share_pct']}%   "
              f"x2.0 -> {out[symbol]['2.0|2.5']['cost_share_pct']}%   "
              f"x3.0 -> {out[symbol]['3.0|2.5']['cost_share_pct']}%")
        best_r = max((v for v in out[symbol].values() if v), key=lambda d: d["avg_R"])
        best_p = max((v for v in out[symbol].values() if v), key=lambda d: d["avg_net_pct"])
        kr = [k for k, v in out[symbol].items() if v is best_r][0]
        kp = [k for k, v in out[symbol].items() if v is best_p][0]
        print(f"  best by avg R:     stop x{kr.split('|')[0]}, {kr.split('|')[1]}R  "
              f"-> {best_r['avg_R']:+.3f} R  (win {best_r['win_pct']}%, PF {best_r['PF']})")
        print(f"  best by avg net %: stop x{kp.split('|')[0]}, {kp.split('|')[1]}R  "
              f"-> {best_p['avg_net_pct']:+.3f}%  (avg R there: {best_p['avg_R']:+.3f})")
    return out


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else "15m"
    band = sys.argv[2] if len(sys.argv) > 2 else "6-8"
    lo, hi = (6.0, 8.0) if band == "6-8" else (6.0, 10.001)

    res = grid(suffix, lo, hi, band)
    with open(os.path.join(DATA, f"sweep_{suffix}_{band}.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote sweep_{suffix}_{band}.json")


if __name__ == "__main__":
    main()
