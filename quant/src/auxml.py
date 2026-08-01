"""Does funding / open interest / positioning data add walk-forward edge?

The controlled experiment the original study could not run, because it never
had these series. Three feature sets, identical everything else:

    BASE  71 OHLCV + taker-flow features (the original study)
    AUX   40 funding / open-interest / positioning / basis features only
    BOTH  all 111

Same labels, same purged walk-forward, same costs, same portfolio construction.
If AUX is flat and BOTH does not beat BASE, the earlier "no edge" conclusion
survives the criticism that it was tested on the wrong data. If BOTH beats BASE
out of sample, the earlier conclusion was data-limited and must be revised.
"""
import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import features as F      # noqa: E402
import labels as L        # noqa: E402
import auxfeat as A       # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
# every symbol with both 1m klines and the auxiliary series. Breadth was the
# constraint proved binding early (5 assets at rho=0.30 gave 2.27 effective
# independent streams) and never acted on until now.
_AUXDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "aux")
SYMS = sorted({f.split("_")[0] for f in os.listdir(_AUXDIR)
               if f.endswith("_metrics.parquet")}) if os.path.isdir(_AUXDIR) else []

SHALLOW = dict(objective="regression", learning_rate=0.03, num_leaves=16,
               max_depth=4, min_data_in_leaf=500, feature_fraction=0.7,
               bagging_fraction=0.8, bagging_freq=1, lambda_l2=20.0,
               verbosity=-1, num_threads=4)


def build(tf="1h", hold=96, atr_mult=2.0, rr=2.0, syms=None):
    syms = syms or SYMS
    frames = []
    for s in syms:
        if not os.path.exists(os.path.join(A.AUX, f"{s}_metrics.parquet")):
            print(f"  {s}: no aux data, skipped")
            continue
        bars, m1 = D.load(s, tf, "DESIGN")
        base = F.build(bars, m1, tf)
        merged = A.attach(bars, s, tf)
        aux = A.features(merged)
        aux.index = base.index[:len(aux)] if len(aux) == len(base) else aux.index
        lb = L.make(s, tf, "DESIGN", atr_mult=atr_mult, rr=rr, max_hold_bars=hold)

        d = pd.concat([base.reset_index(drop=True),
                       aux.reset_index(drop=True).add_prefix("ax_")], axis=1)
        d = d[base["tradeable"].values].reset_index(drop=True)
        kf = d["dt"].astype("int64").values
        kl = lb["dt"].astype("int64").values
        common = np.intersect1d(kf, kl)
        d = d[np.isin(kf, common)].reset_index(drop=True)
        lbs = lb[np.isin(kl, common)].reset_index(drop=True)
        for c in ("r_long", "r_short", "out_long", "out_short"):
            d[c] = lbs[c].values
        d["symbol"] = s
        frames.append(d)
    return pd.concat(frames, ignore_index=True).sort_values("dt").reset_index(drop=True)


def split_features(d):
    drop = {"dt", "close", "tradeable", "open_next", "atr", "symbol", "ret",
            "r_long", "r_short", "out_long", "out_short"}
    allf = [c for c in d.columns if c not in drop]
    aux = [c for c in allf if c.startswith("ax_")]
    base = [c for c in allf if not c.startswith("ax_")]
    return base, aux, allf


def walkforward(d, feats, target, train_months=24, step_months=3, embargo=200):
    dt = pd.DatetimeIndex(d.dt)
    y = d[target].values.astype(float)
    X = np.nan_to_num(d[feats].values.astype(np.float32), nan=0.0)
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
        idx = np.where(trm)[0]
        if len(idx) > embargo * 6:
            trm[idx[-embargo:]] = False
        tem = (dt >= tr_hi) & (dt < te_hi)
        if trm.sum() > 5000 and tem.sum() > 0:
            b = lgb.train(SHALLOW, lgb.Dataset(X[trm], label=y[trm],
                                               feature_name=feats), 250)
            pred[tem] = b.predict(X[tem])
        i += step_months
    return pred


