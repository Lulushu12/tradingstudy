"""Prop-firm economics: is buying a Breakout evaluation a positive-EV purchase?

This is a different question from '10% a month' and it has a different answer,
because the payoff is asymmetric: downside is capped at the evaluation fee,
upside is an uncapped share of profits on someone else's capital.

Contract terms modelled (Breakout 1-Step Classic, verified 2026-07-30):
  - evaluation: +10% target, 6% static floor anchored to starting balance,
    3% daily loss vs previous day's closing balance
  - passing yields a FUNDED account that starts fresh at the original size,
    floor again 6% below it, no profit target
  - the floor never trails, so withdrawing profit is precisely what re-exposes
    the account: cushion = balance - floor, and a payout shrinks it back
  - evaluation fee is refunded in full with the FIRST funded payout
  - 80% profit split (90% purchasable, 95% after 3 months + 2 payouts)
  - a busted account is gone; there is no reset, only a new purchase

The true per-trade expectancy is NOT known. The measured +0.1426R failed its
holdout. So EV is reported as a FUNCTION of true expectancy, and the headline
output is the breakeven edge at which this purchase stops losing money.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Empirical outcome classes from vol_spike_cont (n=3391), used to keep the R
# distribution realistic while expectancy is varied via the win probability.
R_WIN, SD_WIN = 1.942, 0.114
R_LOSS, SD_LOSS = -1.023, 0.011
R_TIME, SD_TIME = 0.290, 0.560
P_TIME = 0.094


def win_prob(mu):
    """Win probability that yields target expectancy mu, timeouts held fixed."""
    return (mu - P_TIME * R_TIME - (1 - P_TIME) * R_LOSS) / (R_WIN - R_LOSS)


def simulate(mu, n_paths=20000, risk=0.0025, A=100_000.0, fee=800.0,
             split=0.80, months=24, daily_counts=None, w=0.05, keep=0.0,
             floor_frac=0.06, daily_frac=0.03, target=0.10, seed=0,
             refund_fee=True):
    """Vectorised Monte Carlo over full account lifecycles.

    w    : withdraw once funded balance >= A*(1+w)
    keep : after withdrawing, leave A*(1+keep) in the account (0 = bank it all)
    """
    rng = np.random.default_rng(seed)
    pw = win_prob(mu)
    pl = 1 - P_TIME - pw
    if pw <= 0 or pl <= 0:
        return None

    days = int(months * 30.44)
    if daily_counts is None:
        daily_counts = np.array([1])
    kmax = int(daily_counts.max())

    eq = np.full(n_paths, A)
    state = np.zeros(n_paths, dtype=np.int8)      # 0 eval, 1 funded, 2 dead
    floor = A * (1 - floor_frac)
    banked = np.zeros(n_paths)                    # trader's realised cash
    n_pay = np.zeros(n_paths, dtype=np.int32)
    days_to_pass = np.full(n_paths, -1)

    for d in range(days):
        alive = state < 2
        if not alive.any():
            break
        day_start = eq.copy()
        k = rng.choice(daily_counts, size=n_paths)
        for j in range(kmax):
            act = alive & (k > j) & (state < 2)
            if not act.any():
                continue
            u = rng.random(n_paths)
            r = np.where(u < pw, rng.normal(R_WIN, SD_WIN, n_paths),
                np.where(u < pw + pl, rng.normal(R_LOSS, SD_LOSS, n_paths),
                         rng.normal(R_TIME, SD_TIME, n_paths)))
            eq = np.where(act, eq * (1 + risk * r), eq)

            # limit checks, applied to whichever account is live
            dead = act & ((eq <= floor) | (eq <= day_start * (1 - daily_frac)))
            state = np.where(dead, 2, state)
            alive = state < 2

            # evaluation passed -> funded account starts fresh at A
            passed = act & (state == 0) & (eq >= A * (1 + target))
            if passed.any():
                days_to_pass = np.where(passed & (days_to_pass < 0), d, days_to_pass)
                eq = np.where(passed, A, eq)
                day_start = np.where(passed, A, day_start)
                state = np.where(passed, 1, state)

        # withdrawals happen at day end on funded accounts
        hit = (state == 1) & (eq >= A * (1 + w))
        if hit.any():
            take = np.where(hit, eq - A * (1 + keep), 0.0)
            first = hit & (n_pay == 0)
            cash = take * split + np.where(first & refund_fee, fee, 0.0)
            banked += np.where(hit, cash, 0.0)
            n_pay += hit.astype(np.int32)
            eq = np.where(hit, A * (1 + keep), eq)

    ev = banked.mean() - fee
    return {
        "mu": mu, "risk": risk, "w": w, "keep": keep,
        "p_pass": float((n_pay > 0).mean()),
        "p_funded": float((days_to_pass >= 0).mean()),
        "p_bust": float((state == 2).mean()),
        "mean_payouts": float(n_pay.mean()),
        "mean_banked": float(banked.mean()),
        "median_banked": float(np.median(banked)),
        "ev": float(ev),
        "roi": float(ev / fee),
        "p_profit": float((banked > fee).mean()),
        "p95_banked": float(np.percentile(banked, 95)),
    }


def empirical_daily_counts():
    """Trades actually taken per calendar day under the frozen risk settings."""
    import account as A_
    T = A_.build_trades("vol_spike_cont")
    eq, live, taken = 100_000.0, [], []
    for _, t in T.iterrows():
        live = [x for x in live if x[0] > t.entry_dt]
        if sum(x[1] for x in live) / eq + 0.0025 > 0.02:
            continue
        live.append((t.exit_dt, eq * 0.0025))
        taken.append(t.entry_dt)
    s = pd.Series(1, index=pd.DatetimeIndex(taken)).resample("D").sum()
    return s.values.astype(int)


def main():
    dc = empirical_daily_counts()
    print(f"empirical daily trade counts: mean {dc.mean():.3f}, max {dc.max()}, "
          f"zero-days {100*(dc==0).mean():.0f}%")

    FEE, A, SPLIT = 800.0, 100_000.0, 0.80
    print(f"\nBreakout 1-Step Classic $100k: fee ${FEE:.0f}, split {100*SPLIT:.0f}%, "
          f"fee refunded on first payout, 24-month horizon\n")

    print("=" * 92)
    print("EV per evaluation purchased, as a function of TRUE per-trade expectancy")
    print("(withdraw at +5%, bank everything, 0.25% risk)")
    print("=" * 92)
    print(f"{'true expR':>10}{'win%':>7}{'P(funded)':>11}{'P(paid)':>9}"
          f"{'payouts':>9}{'mean $':>10}{'EV $':>10}{'ROI':>8}{'P(profit)':>10}")
    rows = []
    for mu in [-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.1426, 0.20, 0.30, 0.50]:
        r = simulate(mu, daily_counts=dc, fee=FEE, split=SPLIT, w=0.05, keep=0.0)
        if r is None:
            continue
        rows.append(r)
        print(f"{mu:>10.3f}{100*win_prob(mu):>7.1f}{100*r['p_funded']:>10.1f}%"
              f"{100*r['p_pass']:>8.1f}%{r['mean_payouts']:>9.2f}"
              f"{r['mean_banked']:>10.0f}{r['ev']:>10.0f}{r['roi']:>+8.2f}"
              f"{100*r['p_profit']:>9.1f}%")

    # breakeven edge
    lo, hi = -0.20, 0.50
    for _ in range(22):
        mid = (lo + hi) / 2
        r = simulate(mid, n_paths=30000, daily_counts=dc, fee=FEE, split=SPLIT,
                     w=0.05, keep=0.0, seed=3)
        if r["ev"] < 0:
            lo = mid
        else:
            hi = mid
    print(f"\n>>> BREAKEVEN true expectancy: {(lo+hi)/2:+.4f}R per trade "
          f"({100*win_prob((lo+hi)/2):.1f}% win rate at 2:1)")

    print("\n" + "=" * 92)
    print("Withdrawal policy: when to bank, given the floor never trails")
    print("(true expR fixed at the measured +0.1426R -- optimistic, see caveat)")
    print("=" * 92)
    print(f"{'withdraw at':>12}{'keep':>7}{'P(paid)':>9}{'payouts':>9}"
          f"{'mean $':>10}{'EV $':>10}{'p95 $':>10}")
    best = None
    for w in [0.02, 0.05, 0.10, 0.20, 0.30]:
        for keep in [0.0, 0.02, 0.05]:
            if keep >= w:
                continue
            r = simulate(0.1426, daily_counts=dc, fee=FEE, split=SPLIT,
                         w=w, keep=keep, seed=5)
            print(f"{100*w:>11.0f}%{100*keep:>6.0f}%{100*r['p_pass']:>8.1f}%"
                  f"{r['mean_payouts']:>9.2f}{r['mean_banked']:>10.0f}"
                  f"{r['ev']:>10.0f}{r['p95_banked']:>10.0f}")
            if best is None or r["ev"] > best[1]["ev"]:
                best = ((w, keep), r)
    print(f"\nbest policy: withdraw at +{100*best[0][0]:.0f}%, "
          f"keep +{100*best[0][1]:.0f}%  ->  EV ${best[1]['ev']:.0f}")

    print("\n" + "=" * 92)
    print("Risk per trade, at the measured edge, best withdrawal policy")
    print("=" * 92)
    print(f"{'risk':>7}{'P(funded)':>11}{'P(paid)':>9}{'payouts':>9}"
          f"{'mean $':>10}{'EV $':>10}{'P(profit)':>10}")
    for risk in [0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02]:
        r = simulate(0.1426, daily_counts=dc, risk=risk, fee=FEE, split=SPLIT,
                     w=best[0][0], keep=best[0][1], seed=7)
        print(f"{100*risk:>6.2f}%{100*r['p_funded']:>10.1f}%{100*r['p_pass']:>8.1f}%"
              f"{r['mean_payouts']:>9.2f}{r['mean_banked']:>10.0f}"
              f"{r['ev']:>10.0f}{100*r['p_profit']:>9.1f}%")

    print("\n" + "=" * 92)
    print("Sensitivity: 90% split, and the honest downside cases")
    print("=" * 92)
    for lbl, kw in [
        ("measured edge, 80% split", dict(mu=0.1426, split=0.80)),
        ("measured edge, 90% split", dict(mu=0.1426, split=0.90)),
        ("lower CI bound (+0.040R)", dict(mu=0.040, split=0.80)),
        ("half the measured edge", dict(mu=0.0713, split=0.80)),
        ("no edge at all (0.0R)", dict(mu=0.0, split=0.80)),
        ("holdout-implied (-0.61R)", dict(mu=-0.61, split=0.80)),
    ]:
        r = simulate(daily_counts=dc, fee=FEE, w=best[0][0], keep=best[0][1],
                     risk=0.0025, seed=11, **kw)
        if r is None:
            print(f"{lbl:<28} degenerate (win prob out of range) -> total loss of fee")
            continue
        print(f"{lbl:<28} P(funded) {100*r['p_funded']:>5.1f}%  "
              f"P(paid) {100*r['p_pass']:>5.1f}%  mean ${r['mean_banked']:>7.0f}  "
              f"EV ${r['ev']:>+7.0f}  ROI {r['roi']:>+6.2f}")


if __name__ == "__main__":
    main()
