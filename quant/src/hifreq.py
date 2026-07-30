"""High-frequency construction with a daily-loss-proof sizing rule.

The 3% daily limit, not the 6% floor, is what kills every aggressive config.
But it can be made unbreachable by construction: cap the number of positions
opened per day at k and risk exactly 3%/k on each. Then even if every trade
that day loses in full, the day loses exactly 3% and never more.

Under that rule:
    monthly return = f * (21k) * expR = (0.03/k) * 21k * expR = 0.63 * expR
which is INDEPENDENT of k, while monthly volatility falls as 1/sqrt(k).
So frequency is free variance reduction, and the whole problem collapses to:
find the highest expR obtainable at k trades per day.

The ranker is a deliberately SHALLOW booster (8 leaves, depth 3). The 400-tree
model used earlier reached +1.86R in-sample and +0.18R walk-forward purely by
memorising bar outcomes. A shallow model cannot do that, so the gap between its
in-sample and walk-forward numbers measures real structure rather than recall.
"""
import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402

SHALLOW = dict(objective="regression", learning_rate=0.05, num_leaves=8,
               max_depth=3, min_data_in_leaf=2000, feature_fraction=0.6,
               bagging_fraction=0.7, bagging_freq=1, lambda_l2=50.0,
               verbosity=-1, num_threads=4)


def fit_predict(d, feats, target, mode="IS", train_months=24, step_months=3,
                embargo=200, rounds=150, params=None):
    params = params or SHALLOW
    y = d[target].values.astype(float)
    X = d[feats].values.astype(np.float32)
    ok = np.isfinite(y)
    if mode == "IS":
        b = lgb.train(params, lgb.Dataset(X[ok], label=y[ok],
                                          feature_name=feats), rounds)
        return b.predict(X), b
    dt = pd.DatetimeIndex(d.dt)
    months = pd.period_range(dt.min(), dt.max(), freq="M")
    pred = np.full(len(d), np.nan)
    i = train_months
    while i < len(months):
        tr_hi = months[i].start_time.tz_localize("UTC")
        te_hi = months[min(i + step_months, len(months) - 1)].start_time.tz_localize("UTC")
        if te_hi <= tr_hi:
            break
        trm = (dt < tr_hi) & ok
        idx = np.where(trm)[0]
        if len(idx) > embargo * 6:
            trm[idx[-embargo:]] = False
        tem = (dt >= tr_hi) & (dt < te_hi)
        if trm.sum() > 5000 and tem.sum() > 0:
            b = lgb.train(params, lgb.Dataset(X[trm], label=y[trm],
                                              feature_name=feats), rounds)
            pred[tem] = b.predict(X[tem])
        i += step_months
    return pred, None


def select_daily_topk(d, score, side_arr, k):
    """Keep the k best-scoring (bar, side) candidates each calendar day."""
    dt = pd.DatetimeIndex(d.dt)
    day = (dt.floor("D") - dt.floor("D").min()).days.values
    order = np.lexsort((-score, day))
    keep = np.zeros(len(d), dtype=bool)
    cnt = {}
    for i in order:
        if not np.isfinite(score[i]):
            continue
        c = cnt.get(day[i], 0)
        if c >= k:
            continue
        cnt[day[i]] = c + 1
        keep[i] = True
    return keep


def evaluate(d, keep, side_arr, k, label):
    """Sizing is f = 3%/k, which makes a daily breach impossible by construction."""
    r = np.where(side_arr > 0, d.r_long.values, d.r_short.values)
    m = keep & np.isfinite(r)
    n = int(m.sum())
    if n < 200:
        return None
    f = 0.03 / k
    dt = pd.DatetimeIndex(d.dt)
    ser = pd.Series(np.where(m, r, 0.0), index=dt).sort_index()
    daily = ser.resample("D").sum()
    monthly = ser.resample("ME").sum()
    span_months = (dt.max() - dt.min()).days / 30.44

    # compounding equity, static floor at 6%
    eq, floor, curve = 1.0, 0.94, []
    peak, mdd, breach = 1.0, 0.0, None
    day_start = 1.0
    for day, v in daily.items():
        eq_new = eq * (1 + f * v)
        if eq_new <= day_start * 0.97 - 1e-12 and breach is None:
            breach = ("daily", day)
        eq = eq_new
        day_start = eq
        peak = max(peak, eq)
        mdd = max(mdd, (peak - eq) / peak)
        if eq <= floor and breach is None:
            breach = ("static", day)
        curve.append(eq)
    curve = pd.Series(curve, index=daily.index)
    mo_ret = curve.resample("ME").last().pct_change().dropna()

    return {"label": label, "k": k, "n": n, "trades_per_day": n / max(len(daily), 1),
            "exp_r": float(np.mean(r[m])), "risk_pct": f,
            "monthly_R": float(monthly.sum() / span_months),
            "mean_mo": float(mo_ret.mean()), "median_mo": float(mo_ret.median()),
            "worst_mo": float(mo_ret.min()), "pos_mo": float((mo_ret > 0).mean()),
            "ge10_mo": float((mo_ret >= 0.10).mean()),
            "worst_day_R": float(daily.min()), "worst_day_ret": float(f * daily.min()),
            "total": float(curve.iloc[-1] - 1), "maxDD": mdd, "breach": breach,
            "cagr": float(curve.iloc[-1] ** (365.25 / max((daily.index[-1] - daily.index[0]).days, 1)) - 1)}


def run(tf="30min", hold=96, ks=(4, 8, 16, 24), modes=("IS", "WF")):
    d = DS.build(tf=tf, hold=hold)
    feats = DS.feature_list(d)
    print(f"=== {tf}: rows {len(d):,}  feats {len(feats)} ===")
    out = []
    for mode in modes:
        print(f"\n  fitting {mode} ...")
        pl, _ = fit_predict(d, feats, "r_long", mode=mode)
        ps, _ = fit_predict(d, feats, "r_short", mode=mode)
        score = np.where(pl >= ps, pl, ps)
        side = np.where(pl >= ps, 1, -1)
        for k in ks:
            keep = select_daily_topk(d, score, side, k)
            m = evaluate(d, keep, side, k, f"{mode} k={k}")
            if m:
                out.append(m)
                print(f"    k={k:<3} n={m['n']:<6} expR {m['exp_r']:+.3f} "
                      f"risk {100*m['risk_pct']:.3f}%  mean/mo {100*m['mean_mo']:+6.2f}% "
                      f"worst/mo {100*m['worst_mo']:+6.2f}%  pos {100*m['pos_mo']:.0f}% "
                      f">=10% {100*m['ge10_mo']:.0f}%  CAGR {100*m['cagr']:.0f}%  "
                      f"maxDD {100*m['maxDD']:.1f}%  breach={m['breach']}")
    return pd.DataFrame(out), d


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="30min")
    p.add_argument("--hold", type=int, default=96)
    a = p.parse_args()
    res, d = run(a.tf, a.hold)
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    res.to_csv(os.path.join(rep, f"hifreq_{a.tf}.csv"), index=False)
