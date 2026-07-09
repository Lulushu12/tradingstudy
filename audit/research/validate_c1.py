"""ONE-SHOT validation of C1 (funding extreme fade) per RESEARCH_PROTOCOL.md.
Rule identical to sandbox. Segment: 2024-01-01 .. 2026-06-21. Pass bar:
net expectancy >= +0.10R on >= 100 trades, majority of half-year windows
nonnegative, one-sided t-stat clearing Bonferroni x5 (p < 0.01), then the
venue survivability bootstrap. This script runs once; the verdict stands.
"""
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(HERE))          # audit/ for phase1
from sandbox import load_bars, simulate, c1_funding, half_label
from phase1 import k5_bootstrap

VAL_START = pd.Timestamp("2024-01-01", tz="UTC")
VAL_END = pd.Timestamp("2026-06-22", tz="UTC")


def main():
    df = load_bars()
    sigs = c1_funding(df)
    dts = df["dt"]
    val_sigs = [s for s in sigs
                if s[0] + 1 < len(df) and VAL_START <= dts.iloc[s[0] + 1] < VAL_END]
    trades, skipped = simulate(val_sigs, df)
    rs = np.array([t["net_r"] for t in trades])
    n = len(rs)
    se = rs.std(ddof=1) / np.sqrt(n)
    tstat = rs.mean() / se
    p_one = 1 - sps.t.cdf(tstat, df=n - 1)
    by_w = defaultdict(list)
    for t in trades:
        by_w[half_label(t["t_entry"])].append(t["net_r"])
    neg = sum(np.mean(v) < 0 for v in by_w.values())
    gp = rs[rs > 0].sum()
    gl = -rs[rs < 0].sum()

    print(f"C1 VALIDATION (one shot): trades={n} skipped={skipped}")
    print(f"expectancy={rs.mean():+.4f}R  SE={se:.4f}  t={tstat:.2f}  "
          f"one-sided p={p_one:.4f} (Bonferroni x5 bar: p<0.01)")
    print(f"win={np.mean(rs > 0):.1%}  PF={gp / gl if gl else float('inf'):.3f}")
    for w in sorted(by_w):
        v = np.array(by_w[w])
        print(f"  {w}: n={len(v):3d} exp={v.mean():+.4f}R")
    span_years = (VAL_END - VAL_START).days / 365.25
    checks = {
        "expectancy >= +0.10R": rs.mean() >= 0.10,
        "trades >= 100": n >= 100,
        "windows nonneg majority": neg <= len(by_w) / 2,
        "Bonferroni x5 (p < 0.01)": p_one < 0.01,
    }
    for k, v in checks.items():
        print(f"  {k}: {'yes' if v else 'NO'}")
    if all(checks.values()):
        pb = k5_bootstrap(trades, n / span_years)
        print(f"venue survivability: P(breach Classic in 1y) = {pb:.1%} "
              f"(bar: <= 50%; closed-trade approx, optimistic)")
        print(f"VERDICT: {'SURVIVES VALIDATION' if pb <= 0.5 else 'DEAD AT VENUE'}")
    else:
        print("VERDICT: DEAD")
    pd.DataFrame(trades).to_csv(os.path.join(HERE, "validation_C1.csv"), index=False)


if __name__ == "__main__":
    main()
