"""Gradient-boosted edge prediction.

Predict the realised R of a long and of a short taken at each bar, from the 71
causal features. Trade when the predicted edge clears a threshold; take the
side with the better prediction.

Reported in two modes, always side by side:
  WF  - purged, embargoed walk-forward. The model at time t saw only data
        before t. This is what could actually have been traded.
  IS  - model fit on the whole span and predicting its own training data.
        Pure hindsight, requested explicitly. Included so the gap between the
        two is visible rather than hidden.

The objective is not expectancy. It is monthly-R divided by worst-drawdown-R,
because that ratio is what the 10%/month at 6% drawdown target reduces to.
"""
import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402

PARAMS = dict(objective="regression", learning_rate=0.03, num_leaves=31,
              min_data_in_leaf=200, feature_fraction=0.7, bagging_fraction=0.7,
              bagging_freq=1, lambda_l2=5.0, verbosity=-1, num_threads=4)


def monthly_R(dt, r):
    s = pd.Series(np.asarray(r), index=pd.DatetimeIndex(dt)).resample("ME").sum()
    return s


def drawdown_R(dt, r):
    """Worst peak-to-trough of the cumulative R curve, in R."""
    s = pd.Series(np.asarray(r), index=pd.DatetimeIndex(dt)).sort_index().cumsum()
    if len(s) == 0:
        return np.nan
    return float((s.cummax() - s).max())


def summarise(dt, r, label, months_total):
    if len(r) == 0:
        return None
    m = monthly_R(dt, r)
    dd = drawdown_R(dt, r)
    mo = float(np.asarray(r).sum() / months_total)
    return {"label": label, "n": len(r), "exp_r": float(np.mean(r)),
            "monthly_R": mo, "maxDD_R": dd,
            "ratio": mo / dd if dd and dd > 0 else np.inf,
            "pos_months": float((m > 0).mean()),
            "worst_month": float(m.min()) if len(m) else np.nan,
            # sizing implied by a 6% static floor, and the return it yields
            "risk_pct": (0.06 / dd) if dd and dd > 0 else np.nan,
            "monthly_ret": (0.06 / dd) * mo if dd and dd > 0 else np.nan}


def walkforward_predict(d, feats, target, train_months=24, step_months=3,
                        embargo_bars=60, n_rounds=400):
    """Expanding-window WF with an embargo to kill overlap leakage."""
    dt = pd.DatetimeIndex(d.dt)
    y = d[target].values.astype(float)
    X = d[feats].values.astype(np.float32)
    ok = np.isfinite(y)
    months = pd.period_range(dt.min(), dt.max(), freq="M")
    pred = np.full(len(d), np.nan)

    i = train_months
    while i < len(months):
        tr_hi = months[i].start_time.tz_localize("UTC")
        te_hi = months[min(i + step_months, len(months) - 1)].start_time.tz_localize("UTC")
        if te_hi <= tr_hi:
            break
        trm = (dt < tr_hi) & ok
        tem = (dt >= tr_hi) & (dt < te_hi)
        # embargo: drop the last `embargo_bars` rows of train (their outcomes
        # overlap the test window)
        idx = np.where(trm)[0]
        if len(idx) > embargo_bars * 6:
            trm[idx[-embargo_bars:]] = False
        if trm.sum() < 2000 or tem.sum() == 0:
            i += step_months
            continue
        ds = lgb.Dataset(X[trm], label=y[trm], feature_name=feats)
        booster = lgb.train(PARAMS, ds, num_boost_round=n_rounds)
        pred[tem] = booster.predict(X[tem])
        i += step_months
    return pred


def insample_predict(d, feats, target, n_rounds=400):
    y = d[target].values.astype(float)
    X = d[feats].values.astype(np.float32)
    ok = np.isfinite(y)
    ds = lgb.Dataset(X[ok], label=y[ok], feature_name=feats)
    b = lgb.train(PARAMS, ds, num_boost_round=n_rounds)
    return b.predict(X), b


def strategy(d, pl, ps, thr, max_per_bar=None):
    """Take the better side when its predicted edge clears thr."""
    best = np.where(pl >= ps, pl, ps)
    side = np.where(pl >= ps, 1, -1)
    take = np.isfinite(best) & (best >= thr)
    r = np.where(side > 0, d.r_long.values, d.r_short.values)
    take &= np.isfinite(r)
    return d.dt.values[take], r[take], side[take], take


def run(tf="4h", hold=60, thr_grid=None, train_months=24):
    d = DS.build(tf=tf, hold=hold)
    feats = DS.feature_list(d)
    months_total = (pd.Timestamp(d.dt.max()) - pd.Timestamp(d.dt.min())).days / 30.44
    print(f"=== {tf} | rows {len(d):,} | feats {len(feats)} | "
          f"{months_total:.1f} months ===")

    print("fitting walk-forward models ...")
    wf_l = walkforward_predict(d, feats, "r_long", train_months=train_months)
    wf_s = walkforward_predict(d, feats, "r_short", train_months=train_months)
    print("fitting in-sample models ...")
    is_l, bl = insample_predict(d, feats, "r_long")
    is_s, bs = insample_predict(d, feats, "r_short")

    imp = pd.Series(bl.feature_importance("gain"), index=feats).sort_values(
        ascending=False)
    print("\ntop features by gain (long model, in-sample):")
    for k, v in imp.head(12).items():
        print(f"   {k:<20}{v:>12.0f}")

    thr_grid = thr_grid or [-0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]
    rows = []
    for mode, pl, ps in (("WF", wf_l, wf_s), ("IS", is_l, is_s)):
        # WF predictions only exist after the first training window
        valid = np.isfinite(pl) & np.isfinite(ps)
        mt = ((pd.Timestamp(d.dt[valid].max()) - pd.Timestamp(d.dt[valid].min())).days
              / 30.44) if valid.any() else months_total
        for thr in thr_grid:
            dts, r, side, take = strategy(d, np.where(valid, pl, np.nan),
                                          np.where(valid, ps, np.nan), thr)
            s = summarise(dts, r, f"{mode} thr={thr}", mt)
            if s and s["n"] >= 100:
                s["mode"], s["thr"] = mode, thr
                rows.append(s)

    res = pd.DataFrame(rows)
    print(f"\n{'mode':>5}{'thr':>7}{'n':>7}{'expR':>8}{'mo_R':>8}{'maxDD_R':>9}"
          f"{'ratio':>7}{'pos%':>6}{'risk%':>7}{'mo_ret%':>9}")
    for _, r_ in res.iterrows():
        print(f"{r_['mode']:>5}{r_.thr:>7.2f}{int(r_.n):>7}{r_.exp_r:>8.3f}"
              f"{r_.monthly_R:>8.2f}{r_.maxDD_R:>9.1f}{r_.ratio:>7.2f}"
              f"{100*r_.pos_months:>5.0f}%{100*r_.risk_pct:>6.2f}%"
              f"{100*r_.monthly_ret:>8.2f}%")
    return res, d, (wf_l, wf_s, is_l, is_s)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--hold", type=int, default=60)
    a = p.parse_args()
    res, _, _ = run(a.tf, a.hold)
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    res.to_csv(os.path.join(rep, f"ml_{a.tf}.csv"), index=False)
    print("\nNOTE: 'risk%' is the per-trade risk implied by sizing the worst")
    print("observed drawdown to exactly 6%, and 'mo_ret%' the monthly return")
    print("that sizing yields. That is the honest translation to the target.")
