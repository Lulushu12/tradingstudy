"""No-holds-barred: your own capital on a normal exchange.

No 3% daily rule, no 6% static floor, no evaluation to pass. The only limits are
exchange leverage, liquidation, and your tolerance for drawdown. This asks what
the systems actually found here would have produced under those conditions.

Sizing is by growth rate: f maximising E[log(1 + f*R)] on the real R
distribution, reported at full Kelly, half Kelly and quarter Kelly, because full
Kelly is correct only if the edge estimate is exact and it never is.

Both signals are shown side by side:
  vol_spike_cont + 15m divergence stop  - the best system in the study
  vol_spike_cont, plain 2R              - the baseline

and both at the STUDIED edge and at the holdout-adjusted posterior, since the
whole question turns on which of those is true.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exits as X         # noqa: E402
import run_exits as RE    # noqa: E402
import run_mtf as RM      # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def build(mode, ltf="15min", buf=0.05):
    parts = []
    for sym in RM.CORE:
        sig, m1 = RM.htf_signals(sym, "4h")
        ev = RE.ltf_events(sym, ltf)
        for side in (1, -1):
            ss = sig[sig.side == side]
            if not len(ss):
                continue
            e = ev[side]
            d = X.run(ss, m1, e["div_dt"], e["div_lvl"], e["dot_dt"],
                      mode=mode, buf_frac=buf)
            if len(d):
                parts.append(d)
    return pd.concat(parts).sort_values("close_dt").reset_index(drop=True)


def tilt(r, target_mu, rng, n):
    w, l = r[r > 0], r[r <= 0]
    mw, ml = w.mean(), l.mean()
    p = np.clip((target_mu - ml) / (mw - ml), 0.001, 0.999)
    pick = rng.random(n) < p
    out = np.empty(n)
    out[pick] = rng.choice(w, pick.sum())
    out[~pick] = rng.choice(l, (~pick).sum())
    return out


def growth(r, f):
    v = 1 + f * r
    return -np.inf if (v <= 0).any() else float(np.mean(np.log(v)))


def kelly(r, grid=np.arange(0.005, 0.601, 0.005)):
    g = np.array([growth(r, f) for f in grid])
    i = int(np.argmax(g))
    return grid[i], g[i]


def paths(r, f, n_per_month, months=24, n_paths=4000, mu=None, seed=3):
    rng = np.random.default_rng(seed)
    n = int(months * n_per_month)
    src = tilt(r, mu, rng, n_paths * n) if mu is not None else \
        rng.choice(r, n_paths * n)
    rs = src.reshape(n_paths, n)
    eq = np.cumprod(1 + f * rs, axis=1)
    peak = np.maximum.accumulate(eq, axis=1)
    dd = ((peak - eq) / peak).max(axis=1)
    fin = eq[:, -1]
    # first month index where equity doubles
    dbl = np.argmax(eq >= 2, axis=1).astype(float)
    dbl[eq.max(axis=1) < 2] = np.nan
    return {"median_final": float(np.median(fin)),
            "p5_final": float(np.percentile(fin, 5)),
            "p95_final": float(np.percentile(fin, 95)),
            "median_dd": float(np.median(dd)),
            "p_dd_over_50": float((dd > 0.5).mean()),
            "p_ruin_90": float((fin < 0.1).mean()),
            "p_double": float(np.isfinite(dbl).mean()),
            "median_months_to_double": float(np.nanmedian(dbl) / n_per_month)
            if np.isfinite(dbl).any() else np.nan,
            "median_monthly": float(np.median(fin) ** (1 / months) - 1)}


def main():
    for label, mode in (("BASE 2R", 0), ("TIGHTEN 15m div", 1)):
        T = build(mode)
        r = T["r"].values
        r = r[np.isfinite(r)]
        months = ((pd.Timestamp(T.close_dt.max())
                   - pd.Timestamp(T.close_dt.min())).days / 30.44)
        npm = len(r) / months
        fstar, g = kelly(r)
        print(f"\n{'='*74}\n{label}: n={len(r)}, {npm:.0f} trades/mo, "
              f"expR {r.mean():+.4f}")
        print(f"  growth-optimal f = {100*fstar:.1f}% of bankroll per trade")
        print(f"{'sizing':<14}{'f':>7}{'med monthly':>13}{'med 24mo':>11}"
              f"{'p5':>8}{'p95':>10}{'med DD':>9}{'P(DD>50%)':>11}{'P(ruin)':>9}")
        for nm, f in (("quarter Kelly", fstar / 4), ("half Kelly", fstar / 2),
                      ("full Kelly", fstar)):
            p = paths(r, f, npm, mu=None)
            print(f"{nm:<14}{100*f:>6.1f}%{100*p['median_monthly']:>12.1f}%"
                  f"{p['median_final']:>11.2f}{p['p5_final']:>8.2f}"
                  f"{p['p95_final']:>10.1f}{100*p['median_dd']:>8.0f}%"
                  f"{100*p['p_dd_over_50']:>10.0f}%{100*p['p_ruin_90']:>8.0f}%")

        print(f"  -- same system if the true edge is the holdout-adjusted "
              f"posterior (+0.024R) --")
        for nm, f in (("quarter Kelly", fstar / 4), ("half Kelly", fstar / 2)):
            p = paths(r, f, npm, mu=0.024)
            print(f"{nm:<14}{100*f:>6.1f}%{100*p['median_monthly']:>12.1f}%"
                  f"{p['median_final']:>11.2f}{p['p5_final']:>8.2f}"
                  f"{p['p95_final']:>10.1f}{100*p['median_dd']:>8.0f}%"
                  f"{100*p['p_dd_over_50']:>10.0f}%{100*p['p_ruin_90']:>8.0f}%")


if __name__ == "__main__":
    main()
