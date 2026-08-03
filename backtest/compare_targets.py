"""Fixed-R targets vs structure-derived targets, on identical entry signals.

Only the take-profit changes between the two runs. Entries, stops, time stops
and cost assumptions are byte-for-byte the same, so any difference is
attributable to the targeting method alone.
"""

import json
import os

import numpy as np

import indicators
import simulate
import strategy
from run_backtest import load, WARMUP

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]


def run(symbol, target_mode, cache={}):
    if symbol not in cache:
        ts, o, h, l, c, v = load(symbol)
        cache[symbol] = (o, h, l, c, indicators.build(o, h, l, c, v),
                         indicators.pivot_lists(h, l))
    o, h, l, c, f, piv = cache[symbol]
    n = len(c)
    out = {"all": [], "sel": []}
    rr_used, basis = [], {}

    for i in range(WARMUP, n - 1):
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue
        setup, direction = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
        conv = strategy.conviction(setup, direction, i, f, c)
        entry = c[i] * (1 + direction * simulate.SLIPPAGE)
        stop, target, tstop, _, r_mult, tnote = strategy.levels(
            setup, direction, entry, i, f, piv, target_mode
        )
        res = simulate.simulate(i, direction, entry, stop, target, tstop, o, h, l, c, n)
        if not res or res["status"] != "CLOSED":
            continue
        rec = (res["r_multiple"], res["net_pct"], res["exit_reason"])
        out["all"].append(rec)
        if conv >= strategy.SELECTIVE_THRESHOLD:
            out["sel"].append(rec)
        rr_used.append(r_mult)
        key = "structure level" if tnote.startswith("swing") else (
            "6R cap" if "cap" in tnote else ("fixed-R fallback" if "fallback" in tnote else "fixed R"))
        basis[key] = basis.get(key, 0) + 1

    stats = {}
    for book in ("all", "sel"):
        rs = np.array([x[0] for x in out[book]])
        nets = np.array([x[1] for x in out[book]])
        wins = rs[rs > 0]
        gl = abs(rs[rs <= 0].sum())
        hits = sum(1 for x in out[book] if x[2].startswith("TARGET"))
        stats[book] = {
            "n": len(rs),
            "win_pct": round(100 * len(wins) / len(rs), 1),
            "avg_R": round(float(rs.mean()), 4),
            "total_R": round(float(rs.sum()), 1),
            "PF": round(float(wins.sum() / gl), 3) if gl > 0 else None,
            "avg_net_pct": round(float(nets.mean()) * 100, 4),
            "target_hit_pct": round(100 * hits / len(rs), 1),
        }
    stats["planned_rr"] = {
        "distinct_values": len(set(np.round(rr_used, 2))),
        "min": round(float(np.min(rr_used)), 2),
        "median": round(float(np.median(rr_used)), 2),
        "max": round(float(np.max(rr_used)), 2),
    }
    stats["target_basis"] = basis
    return stats


def main():
    report = {}
    for symbol in SYMBOLS:
        report[symbol] = {}
        print("\n" + "=" * 104)
        print(symbol)
        print("=" * 104)
        print(f"{'targeting':<14}{'book':<12}{'n':>7}{'win%':>7}{'avgR':>9}{'totR':>10}"
              f"{'PF':>7}{'net%/trade':>12}{'TP hit%':>9}{'distinct R:R':>14}")
        for mode, label in (("fixed_r", "fixed R"), ("structure", "structure")):
            s = run(symbol, mode)
            report[symbol][mode] = s
            for book, bl in (("all", "all trades"), ("sel", "selective")):
                b = s[book]
                print(f"{label:<14}{bl:<12}{b['n']:>7}{b['win_pct']:>7}{b['avg_R']:>9.3f}"
                      f"{b['total_R']:>10.1f}{(b['PF'] or 0):>7.2f}{b['avg_net_pct']:>12.4f}"
                      f"{b['target_hit_pct']:>9.1f}{s['planned_rr']['distinct_values']:>14}")
        st = report[symbol]["structure"]
        print(f"  structure R:R range: {st['planned_rr']['min']}R to {st['planned_rr']['max']}R, "
              f"median {st['planned_rr']['median']}R")
        print(f"  target basis: {st['target_basis']}")

        for book in ("all", "sel"):
            a = report[symbol]["fixed_r"][book]["avg_R"]
            b = report[symbol]["structure"][book]["avg_R"]
            verdict = "structure better" if b > a else "fixed R better"
            print(f"  {book:<10} {a:+.4f} -> {b:+.4f} R   ({verdict}, delta {b - a:+.4f})")

    with open(os.path.join(DATA, "target_comparison.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print("\nwrote target_comparison.json")


if __name__ == "__main__":
    main()
