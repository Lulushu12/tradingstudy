"""Regime filter for the base signal.

Diagnosis from the holdout failure: vol_spike_cont is a trend-continuation bet
and it dies when the market has no trend to continue. The holdout window had
path-efficiency 0.000 (BTC moved +0.04% net over 5.5 weeks) against a TRAIN
median of 0.082.

So: condition the signal on a causal measure of how trend-worthy the regime is,
and see how much of the edge that recovers. Reported two ways —
  IS   : best threshold chosen with full hindsight (what you asked for)
  WF   : threshold refitted on a rolling trailing window only (honest version)
so the gap between them measures how much of the gain is hindsight.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402


def base_signal(d):
    """vol_spike_cont, as frozen."""
    sp = d.trade_intensity > 1.8
    lm = sp & (d.disp96 > 0) & (d.ret > 0)
    sm = sp & (d.disp96 < 0) & (d.ret < 0)
    return lm.fillna(False).values, sm.fillna(False).values


def to_trades(d, lm, sm, extra=None):
    """Collapse a long/short mask pair into a trade frame."""
    cols = ["dt", "symbol"] + (extra or [])
    parts = []
    for mask, side, rc, oc in ((lm, 1, "r_long", "out_long"),
                               (sm, -1, "r_short", "out_short")):
        sel = mask & np.isfinite(d[rc].values)
        if sel.sum() == 0:
            continue
        t = d.loc[sel, cols].copy()
        t["side"] = side
        t["r"] = d.loc[sel, rc].values
        t["outcome"] = d.loc[sel, oc].values
        parts.append(t)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts).sort_values("dt").reset_index(drop=True)


def monthly_R(t):
    """Sum of R per calendar month — the quantity that maps to account return."""
    if len(t) == 0:
        return pd.Series(dtype=float)
    s = t.set_index(pd.DatetimeIndex(t.dt))["r"].resample("ME").sum()
    return s


def scan_regime(d, min_frac=0.15):
    """For each feature, find the threshold (either direction) that maximises
    the base signal's expectancy, keeping at least min_frac of the trades."""
    lm, sm = base_signal(d)
    feats = DS.feature_list(d)
    base_t = to_trades(d, lm, sm)
    n0, e0 = len(base_t), base_t.r.mean()
    rows = []
    for c in feats:
        x = d[c].values.astype(float)
        if not np.isfinite(x).any():
            continue
        qs = np.nanquantile(x, np.linspace(0.05, 0.95, 19))
        for thr in np.unique(qs):
            for direction in (1, -1):
                keep = (x >= thr) if direction > 0 else (x <= thr)
                keep = keep & np.isfinite(x)
                t = to_trades(d, lm & keep, sm & keep)
                if len(t) < n0 * min_frac or len(t) < 200:
                    continue
                mR = monthly_R(t)
                rows.append({
                    "feature": c, "thr": float(thr), "sgn": direction,
                    "n": len(t), "frac": len(t) / n0,
                    "exp_r": float(t.r.mean()), "lift": float(t.r.mean() - e0),
                    "wr": float((t.outcome == 1).mean()),
                    "monthly_R": float(mR.mean()),
                    "ratio": float(mR.mean()/abs(mR.min())) if mR.min()<0 else np.inf,
                    "pos_months": float((mR > 0).mean()),
                    "worst_month_R": float(mR.min()),
                })
    return pd.DataFrame(rows), n0, e0


