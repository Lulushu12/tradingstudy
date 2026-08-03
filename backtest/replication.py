"""Cross-dataset replication: does anything survive outside the window it was found in?

Three datasets, all 10,000 bars x 3 symbols:
  1h        2025-06-12 -> 2026-08-03   the window every rule in this study was derived from
  1h_prior  2024-04-22 -> 2025-06-12   strictly disjoint, genuinely out of sample
  15m       2026-04-21 -> 2026-08-03   different timeframe, overlaps the tail of the main window

A rule discovered in the main window is only worth anything if it holds in
1h_prior, which no part of the derivation ever saw.
"""

import json
import os

import numpy as np

import strategy
from system_v2 import SYMBOLS, build, summarize, bootstrap

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

DATASETS = [
    ("1h", "MAIN 1h (in-sample)", 168),
    ("1h_prior", "PRIOR 1h (OUT-of-sample)", 168),
    ("15m", "15m (different timeframe)", 672),
]

CONFIGS = [
    ("v1 selective (conv >= 6)", lambda st, cv: cv >= 6.0, 1.0, None),
    ("drop RANGE_FADE only", lambda st, cv: cv >= 6.0 and st != "RANGE_FADE", 1.0, None),
    ("v1 6-8 band", lambda st, cv: 6.0 <= cv < 8.0, 1.0, None),
    ("v2 (6-8 + no RANGE_FADE)", strategy.qualifies_v2, 1.0, None),
    ("v2b (+ x1.6 / 4R geometry)", strategy.qualifies_v2, 1.6, 4.0),
]

CUTS = [
    ("CUT conviction 8-10", lambda st, cv: cv >= 8.0, 1.0, None),
    ("CUT RANGE_FADE (6-8)", lambda st, cv: st == "RANGE_FADE" and 6.0 <= cv < 8.0, 1.0, None),
    ("CUT RANGE_FADE (all >=6)", lambda st, cv: st == "RANGE_FADE" and cv >= 6.0, 1.0, None),
]


def evaluate(suffix, rule, scale, tr, block):
    rows = []
    for s in SYMBOLS:
        rows += build(s, suffix, rule, scale, tr)
    if not rows:
        return None
    return {**summarize(rows), **bootstrap(rows, block)}


def matrix(title, configs, note):
    print("\n" + "=" * 116)
    print(title)
    print("=" * 116)
    print(note)
    head = f"{'configuration':<30}"
    for _, label, _ in DATASETS:
        head += f"{label:>28}"
    print(head)
    print(f"{'':<30}" + "".join(f"{'n    avgR      P(>0)':>28}" for _ in DATASETS))

    results = {}
    for name, rule, scale, tr in configs:
        cells = ""
        results[name] = {}
        for suffix, _, block in DATASETS:
            d = evaluate(suffix, rule, scale, tr, block)
            results[name][suffix] = d
            if not d:
                cells += f"{'-':>28}"
                continue
            mark = "*" if (d["lo"] > 0 or d["hi"] < 0) else " "
            cells += f"{d['n']:>6}{d['avg']:>+9.3f}{d['p_pos']:>9.1f}%{mark:>3}"
        print(f"{name:<30}{cells}")
    print("  * = 95% bootstrap interval excludes zero")
    return results


def main():
    books = matrix(
        "DO THE BOOKS REPLICATE?", CONFIGS,
        "Every rule below was derived from the MAIN window. PRIOR is the honest test.\n")

    cuts = matrix(
        "DO THE CUTS REPLICATE?", CUTS,
        "These are the trades v2 REMOVES. For a cut to be justified they must be negative\n"
        "in every dataset, not just the one that motivated the cut.\n")

    print("\n" + "=" * 116)
    print("BREAKEVEN vs ACHIEVED WIN RATE - the structural test for RANGE_FADE")
    print("=" * 116)
    print(f"{'dataset':<30}{'n':>7}{'win %':>10}{'breakeven %':>14}{'gap':>10}{'verdict':>26}")
    for suffix, label, block in DATASETS:
        d = cuts["CUT RANGE_FADE (all >=6)"][suffix]
        if not d:
            continue
        gap = d["win"] - d["be"]
        verdict = "cannot pay for itself" if gap < 0 else "viable in principle"
        print(f"{label:<30}{d['n']:>7}{d['win']:>10.1f}{d['be']:>14.1f}{gap:>+10.1f}{verdict:>26}")

    with open(os.path.join(DATA, "replication.json"), "w") as fh:
        json.dump({"books": books, "cuts": cuts}, fh, indent=2, default=float)
    print("\nwrote replication.json")


if __name__ == "__main__":
    main()
