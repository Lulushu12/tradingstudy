"""Follow-up: resolve the 'breakeven at zero edge' result and price the honest edge.

Two things the first pass left open.

1. Why is breakeven at ~0.00R rather than something demanding? Because R here is
   already NET of fees and slippage. 'Zero net expectancy' is not 'no skill' - a
   no-skill trader has NEGATIVE net expectancy equal to the cost drag. The right
   null for someone with no edge is the unconditional expectancy of the trade
   template, not zero. Priced explicitly below.

2. What edge should actually be assumed? +0.1426R is the studied-data figure and
   the holdout came in at -0.6135R. Combining both by inverse variance gives the
   honest posterior, which is what the decision should be priced on.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import payout as P       # noqa: E402


def posterior():
    """Inverse-variance blend of studied-data and holdout estimates."""
    mu1, se1, n1 = 0.1426, 0.0531, 3391      # se from the block-bootstrap CI width
    mu2, se2, n2 = -0.6135, 0.1230, 52       # holdout
    w1, w2 = 1 / se1 ** 2, 1 / se2 ** 2
    mu = (w1 * mu1 + w2 * mu2) / (w1 + w2)
    se = (1 / (w1 + w2)) ** 0.5
    return mu, se, (mu - 1.96 * se, mu + 1.96 * se)


def main():
    dc = P.empirical_daily_counts()
    FEE, SPLIT = 800.0, 0.80

    print("=" * 88)
    print("1. What is the correct null? R is already net of costs.")
    print("=" * 88)
    print("Unconditional 4h/2xATR/2:1 expectancy, i.e. a coin-flip trader paying")
    print("the same costs, measured earlier:")
    print("   TRAIN  -0.0148R      TEST  +0.0112R      HOLDOUT  -0.2860R")
    print("\nSo a no-skill trader sits near -0.015R, not 0.000R. Pricing that:")
    print(f"\n{'true expR':>11}{'P(funded)':>11}{'P(paid)':>9}{'mean $':>10}"
          f"{'EV $':>9}{'ROI':>8}   interpretation")
    cases = [
        (-0.2860, "holdout-regime coin flipper"),
        (-0.0500, "no skill, poor conditions"),
        (-0.0148, "no skill, TRAIN-average conditions"),
        (0.0000, "exactly covers costs"),
        (0.0244, "POSTERIOR (studied data + holdout)"),
        (0.0500, "half the lower CI bound"),
        (0.1426, "studied-data point estimate"),
    ]
    for mu, lbl in cases:
        r = P.simulate(mu, n_paths=30000, daily_counts=dc, fee=FEE, split=SPLIT,
                       w=0.02, keep=0.0, risk=0.0025, seed=21)
        if r is None:
            print(f"{mu:>11.4f}  degenerate  -> certain loss of fee            {lbl}")
            continue
        print(f"{mu:>11.4f}{100*r['p_funded']:>10.1f}%{100*r['p_pass']:>8.1f}%"
              f"{r['mean_banked']:>10.0f}{r['ev']:>9.0f}{r['roi']:>+8.2f}   {lbl}")

    mu, se, ci = posterior()
    print("\n" + "=" * 88)
    print("2. The honest edge estimate")
    print("=" * 88)
    print(f"studied data : +0.1426R  (n=3391, bootstrap SE ~0.053)")
    print(f"holdout      : -0.6135R  (n=52,   SE ~0.123)")
    print(f"inverse-variance posterior: {mu:+.4f}R  SE {se:.4f}  "
          f"95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    print("\nCaveat that matters more than the arithmetic: this blend assumes one")
    print("stationary edge. The per-year table (+0.23, +0.22, +0.01, +0.08, +0.09,")
    print("+0.37) says the edge is regime-conditional, so the forward value depends")
    print("on the future regime mix, which is not estimable from this data.")

    print("\n" + "=" * 88)
    print("3. EV across the posterior CI, at the frozen 0.25% risk")
    print("=" * 88)
    print(f"{'expR':>9}{'P(funded)':>11}{'P(paid)':>9}{'mean $':>10}{'EV $':>9}"
          f"{'P(lose fee)':>13}")
    for m in [ci[0], -0.05, 0.0, mu, 0.05, ci[1], 0.10]:
        r = P.simulate(m, n_paths=30000, daily_counts=dc, fee=FEE, split=SPLIT,
                       w=0.02, keep=0.0, risk=0.0025, seed=23)
        if r is None:
            print(f"{m:>9.4f}   degenerate -> certain loss")
            continue
        print(f"{m:>9.4f}{100*r['p_funded']:>10.1f}%{100*r['p_pass']:>8.1f}%"
              f"{r['mean_banked']:>10.0f}{r['ev']:>9.0f}"
              f"{100*(1-r['p_profit']):>12.1f}%")

    print("\n" + "=" * 88)
    print("4. Withdrawal policy at the POSTERIOR edge (not the optimistic one)")
    print("=" * 88)
    print(f"{'withdraw at':>12}{'keep':>7}{'P(paid)':>9}{'payouts':>9}"
          f"{'mean $':>10}{'EV $':>9}")
    for w in [0.02, 0.05, 0.10, 0.20]:
        for keep in [0.0, 0.05]:
            if keep >= w:
                continue
            r = P.simulate(mu, n_paths=30000, daily_counts=dc, fee=FEE,
                           split=SPLIT, w=w, keep=keep, risk=0.0025, seed=25)
            print(f"{100*w:>11.0f}%{100*keep:>6.0f}%{100*r['p_pass']:>8.1f}%"
                  f"{r['mean_payouts']:>9.2f}{r['mean_banked']:>10.0f}"
                  f"{r['ev']:>9.0f}")

    print("\n" + "=" * 88)
    print("5. Account size: fee scales, edge does not")
    print("=" * 88)
    print(f"{'size':>9}{'fee':>7}{'EV @posterior':>15}{'EV @+0.1426R':>14}"
          f"{'EV @-0.015R':>13}")
    for size, fee in [(5_000, 45), (25_000, 250), (50_000, 450), (100_000, 800)]:
        out = []
        for m in (mu, 0.1426, -0.0148):
            r = P.simulate(m, n_paths=20000, daily_counts=dc, A=float(size),
                           fee=float(fee), split=SPLIT, w=0.02, keep=0.0,
                           risk=0.0025, seed=27)
            out.append(r["ev"] if r else -fee)
        print(f"{size:>9,}{fee:>7}{out[0]:>15.0f}{out[1]:>14.0f}{out[2]:>13.0f}")


if __name__ == "__main__":
    main()