def walkforward_filter(d, feature, direction, q=0.5, train_months=18,
                       step_months=1):
    """Refit the threshold on a trailing window only, then apply it forward."""
    lm, sm = base_signal(d)
    x = d[feature].values.astype(float)
    dt = pd.DatetimeIndex(d.dt)
    months = pd.period_range(dt.min(), dt.max(), freq="M")
    keep = np.zeros(len(d), dtype=bool)
    for i in range(train_months, len(months), step_months):
        tr_lo = months[i - train_months].start_time.tz_localize("UTC")
        tr_hi = months[i].start_time.tz_localize("UTC")
        te_hi = months[min(i + step_months, len(months) - 1)].start_time.tz_localize("UTC")
        trm = (dt >= tr_lo) & (dt < tr_hi)
        tem = (dt >= tr_hi) & (dt < te_hi)
        if trm.sum() < 500 or tem.sum() == 0:
            continue
        xt = x[trm]
        xt = xt[np.isfinite(xt)]
        if len(xt) < 100:
            continue
        thr = np.quantile(xt, q if direction > 0 else 1 - q)
        sel = (x >= thr) if direction > 0 else (x <= thr)
        keep |= (tem & sel & np.isfinite(x))
    return to_trades(d, lm & keep, sm & keep)


def main():
    d = DS.build(tf="4h", hold=60)
    lm, sm = base_signal(d)
    base = to_trades(d, lm, sm)
    mR = monthly_R(base)
    print("=== base signal (vol_spike_cont, 5 assets, 4h) ===")
    print(f"n={len(base)}  expR {base.r.mean():+.4f}  "
          f"monthly sum-R {mR.mean():+.2f}  positive months {100*(mR>0).mean():.0f}%  "
          f"worst month {mR.min():+.1f}R")

    print("\n=== regime scan: best threshold per feature (IN-SAMPLE, hindsight) ===")
    sc, n0, e0 = scan_regime(d)
    sc = sc.sort_values("exp_r", ascending=False)
    best = sc.drop_duplicates("feature").head(20)
    print(f"{'feature':<18}{'dir':>4}{'thr':>10}{'n':>7}{'keep%':>7}"
          f"{'expR':>8}{'lift':>8}{'mo_R':>7}{'pos%':>6}{'worst':>8}")
    for _, r in best.iterrows():
        print(f"{r.feature:<18}{int(r.sgn):>4}{r.thr:>10.3g}{int(r.n):>7}"
              f"{100*r.frac:>6.0f}%{r.exp_r:>8.3f}{r.lift:>8.3f}"
              f"{r.monthly_R:>7.2f}{100*r.pos_months:>5.0f}%{r.worst_month_R:>8.1f}")

    sc.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "reports", "regime_scan.csv"), index=False)

    print("\n=== walk-forward check on the top 8 (threshold refit on trailing 18m) ===")
    print(f"{'feature':<18}{'IS expR':>9}{'WF expR':>9}{'WF n':>7}"
          f"{'WF mo_R':>9}{'WF pos%':>9}")
    for _, r in best.head(8).iterrows():
        wf = walkforward_filter(d, r.feature, int(r.sgn), q=1 - r.frac)
        if len(wf) < 50:
            print(f"{r.feature:<18}{r.exp_r:>9.3f}   too few WF trades")
            continue
        wmR = monthly_R(wf)
        print(f"{r.feature:<18}{r.exp_r:>9.3f}{wf.r.mean():>9.3f}{len(wf):>7}"
              f"{wmR.mean():>9.2f}{100*(wmR>0).mean():>8.0f}%")

    # combined filter: intersect the top few independent regime conditions
    print("\n=== stacked regime conditions (in-sample) ===")
    top = best.head(6)
    for k in (2, 3, 4):
        for combo in _combos(list(top.itertuples()), k):
            keep = np.ones(len(d), dtype=bool)
            for r in combo:
                x = d[r.feature].values.astype(float)
                keep &= ((x >= r.thr) if r.sgn > 0 else (x <= r.thr)) & np.isfinite(x)
            t = to_trades(d, lm & keep, sm & keep)
            if len(t) < 300:
                continue
            m = monthly_R(t)
            names = "+".join(r.feature for r in combo)
            if t.r.mean() > e0 + 0.15:
                print(f"  {names:<52} n={len(t):>5} expR {t.r.mean():+.3f} "
                      f"mo_R {m.mean():+.2f} pos {100*(m>0).mean():.0f}% "
                      f"worst {m.min():+.1f}")


def _combos(items, k):
    from itertools import combinations
    return list(combinations(items, k))


if __name__ == "__main__":
    main()
