"""What does 10%/month at <=6% static DD actually require of a strategy?

Rather than argue about it, simulate. For a grid of (per-trade expectancy,
trades per month), size risk to the largest value that keeps a Monte-Carlo
max-drawdown below the Breakout limit at a stated confidence, then read off
the achievable monthly return. This produces the frontier the search must hit.

Two regimes, because they differ enormously:
  KEEP  - profits stay in the account. Static floor at 94k never trails, so the
          buffer grows. This is the evaluation / compounding case.
  SWEEP - profits withdrawn monthly, balance and floor reset every month. Every
          month is month one. This is 'consistent 10% every month'.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
N_PATH = 4000


def trade_r(n, exp_r, rr, rng):
    """Bernoulli R outcomes with the given expectancy at a fixed RR."""
    p = (exp_r + 1.0) / (1.0 + rr)
    p = np.clip(p, 0.001, 0.999)
    w = rng.random(n) < p
    return np.where(w, rr, -1.0)


def sim_sweep(exp_r, tpm, risk, rr, months=24, npath=N_PATH, floor=0.06,
              daily_cap=0.03, per_day=None):
    """Monthly reset. Returns (mean monthly ret, P(bust in a month), P(month>=10%))."""
    rets = np.zeros((npath, months))
    bust = np.zeros((npath, months), dtype=bool)
    for m in range(months):
        rs = trade_r(npath * tpm, exp_r, rr, rng).reshape(npath, tpm)
        eq = 1.0 + np.cumsum(rs * risk, axis=1)
        low = np.minimum.accumulate(eq, axis=1).min(axis=1)
        bust[:, m] = low <= (1 - floor)
        rets[:, m] = eq[:, -1] - 1.0
    rets = np.where(bust, -floor, rets)
    return rets.mean(), bust.mean(), (rets >= 0.10).mean()


def sim_keep(exp_r, tpm, risk, rr, months=24, npath=N_PATH, floor=0.06):
    """Compounding, static floor anchored to the ORIGINAL balance."""
    n = tpm * months
    rs = trade_r(npath * n, exp_r, rr, rng).reshape(npath, n)
    eq = np.ones(npath)
    floor_abs = 1 - floor
    alive = np.ones(npath, dtype=bool)
    curve = np.zeros((npath, n))
    for i in range(n):
        eq = np.where(alive, eq * (1 + rs[:, i] * risk), eq)
        alive &= eq > floor_abs
        curve[:, i] = eq
    peak = np.maximum.accumulate(curve, axis=1)
    dd = ((peak - curve) / peak).max(axis=1)
    monthly = curve[:, -1] ** (1 / months) - 1
    return monthly.mean(), (~alive).mean(), dd.mean(), np.median(monthly)


def frontier():
    rr = 2.0
    print("=== SWEEP regime: withdraw monthly, floor resets. "
          "'consistent 10% every month' ===")
    print(f"{'expR':>6} {'trades/mo':>10} {'risk%':>7} {'mean/mo':>9} "
          f"{'P(bust)':>8} {'P(>=10%)':>9}")
    rows = []
    for exp_r in [0.05, 0.10, 0.20, 0.30, 0.50]:
        for tpm in [20, 60, 150, 300]:
            best = None
            for risk in np.arange(0.001, 0.061, 0.001):
                mu, pb, p10 = sim_sweep(exp_r, tpm, risk, rr, months=24, npath=1500)
                if pb <= 0.02:            # <=2% chance of blowing an account per month
                    best = (risk, mu, pb, p10)
                else:
                    break
            if best:
                risk, mu, pb, p10 = best
                rows.append(dict(exp_r=exp_r, tpm=tpm, risk=risk, mean_mo=mu,
                                 p_bust=pb, p_10=p10))
                print(f"{exp_r:6.2f} {tpm:10d} {100*risk:6.2f}% {100*mu:8.2f}% "
                      f"{100*pb:7.2f}% {100*p10:8.1f}%")
    pd.DataFrame(rows).to_csv(
        os.path.join(os.path.dirname(__file__), "..", "reports", "req_sweep.csv"),
        index=False)

    print("\n=== KEEP regime: compound, static floor never trails ===")
    print(f"{'expR':>6} {'trades/mo':>10} {'risk%':>7} {'CAGR/mo':>9} "
          f"{'P(bust)':>8} {'meanDD':>8}")
    rows = []
    for exp_r in [0.05, 0.10, 0.20, 0.30, 0.50]:
        for tpm in [20, 60, 150, 300]:
            best = None
            for risk in np.arange(0.001, 0.061, 0.001):
                mu, pb, dd, med = sim_keep(exp_r, tpm, risk, rr, months=24, npath=1200)
                if pb <= 0.02:
                    best = (risk, mu, pb, dd)
                else:
                    break
            if best:
                risk, mu, pb, dd = best
                rows.append(dict(exp_r=exp_r, tpm=tpm, risk=risk, cagr_mo=mu,
                                 p_bust=pb, mean_dd=dd))
                print(f"{exp_r:6.2f} {tpm:10d} {100*risk:6.2f}% {100*mu:8.2f}% "
                      f"{100*pb:7.2f}% {100*dd:7.2f}%")
    pd.DataFrame(rows).to_csv(
        os.path.join(os.path.dirname(__file__), "..", "reports", "req_keep.csv"),
        index=False)

    # What per-trade expectancy is REQUIRED for 10%/mo in the sweep regime?
    print("\n=== minimum expectancy for mean 10%/mo with P(bust)<=2%, SWEEP ===")
    for tpm in [20, 60, 150, 300, 600]:
        found = None
        for exp_r in np.arange(0.02, 1.51, 0.02):
            ok = None
            for risk in np.arange(0.001, 0.081, 0.001):
                mu, pb, p10 = sim_sweep(exp_r, tpm, risk, rr, months=12, npath=1200)
                if pb <= 0.02:
                    ok = mu
                else:
                    break
            if ok is not None and ok >= 0.10:
                found = (exp_r, ok)
                break
        if found:
            wr = (found[0] + 1) / 3
            print(f"  {tpm:4d} trades/mo -> need expR >= {found[0]:.2f} "
                  f"(= {100*wr:.1f}% WR at 2:1 net)  achieves {100*found[1]:.1f}%/mo")
        else:
            print(f"  {tpm:4d} trades/mo -> UNREACHABLE even at expR 1.50")


if __name__ == "__main__":
    frontier()
