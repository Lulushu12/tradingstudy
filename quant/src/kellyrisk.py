"""How fragile is the own-money plan to being wrong about the edge?

Kelly sizing is derived from an ASSUMED edge. Size for +0.14R when the truth is
+0.02R and you are massively over-levered: growth goes negative even though the
edge is still positive. This quantifies that, because it is the difference
between a business and a blow-up.

Also: a power calculation. How many prop accounts, or how many trades, before
the pass/fail record actually distinguishes a +0.14R edge from a +0.02R one?
That number is what the prop structure is really worth - it is paid-for
out-of-sample evidence with capped downside.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import account as A       # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def tilt(r, target_mu, rng, n):
    """Resample the empirical R distribution, shifted to a target expectancy by
    reweighting wins vs losses rather than by adding a constant."""
    win = r[r > 0]
    loss = r[r <= 0]
    mw, ml = win.mean(), loss.mean()
    p = (target_mu - ml) / (mw - ml)
    p = np.clip(p, 0.001, 0.999)
    pick = rng.random(n) < p
    out = np.empty(n)
    out[pick] = rng.choice(win, pick.sum())
    out[~pick] = rng.choice(loss, (~pick).sum())
    return out


def growth(r, f):
    v = 1 + f * r
    if (v <= 0).any():
        return -np.inf
    return float(np.mean(np.log(v)))


def kelly_star(r, grid=np.arange(0.002, 0.401, 0.002)):
    g = np.array([growth(r, f) for f in grid])
    i = int(np.argmax(g))
    return grid[i], g[i]


def mismatch_matrix(T, assumed=(0.024, 0.05, 0.1426), truths=(-0.0148, 0.0, 0.024, 0.05, 0.1426),
                    n_per_month=52, seed=3):
    r = T.r.values.astype(float)
    r = r[np.isfinite(r)]
    rng = np.random.default_rng(seed)
    print("Monthly growth when you SIZE for one edge and the TRUTH is another")
    print("(half-Kelly sizing, which is what any sane operator would use)\n")
    hdr = "".join(f"{t:>+12.4f}" for t in truths)
    print(f"{'sized for':>12}{'f used':>9}{hdr}")
    rows = []
    for a in assumed:
        ra = tilt(r, a, rng, 400_000)
        fa, _ = kelly_star(ra)
        f_half = fa / 2
        cells = []
        for t in truths:
            rt = tilt(r, t, rng, 400_000)
            g = growth(rt, f_half)
            mo = np.exp(g * n_per_month) - 1 if np.isfinite(g) else -1.0
            cells.append(mo)
            rows.append({"assumed": a, "truth": t, "f": f_half, "monthly": mo})
        print(f"{a:>+12.4f}{100*f_half:>8.1f}%" +
              "".join(f"{100*c:>11.1f}%" for c in cells))
    print("\n  Read the diagonal for 'you were right'. Read left of it for the")
    print("  cost of being optimistic. Growth turns negative well before the")
    print("  edge does.")
    return pd.DataFrame(rows)


def drawdown_at_f(T, f, mu, n_paths=2000, months=24, n_per_month=52, seed=7):
    r = T.r.values.astype(float)
    r = r[np.isfinite(r)]
    rng = np.random.default_rng(seed)
    n = int(months * n_per_month)
    rs = tilt(r, mu, rng, n_paths * n).reshape(n_paths, n)
    eq = np.cumprod(1 + f * rs, axis=1)
    peak = np.maximum.accumulate(eq, axis=1)
    dd = ((peak - eq) / peak).max(axis=1)
    final = eq[:, -1]
    return {"f": f, "mu": mu, "median_dd": float(np.median(dd)),
            "p95_dd": float(np.percentile(dd, 95)),
            "p_dd_over_50": float((dd > 0.5).mean()),
            "median_final": float(np.median(final)),
            "p_lose_half": float((final < 0.5).mean()),
            "p_double_in_4mo": float((eq[:, min(4*n_per_month, n-1)] >= 2).mean())}


def power(T, mu_a=0.1426, mu_b=0.024, seed=11):
    """Trades needed to tell a +0.14R edge from a +0.02R one at 95%/80%."""
    r = T.r.values.astype(float)
    sd = float(np.nanstd(r))
    delta = mu_a - mu_b
    n = ((1.96 + 0.84) * sd / delta) ** 2
    print(f"\n  R standard deviation           : {sd:.3f}")
    print(f"  difference to detect           : {delta:.4f}R")
    print(f"  trades needed (95% conf, 80% power): {n:,.0f}")
    print(f"  at 52 trades/month that is      : {n/52:,.0f} months "
          f"({n/52/12:.1f} years)")
    return n


def main():
    T = A.build_trades("vol_spike_cont")
    r = T.r.values.astype(float)
    n_per_month = len(T) / ((T.entry_dt.max() - T.entry_dt.min()).days / 30.44)

    print("=" * 84)
    print("1.  KELLY MISMATCH: the cost of being wrong about the edge")
    print("=" * 84)
    mismatch_matrix(T, n_per_month=n_per_month)

    print("\n" + "=" * 84)
    print("2.  WHAT THOSE SIZINGS ACTUALLY FEEL LIKE (24 months, simulated)")
    print("=" * 84)
    print(f"{'f':>7}{'true expR':>11}{'median DD':>11}{'p95 DD':>9}"
          f"{'P(DD>50%)':>11}{'median x':>10}{'P(lose half)':>14}{'P(2x in 4mo)':>14}")
    for f in (0.01, 0.02, 0.04, 0.08):
        for mu in (0.024, 0.1426):
            d = drawdown_at_f(T, f, mu, n_per_month=int(n_per_month))
            print(f"{100*f:>6.1f}%{mu:>+11.4f}{100*d['median_dd']:>10.0f}%"
                  f"{100*d['p95_dd']:>8.0f}%{100*d['p_dd_over_50']:>10.0f}%"
                  f"{d['median_final']:>10.2f}{100*d['p_lose_half']:>13.0f}%"
                  f"{100*d['p_double_in_4mo']:>13.0f}%")

    print("\n" + "=" * 84)
    print("3.  HOW LONG UNTIL YOU KNOW WHICH EDGE YOU HAVE")
    print("=" * 84)
    power(T)


if __name__ == "__main__":
    main()
