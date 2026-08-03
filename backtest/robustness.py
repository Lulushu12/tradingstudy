"""Two checks that separate guidance from curve-fitting.

1. Time-split stability. Halve the sample and re-run the statistics on each
   half independently. A rule that only works in one half is a description of
   that half, not an edge.
2. MAE distribution by outcome. How far does a trade that eventually wins go
   against you first? This is what actually tells you whether the stops are
   placed sensibly, or whether they are just wide enough to be right by luck.
"""

import csv
import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]


def load(symbol):
    out = []
    with open(os.path.join(DATA, f"{symbol}_trades.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["status"] != "CLOSED":
                continue
            r["r_multiple"] = float(r["r_multiple"])
            r["mae_r"] = float(r["mae_r"])
            r["mfe_r"] = float(r["mfe_r"])
            r["bar_index"] = int(r["bar_index"])
            r["conviction"] = float(r["conviction"])
            r["selective"] = r["selective"] == "True"
            out.append(r)
    return out


def brief(rows):
    if not rows:
        return {"n": 0}
    rs = np.array([r["r_multiple"] for r in rows])
    wins = rs[rs > 0]
    gl = abs(rs[rs <= 0].sum())
    return {
        "n": len(rs),
        "win_pct": round(100 * len(wins) / len(rs), 1),
        "avg_R": round(float(rs.mean()), 3),
        "total_R": round(float(rs.sum()), 1),
        "PF": round(float(wins.sum() / gl), 2) if gl > 0 else None,
    }


def main():
    out = {}
    for symbol in SYMBOLS:
        rows = load(symbol)
        mid = (min(r["bar_index"] for r in rows) + max(r["bar_index"] for r in rows)) // 2

        first = [r for r in rows if r["bar_index"] <= mid]
        second = [r for r in rows if r["bar_index"] > mid]

        print("\n" + "=" * 90)
        print(f"{symbol}  TIME-SPLIT STABILITY  (split at bar {mid})")
        print("=" * 90)
        print(f"{'book':<34}{'half':<8}{'n':>7}{'win%':>7}{'avgR':>8}{'totR':>9}{'PF':>7}")
        for name, sel_only in (("always-on (every close)", False), ("selective (conv>=6)", True)):
            for label, half in (("H1", first), ("H2", second)):
                rs = [r for r in half if (r["selective"] or not sel_only)]
                b = brief(rs)
                pf = b.get("PF") or 0.0
                print(f"{name:<34}{label:<8}{b['n']:>7}{b['win_pct']:>7}{b['avg_R']:>8.3f}{b['total_R']:>9.1f}{pf:>7.2f}")

        # The setup x direction combos, checked in both halves.
        print(f"\n  {'combo':<30}{'H1 n':>7}{'H1 avgR':>10}{'H2 n':>7}{'H2 avgR':>10}{'stable?':>10}")
        combos = defaultdict(lambda: {"H1": [], "H2": []})
        for r in rows:
            if not r["selective"]:
                continue
            combos[f"{r['setup']}/{r['direction']}"]["H1" if r["bar_index"] <= mid else "H2"].append(r)
        combo_out = {}
        for k in sorted(combos):
            a, b = brief(combos[k]["H1"]), brief(combos[k]["H2"])
            if a["n"] < 15 or b["n"] < 15:
                continue
            stable = "yes" if (a["avg_R"] > 0) == (b["avg_R"] > 0) else "NO"
            print(f"  {k:<30}{a['n']:>7}{a['avg_R']:>10.3f}{b['n']:>7}{b['avg_R']:>10.3f}{stable:>10}")
            combo_out[k] = {"H1": a, "H2": b, "sign_stable": stable == "yes"}

        # MAE: how far do eventual winners go against you first?
        winners = [r["mae_r"] for r in rows if r["r_multiple"] > 0]
        losers = [r["mae_r"] for r in rows if r["r_multiple"] <= 0]
        wq = np.percentile(winners, [50, 75, 90, 95, 99])
        print(f"\n  MAE of eventual WINNERS (R against you before it worked):")
        print(f"    median {wq[0]:.2f}   p75 {wq[1]:.2f}   p90 {wq[2]:.2f}   p95 {wq[3]:.2f}   p99 {wq[4]:.2f}")
        print(f"    share of winners that never went beyond 0.50R against: "
              f"{100 * np.mean(np.array(winners) <= 0.5):.1f}%")
        print(f"    share of winners that never went beyond 0.75R against: "
              f"{100 * np.mean(np.array(winners) <= 0.75):.1f}%")
        print(f"  MAE of losers: median {np.median(losers):.2f}")

        out[symbol] = {
            "split_bar": mid,
            "always_on": {"H1": brief(first), "H2": brief(second)},
            "selective": {
                "H1": brief([r for r in first if r["selective"]]),
                "H2": brief([r for r in second if r["selective"]]),
            },
            "combo_stability": combo_out,
            "winner_mae": {
                "median": round(float(wq[0]), 3),
                "p75": round(float(wq[1]), 3),
                "p90": round(float(wq[2]), 3),
                "p95": round(float(wq[3]), 3),
                "p99": round(float(wq[4]), 3),
                "pct_within_0_50R": round(float(100 * np.mean(np.array(winners) <= 0.5)), 1),
                "pct_within_0_75R": round(float(100 * np.mean(np.array(winners) <= 0.75)), 1),
            },
        }

    with open(os.path.join(DATA, "robustness.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\nwrote robustness.json")


if __name__ == "__main__":
    main()
