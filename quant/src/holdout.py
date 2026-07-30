"""FINAL HOLDOUT TEST. Run exactly once, after SYSTEM_FROZEN.md was written.

Unseals 2026-06-22 .. 2026-07-29 across all five assets and applies the frozen
rule with no modification.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import account as A       # noqa: E402
import candidate as C     # noqa: E402
import labels as L        # noqa: E402

UNLOCK = "I_AM_RUNNING_THE_FINAL_HOLDOUT_TEST"


def main():
    print("=" * 68)
    print("FINAL HOLDOUT — 2026-06-22 .. 2026-07-29, frozen rule, no changes")
    print("=" * 68)

    T = A.build_trades("vol_spike_cont", block="HOLDOUT", unlock=UNLOCK)
    print(f"\ntrades: {len(T)}   span {T.entry_dt.min()} -> {T.entry_dt.max()}")

    mu, lo, hi = L.block_bootstrap(T.r.values, n_boot=3000, block=8)
    print(f"\npooled net expectancy  {T.r.mean():+.4f}R   "
          f"95% CI [{lo:+.4f}, {hi:+.4f}]")
    print(f"win rate {float((T.outcome==1).mean()):.3f}   "
          f"stops {float((T.outcome==-1).mean()):.3f}   "
          f"time-stopped {float((T.outcome==0).mean()):.3f}")
    print(f"sum R {T.r.sum():+.2f}")

    print(f"\n{'symbol':>10}{'n':>6}{'expR':>10}{'sumR':>9}")
    for s, g in T.groupby("symbol"):
        print(f"{s:>10}{len(g):>6}{g.r.mean():>10.3f}{g.r.sum():>9.2f}")

    print("\n--- account simulation at the frozen settings (0.25% risk, 2% heat) ---")
    starts = pd.date_range(T.entry_dt.min(),
                           T.entry_dt.max() - pd.Timedelta(days=20),
                           freq="1D", tz="UTC")
    res = [A.run_account(T, s, 30, 0.0025, 0.02) for s in starts]
    oc = pd.Series([r[0] for r in res])
    rt = pd.Series([r[1] for r in res])
    print(f"accounts: {len(res)}   pass {100*float((oc=='pass').mean()):.1f}%   "
          f"bust {100*float(oc.str.startswith('bust').mean()):.1f}%   "
          f"mean ret {100*rt.mean():+.2f}%")

    # single account over the whole holdout
    import engine as E
    stats, curve = E.simulate(T, risk_pct=0.0025, max_concurrent=8)
    print(f"\nsingle account over full holdout: n={stats['n']}  "
          f"total {100*stats['total_ret']:+.2f}%  maxDD {100*stats['max_dd']:.2f}%  "
          f"breach={stats['breached']}")

    verdict = "PASS (not falsified)" if T.r.mean() > 0 else "FAIL"
    print(f"\n>>> PRE-REGISTERED VERDICT: {verdict}")
    print("    Criterion was: pooled net expectancy > 0.")
    print(f"    Standard error on {len(T)} trades is ~{T.r.std(ddof=0)/np.sqrt(len(T)):.3f}R, "
          "so this test is weak by construction.")


if __name__ == "__main__":
    main()
