#!/usr/bin/env python3
"""What risk per trade actually survives a Breakout evaluation.

Stdlib only. Monte Carlo over the real constraint: reach the profit target before
touching the static drawdown floor.

    python3 prop_math.py
    python3 prop_math.py --target 10 --dd 6 --daily 3
    python3 prop_math.py --wr 0.42 --sims 50000

Model:
  - Each trade wins +R_win (default 2R) with probability wr, else loses -1R.
  - Fee drag is applied in R, derived from the stop distance as a percent of price,
    so a tighter stop is correctly penalised more.
  - Risk is a fixed percent of CURRENT equity (compounding, as the spec sizes it).
  - The drawdown floor is STATIC: fixed at start * (1 - dd/100), per Breakout's
    1-Step Classic rules. It does not trail up as equity rises.
  - A daily loss cap is applied by limiting consecutive losses per day, matching the
    Layer 6 rule of two losses then stop.

Everything here assumes the backtested win rate is real. It is a planning tool for
sizing, not a prediction. The output that matters is the SHAPE: how P(pass) and
P(bust) move as risk changes.
"""

import argparse
import random
import statistics


def simulate(wr, r_win, risk_pct, target_pct, dd_pct, fee_r, max_trades,
             losses_per_day, sims, seed=11):
    rng = random.Random(seed)
    passes = busts = stalls = 0
    trades_to_pass = []
    for _ in range(sims):
        start = 100.0
        equity = start
        floor = start * (1 - dd_pct / 100.0)
        goal = start * (1 + target_pct / 100.0)
        day_losses = 0
        for n in range(1, max_trades + 1):
            risk = equity * risk_pct / 100.0
            if rng.random() < wr:
                equity += risk * (r_win - fee_r)
                day_losses = 0
            else:
                equity -= risk * (1.0 + fee_r)
                day_losses += 1
                if day_losses >= losses_per_day:
                    day_losses = 0  # stop for the day, resume tomorrow
            if equity <= floor:
                busts += 1
                break
            if equity >= goal:
                passes += 1
                trades_to_pass.append(n)
                break
        else:
            stalls += 1
    return {
        "pass": passes / sims,
        "bust": busts / sims,
        "stall": stalls / sims,
        "median_trades": statistics.median(trades_to_pass) if trades_to_pass else None,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--target", type=float, default=10.0, help="profit target %%")
    p.add_argument("--dd", type=float, default=6.0, help="static max drawdown %%")
    p.add_argument("--daily", type=float, default=3.0, help="daily loss limit %% (reported only)")
    p.add_argument("--wr", type=float, default=None, help="single win rate to test")
    p.add_argument("--rwin", type=float, default=2.0, help="R multiple on a win")
    p.add_argument("--stop-pct", type=float, default=1.5,
                   help="typical stop distance as %% of price, used for fee drag")
    p.add_argument("--fee", type=float, default=0.08, help="round-trip fee %%")
    p.add_argument("--losses-per-day", type=int, default=2)
    p.add_argument("--max-trades", type=int, default=600)
    p.add_argument("--sims", type=int, default=20000)
    args = p.parse_args()

    fee_r = args.fee / args.stop_pct
    win_rates = [args.wr] if args.wr else [0.38, 0.42, 0.46]
    risks = [0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00]

    print("")
    print("=" * 78)
    print("PROP EVALUATION MATH")
    print("=" * 78)
    print("target +%.1f%%   static DD floor -%.1f%%   daily cap %.1f%% (%d losses/day rule)"
          % (args.target, args.dd, args.daily, args.losses_per_day))
    print("win pays %.1fR   fee %.2f%% round trip on a %.2f%% stop = %.3fR drag per trade"
          % (args.rwin, args.fee, args.stop_pct, fee_r))
    for wr in win_rates:
        exp = wr * (args.rwin - fee_r) - (1 - wr) * (1 + fee_r)
        print("  wr %.0f%% -> net expectancy %+.3fR per trade" % (wr * 100, exp))
    print("%d simulations per cell, sizing compounds on current equity." % args.sims)
    print("")

    header = "risk/trade  " + "".join("   wr %.0f%%%s" % (wr * 100, " " * 14) for wr in win_rates)
    print(header)
    print("            " + "".join("   P(pass) P(bust) median n " for _ in win_rates))
    print("-" * (12 + 29 * len(win_rates)))
    for risk in risks:
        row = "%9.2f%%  " % risk
        for wr in win_rates:
            r = simulate(wr, args.rwin, risk, args.target, args.dd, fee_r,
                         args.max_trades, args.losses_per_day, args.sims)
            med = "%6s" % (int(r["median_trades"]) if r["median_trades"] else "-")
            row += "    %5.1f%%  %5.1f%%  %s   " % (r["pass"] * 100, r["bust"] * 100, med)
        print(row)
    print("-" * (12 + 29 * len(win_rates)))
    print("")
    print("P(pass) + P(bust) may not reach 100%%: the remainder ran past the %d-trade cap"
          % args.max_trades)
    print("without resolving either way.")
    print("")
    print("Reading this: a static floor means the buffer is fixed in DOLLARS at the start,")
    print("so early losses are far more dangerous than late ones. Smaller risk buys a")
    print("higher pass rate at the cost of taking many more trades to get there.")
    print("")


if __name__ == "__main__":
    main()
