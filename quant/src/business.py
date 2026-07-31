"""Business-model analysis for the two structures on offer.

The per-account numbers are unattractive. But a business is not one account. The
questions that decide whether anything here scales are different ones:

  1. CORRELATION. Running the same system on N prop accounts at once is one bet
     wearing N hats: they all pass or all bust together. Real parallelism needs
     decorrelated streams. So measure the actual correlation between per-asset
     and per-system monthly returns, and convert it into an EFFECTIVE number of
     independent accounts.

  2. CAPITAL EFFICIENCY. A prop fee is not an investment in the trade, it is the
     price of an option on someone else's balance sheet. The right metric is EV
     per dollar of fee per unit of elapsed time, not return on the notional.

  3. GROWTH-OPTIMAL SIZING for own money. Not "what leverage doubles fastest"
     but the f that maximises E[log(1+f*R)] on the real R distribution, with the
     drawdown and ruin that come with it.

Everything is computed on the honest (walk-forward-credible) edge range, not the
hindsight fit, because a business plan built on the hindsight fit is fiction.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import account as A       # noqa: E402
import payout as P        # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


# ---------------------------------------------------------------- 1. correlation
def stream_correlation():
    T = A.build_trades("vol_spike_cont")
    T["month"] = pd.DatetimeIndex(T.entry_dt).to_period("M")
    piv = T.pivot_table(index="month", columns="symbol", values="r",
                        aggfunc="sum").fillna(0.0)
    corr = piv.corr()
    print("Monthly R correlation between per-asset streams (same system):")
    print(corr.round(3).to_string())
    off = corr.values[np.triu_indices_from(corr.values, k=1)]
    rho = float(np.mean(off))
    n = len(corr)
    eff = n / (1 + (n - 1) * rho) if (1 + (n - 1) * rho) > 0 else np.nan
    print(f"\n  mean pairwise correlation rho = {rho:.3f}")
    print(f"  {n} assets -> effective independent streams = {eff:.2f}")
    print(f"  variance reduction available = {np.sqrt(eff/n):.2f}x "
          f"(1.00 = none, {1/np.sqrt(n):.2f} = perfect)")
    return piv, rho, eff


def sequential_vs_parallel(rho, n_acc=(1, 2, 5, 10, 20)):
    """How much does running N accounts at once actually help, given rho?"""
    print("\n  Running N accounts SIMULTANEOUSLY on the same system:")
    print(f"  {'N':>4}{'eff. independent':>19}{'sd of mean outcome':>22}")
    for n in n_acc:
        eff = n / (1 + (n - 1) * rho) if (1 + (n - 1) * rho) > 0 else np.nan
        print(f"  {n:>4}{eff:>19.2f}{1/np.sqrt(eff):>21.2f}x")
    print("\n  Running N accounts SEQUENTIALLY (different time periods, rho~0):")
    print(f"  {'N':>4}{'eff. independent':>19}{'sd of mean outcome':>22}")
    for n in n_acc:
        print(f"  {n:>4}{n:>19.2f}{1/np.sqrt(n):>21.2f}x")


# ------------------------------------------------------- 2. prop business model
def prop_business(edges=(-0.0148, 0.0, 0.024, 0.05, 0.1426), fee=800.0,
                  accounts_per_year=6):
    """EV per account and the resulting annual business economics."""
    dc = P.empirical_daily_counts()
    print(f"\n{'true expR':>10}{'EV/account':>12}{'ROI on fee':>12}"
          f"{'P(lose fee)':>13}{'ann. EV @6 acc':>16}{'ann. fees':>11}")
    rows = []
    for mu in edges:
        r = P.simulate(mu, n_paths=30000, daily_counts=dc, fee=fee, split=0.80,
                       w=0.02, keep=0.0, risk=0.0025, seed=31)
        if r is None:
            continue
        ann_ev = r["ev"] * accounts_per_year
        ann_fee = fee * accounts_per_year
        rows.append({"mu": mu, "ev": r["ev"], "roi": r["roi"],
                     "p_lose": 1 - r["p_profit"], "ann_ev": ann_ev})
        print(f"{mu:>10.4f}{r['ev']:>12.0f}{r['roi']:>+12.2f}"
              f"{100*(1-r['p_profit']):>12.1f}%{ann_ev:>16.0f}{ann_fee:>11.0f}")
    return pd.DataFrame(rows)


def business_ruin(mu, fee=800.0, bankroll_mult=(5, 10, 20, 50), n_paths=4000,
                  n_cycles=24, seed=5):
    """Buy accounts sequentially from a bankroll. Does the business survive its
    own variance long enough for the edge to show up?"""
    dc = P.empirical_daily_counts()
    r = P.simulate(mu, n_paths=20000, daily_counts=dc, fee=fee, split=0.80,
                   w=0.02, keep=0.0, risk=0.0025, seed=seed)
    if r is None:
        return None
    # empirical payoff distribution per account: approximate with the simulated
    # mean/prob structure - win pays (ev+fee)/p, else 0
    p_win = r["p_pass"]
    if p_win <= 0:
        return None
    pay_win = r["mean_banked"] / p_win
    rng = np.random.default_rng(seed)
    out = []
    for bm in bankroll_mult:
        bank0 = fee * bm
        bank = np.full(n_paths, bank0)
        alive = np.ones(n_paths, bool)
        for _ in range(n_cycles):
            can = alive & (bank >= fee)
            bank = np.where(can, bank - fee, bank)
            win = rng.random(n_paths) < p_win
            bank = np.where(can & win, bank + pay_win, bank)
            alive &= (bank >= fee)
        out.append({"bankroll_fees": bm, "start": bank0,
                    "p_broke": float((~alive).mean()),
                    "median_end": float(np.median(bank)),
                    "mean_end": float(bank.mean()),
                    "p_doubled": float((bank >= 2 * bank0).mean())})
    return pd.DataFrame(out), p_win, pay_win


# ------------------------------------------------- 3. growth-optimal own money
def kelly(T, fracs=np.arange(0.005, 0.301, 0.005)):
    """f maximising E[log(1+f*R)] on the real R distribution."""
    r = T.r.values.astype(float)
    r = r[np.isfinite(r)]
    g = []
    for f in fracs:
        v = 1 + f * r
        if (v <= 0).any():
            g.append(-np.inf)
            continue
        g.append(float(np.mean(np.log(v))))
    g = np.array(g)
    i = int(np.argmax(g))
    return fracs[i], g[i], fracs, g


def own_money_business(T, label):
    f_star, g_star, fracs, g = kelly(T)
    n_per_month = len(T) / ((T.entry_dt.max() - T.entry_dt.min()).days / 30.44)
    print(f"\n  --- {label} (expR {T.r.mean():+.4f}, {n_per_month:.0f} trades/mo) ---")
    print(f"  growth-optimal f (full Kelly) = {100*f_star:.1f}% of bankroll per trade")
    print(f"  log-growth per trade at f*    = {g_star:.5f}")
    print(f"  implied monthly growth        = {100*(np.exp(g_star*n_per_month)-1):.1f}%")
    print(f"  {'f':>7}{'g/trade':>11}{'monthly':>10}{'annual':>12}{'note':>16}")
    for f in (0.01, 0.02, f_star / 2, f_star, min(f_star * 1.5, 0.3)):
        v = 1 + f * T.r.values
        if (v <= 0).any():
            print(f"  {100*f:>6.1f}%{'RUIN':>11}{'-':>10}{'-':>12}"
                  f"{'a loss exceeds bankroll':>16}")
            continue
        gg = float(np.mean(np.log(v)))
        mo = np.exp(gg * n_per_month) - 1
        yr = np.exp(gg * n_per_month * 12) - 1
        note = "half-Kelly" if abs(f - f_star / 2) < 1e-9 else (
            "FULL Kelly" if abs(f - f_star) < 1e-9 else "")
        print(f"  {100*f:>6.1f}%{gg:>11.5f}{100*mo:>9.1f}%{100*yr:>11.0f}%{note:>16}")
    return f_star, n_per_month


def main():
    print("=" * 82)
    print("1.  CORRELATION: can prop accounts be run in parallel at all?")
    print("=" * 82)
    piv, rho, eff = stream_correlation()
    sequential_vs_parallel(rho)

    print("\n" + "=" * 82)
    print("2.  PROP CHURN ECONOMICS (per account, and annualised)")
    print("=" * 82)
    prop_business()

    print("\n" + "=" * 82)
    print("3.  BANKROLL SURVIVAL: sequential account buying, 24 cycles")
    print("=" * 82)
    for mu in (0.024, 0.1426):
        res = business_ruin(mu)
        if res is None:
            continue
        df, p_win, pay = res
        print(f"\n  true expR {mu:+.4f}: P(account pays) {100*p_win:.1f}%, "
              f"mean payout when it does ${pay:,.0f}")
        print(f"  {'bankroll':>10}{'start $':>10}{'P(broke)':>10}"
              f"{'median end':>13}{'mean end':>11}{'P(2x)':>8}")
        for _, r in df.iterrows():
            print(f"  {int(r.bankroll_fees):>7} fees{r.start:>10.0f}"
                  f"{100*r.p_broke:>9.1f}%{r.median_end:>13.0f}"
                  f"{r.mean_end:>11.0f}{100*r.p_doubled:>7.1f}%")

    print("\n" + "=" * 82)
    print("4.  OWN MONEY: growth-optimal sizing on the real R distribution")
    print("=" * 82)
    T = A.build_trades("vol_spike_cont")
    own_money_business(T, "vol_spike_cont, all 5 assets")


if __name__ == "__main__":
    main()
