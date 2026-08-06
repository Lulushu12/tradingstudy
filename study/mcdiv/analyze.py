"""Winner-vs-loser statistics and models on the trade feature table.

Per system (A, B, WTdiv, MFIdiv) and per R target (1:1, 2:1):
  1. mean/median of every oscillator feature for winners vs losers,
     Mann-Whitney U p-value and Cliff's delta effect size
  2. quintile winrate tables for the headline features
  3. L2 logistic regression (standardized) with time-ordered 5-fold CV AUC
  4. depth-3 decision tree rules (interpretability check)
  5. per-year winrate stability for any feature split that looks real
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

FEATURES = [
    # trigger-bar oscillator state (extremity: -direction*value, higher=deeper in favor)
    "x_trig_wt2", "x_trig_wt1", "x_trig_mfi",
    # divergence leg pivots and anchor (reference) pivots
    "x_wt_pivot_osc", "x_wt_anchor_osc", "x_mfi_pivot_osc", "x_mfi_anchor_osc",
    "x_wt_div_delta", "x_mfi_div_delta", "x_wt_div_price", "x_mfi_div_price",
    "wt_anchor_age", "mfi_anchor_age", "gap_bars",
    # higher-timeframe current state
    "x_h1_wt2", "x_h1_mfi", "x_h4_wt2", "x_h4_mfi",
    # higher-timeframe last completed wave
    "x_h1_wt2_wave", "x_h1_mfi_wave", "x_h4_wt2_wave", "x_h4_mfi_wave",
    "h1_wt2_wave_aligned", "h4_wt2_wave_aligned",
    "h1_wt2_wave_age", "h4_wt2_wave_age",
    # daily context and trend regimes
    "x_hd_wt2", "x_hd_mfi", "x_hd_wt2_wave", "x_hd_mfi_wave",
    "hd_wt2_wave_aligned", "hd_mfi_wave_aligned",
    "h4_trend_aligned", "hd_trend_aligned",
    "atr_pct",
]
HEADLINE = ["x_trig_wt2", "x_trig_mfi", "x_wt_pivot_osc", "x_wt_anchor_osc",
            "x_mfi_pivot_osc", "x_mfi_anchor_osc", "x_h1_wt2", "x_h4_wt2",
            "x_h1_mfi", "x_h4_mfi", "x_h1_wt2_wave", "x_h4_wt2_wave"]


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or len(b) == 0:
        return np.nan
    # efficient via ranks
    m, n = len(a), len(b)
    allv = np.concatenate([a, b])
    r = pd.Series(allv).rank().to_numpy()
    ra = r[:m].sum()
    u = ra - m * (m + 1) / 2
    return 2 * u / (m * n) - 1


def prep(df):
    df = df.copy()
    d = df["direction"].to_numpy(float)
    df["x_wt_div_delta"] = d * df.get("wt_div_osc_delta", np.nan)
    df["x_mfi_div_delta"] = d * df.get("mfi_div_osc_delta", np.nan)
    df["x_wt_div_price"] = -d * df.get("wt_div_price_pct", np.nan)
    df["x_mfi_div_price"] = -d * df.get("mfi_div_price_pct", np.nan)
    return df


def winner_loser_table(m, rr):
    y = m[f"win{rr}"]
    rows = []
    for f in FEATURES:
        if f not in m.columns:
            continue
        v = m[f].astype(float)
        w, l = v[(y == 1) & v.notna()], v[(y == 0) & v.notna()]
        if len(w) < 10 or len(l) < 10:
            continue
        try:
            p = mannwhitneyu(w, l, alternative="two-sided").pvalue
        except ValueError:
            p = np.nan
        rows.append(dict(feature=f, n_win=len(w), n_loss=len(l),
                         mean_win=w.mean(), mean_loss=l.mean(),
                         med_win=w.median(), med_loss=l.median(),
                         mw_p=p, cliffs_d=cliffs_delta(w, l)))
    t = pd.DataFrame(rows)
    return t.sort_values("mw_p") if len(t) else t


def quintile_table(m, rr, feats):
    y = m[f"win{rr}"]
    rows = []
    for f in feats:
        if f not in m.columns:
            continue
        v = m[f].astype(float)
        ok = v.notna() & y.notna()
        if ok.sum() < 100:
            continue
        try:
            q = pd.qcut(v[ok], 5, duplicates="drop")
        except ValueError:
            continue
        g = y[ok].groupby(q, observed=True)
        for interval, grp in g:
            rows.append(dict(feature=f, bucket=str(interval), n=len(grp),
                             winrate=grp.mean(),
                             avg_netR=m.loc[grp.index, f"netR{rr}"].mean()))
    return pd.DataFrame(rows)


def fit_models(m, rr):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.metrics import roc_auc_score

    feats = [f for f in FEATURES if f in m.columns and m[f].notna().mean() > 0.9]
    d = m.dropna(subset=feats + [f"win{rr}"]).sort_values("signal_i")
    if len(d) < 200:
        return None
    X = d[feats].astype(float).to_numpy()
    y = d[f"win{rr}"].to_numpy()
    if y.mean() in (0, 1):
        return None
    # time-ordered 5-fold CV
    aucs = []
    folds = np.array_split(np.arange(len(d)), 5)
    for k in range(1, 5):
        tr = np.concatenate(folds[:k])
        te = folds[k]
        sc = StandardScaler().fit(X[tr])
        lr = LogisticRegression(C=0.5, max_iter=2000).fit(sc.transform(X[tr]), y[tr])
        pv = lr.predict_proba(sc.transform(X[te]))[:, 1]
        if len(np.unique(y[te])) == 2:
            aucs.append(roc_auc_score(y[te], pv))
    sc = StandardScaler().fit(X)
    lr = LogisticRegression(C=0.5, max_iter=2000).fit(sc.transform(X), y)
    coef = pd.Series(lr.coef_[0], index=feats).sort_values(key=np.abs, ascending=False)
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=max(30, len(d) // 50),
                                  random_state=0).fit(X, y)
    rules = export_text(tree, feature_names=feats, decimals=1)
    return dict(n=len(d), base=y.mean(), cv_auc=np.mean(aucs) if aucs else np.nan,
                cv_auc_folds=[round(a, 3) for a in aucs], coef=coef, tree=rules)


def yearly_split(m, rr, feat, thresh):
    y = m[f"win{rr}"]
    v = m[feat].astype(float)
    rows = []
    for yr, grp in m.groupby("year"):
        hi = grp[(v.loc[grp.index] >= thresh)][f"win{rr}"]
        lo = grp[(v.loc[grp.index] < thresh)][f"win{rr}"]
        rows.append(dict(year=yr, n_hi=len(hi), wr_hi=hi.mean(),
                         n_lo=len(lo), wr_lo=lo.mean()))
    return pd.DataFrame(rows)


def main():
    m = prep(pd.read_parquet(os.path.join(OUT, "trades.parquet")))
    m = m[~m["skip"]]
    lines = []
    for system in ("A", "B", "WTdiv", "MFIdiv"):
        s = m[m["system"] == system]
        for rr in (1, 2):
            sub = s[s[f"win{rr}"].notna()]
            if len(sub) < 50:
                continue
            tag = f"{system}_rr{rr}"
            wl = winner_loser_table(sub, rr)
            wl.to_csv(os.path.join(OUT, f"stats_{tag}.csv"), index=False)
            qt = quintile_table(sub, rr, HEADLINE)
            qt.to_csv(os.path.join(OUT, f"quintiles_{tag}.csv"), index=False)
            mod = fit_models(sub, rr)
            lines.append(f"\n===== {system} @ {rr}:1  n={len(sub)} "
                         f"winrate={sub[f'win{rr}'].mean():.3f} "
                         f"avg_netR={sub[f'netR{rr}'].mean():+.3f} =====")
            if len(wl):
                lines.append(wl.head(12).to_string(index=False,
                             float_format=lambda x: f"{x:.3f}"))
            if mod:
                lines.append(f"logit time-CV AUC={mod['cv_auc']:.3f} folds={mod['cv_auc_folds']}"
                             f" (base wr {mod['base']:.3f}, n={mod['n']})")
                lines.append("top coefficients (standardized):")
                lines.append(mod["coef"].head(10).to_string(float_format=lambda x: f"{x:+.3f}"))
                lines.append("tree rules:\n" + mod["tree"])
    rep = "\n".join(lines)
    with open(os.path.join(OUT, "analysis_raw.txt"), "w") as fh:
        fh.write(rep)
    print(rep)


if __name__ == "__main__":
    main()