def evaluate(d, pl, ps, label, thr_grid=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0)):
    months = (pd.Timestamp(d.dt.max()) - pd.Timestamp(d.dt.min())).days / 30.44
    rl, rs = d.r_long.values, d.r_short.values
    score = np.where(pl >= ps, pl, ps)
    side = np.where(pl >= ps, 1, -1)
    r = np.where(side > 0, rl, rs)
    out = []
    for thr in thr_grid:
        m = np.isfinite(score) & (score >= thr) & np.isfinite(r)
        if m.sum() < 200:
            continue
        sel = r[m]
        cum = np.cumsum(sel)
        dd = float(np.max(np.maximum.accumulate(cum) - cum))
        moR = sel.sum() / months
        out.append({"set": label, "thr": thr, "n": int(m.sum()),
                    "expR": float(sel.mean()), "moR": moR, "ddR": dd,
                    "ratio": moR / dd if dd > 0 else np.nan,
                    "monthly_ret": min(0.06 / dd, 0.02) * moR if dd > 0 else 0.0})
    return out


def main(tf="1h", hold=96):
    d = build(tf=tf, hold=hold)
    base, aux, allf = split_features(d)
    print(f"=== {tf}: {len(d):,} rows, {d.symbol.nunique()} symbols ===")
    print(f"    BASE {len(base)} features | AUX {len(aux)} features | "
          f"BOTH {len(allf)}")
    print(f"    unconditional expR: long {np.nanmean(d.r_long):+.4f}  "
          f"short {np.nanmean(d.r_short):+.4f}")

    rows = []
    booster_gain = {}
    for name, feats in (("BASE", base), ("AUX", aux), ("BOTH", allf)):
        pl = walkforward(d, feats, "r_long")
        ps = walkforward(d, feats, "r_short")
        rows += evaluate(d, pl, ps, name)
        # in-sample importance, for the feature story only
        ok = np.isfinite(d.r_long.values)
        X = np.nan_to_num(d[feats].values.astype(np.float32), nan=0.0)
        b = lgb.train(SHALLOW, lgb.Dataset(X[ok], label=d.r_long.values[ok],
                                           feature_name=feats), 250)
        booster_gain[name] = pd.Series(b.feature_importance("gain"),
                                       index=feats).sort_values(ascending=False)

    res = pd.DataFrame(rows)
    print(f"\n{'set':>6}{'thr':>6}{'n':>8}{'expR':>9}{'monthly R':>11}"
          f"{'maxDD R':>10}{'ratio':>8}{'%/mo @6% floor':>16}")
    for _, r in res.iterrows():
        print(f"{r['set']:>6}{r.thr:>6.1f}{int(r.n):>8}{r.expR:>9.4f}"
              f"{r.moR:>11.2f}{r.ddR:>10.1f}{r.ratio:>8.3f}"
              f"{100*r.monthly_ret:>15.2f}%")

    print(f"\ntop AUX features by in-sample gain:")
    for k, v in booster_gain["AUX"].head(12).items():
        print(f"   {k:<24}{v:>12.0f}")
    print(f"\ntop features overall (BOTH), aux marked *:")
    for k, v in booster_gain["BOTH"].head(15).items():
        print(f"   {'*' if k.startswith('ax_') else ' '} {k:<24}{v:>12.0f}")
    n_aux_top = sum(1 for k in booster_gain["BOTH"].head(20).index
                    if k.startswith("ax_"))
    print(f"\n   {n_aux_top}/20 of the top features are auxiliary "
          f"({len(aux)}/{len(allf)} = {100*len(aux)/len(allf):.0f}% of the pool)")

    res.to_csv(os.path.join(REP, f"auxml_{tf}.csv"), index=False)
    best = res.groupby("set")["monthly_ret"].max()
    print(f"\n=== VERDICT (walk-forward, best threshold per set) ===")
    for k, v in best.items():
        print(f"   {k:<6} {100*v:+.3f}%/month")
    if "BOTH" in best and "BASE" in best:
        print(f"\n   adding auxiliary data changed walk-forward monthly return by "
              f"{100*(best['BOTH'] - best['BASE']):+.3f} percentage points")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="1h")
    p.add_argument("--hold", type=int, default=96)
    a = p.parse_args()
    main(a.tf, a.hold)
