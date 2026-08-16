"""Walk-forward LightGBM over the pooled 6-symbol matrix.

Protocol (leak-free):
  - Holdout = 2025-01-01 onward. NEVER touched until final eval.
  - Walk-forward validation inside pre-2025:
      folds validate on [2022-07..2022-12], [2023-01..06], [2023-07..12],
      [2024-01..06], [2024-07..12]; each trains on everything before its
      validation window minus an EMBARGO of MAX_H trading-TF bars.
  - Model: LightGBM binary, per target (long/short x 1:1/2:1), symbols pooled,
    sym as categorical.
  - Trade rule: prob > threshold. Threshold chosen ON VALIDATION to maximize
    total net R subject to >= MIN_TPM trades/month average.
  - Report: per-fold val metrics, then ONE final fit on all pre-2025 and ONE
    pass over the holdout at the frozen threshold.

Outputs: data/ml_{ival}_{target}.json summary + holdout trade list parquet.
"""
import sys, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import lightgbm as lgb
import core

EMBARGO_BARS = core.MAX_H
MIN_TPM = 5          # min avg trades/month across pooled symbols for a threshold
THRESH_GRID = np.round(np.arange(0.50, 0.86, 0.01), 2)

META = {"sym", "dt", "entry", "stop_dist", "feeR",
        "long_y_11", "short_y_11", "long_y_21", "short_y_21"}

FOLDS = [("2022-07-01", "2023-01-01"), ("2023-01-01", "2023-07-01"),
         ("2023-07-01", "2024-01-01"), ("2024-01-01", "2024-07-01"),
         ("2024-07-01", "2025-01-01")]

PARAMS = dict(objective="binary", learning_rate=0.03, num_leaves=63,
              min_data_in_leaf=200, feature_fraction=0.7, bagging_fraction=0.8,
              bagging_freq=1, lambda_l2=5.0, verbosity=-1, num_boost_round=600)

def bar_hours(ival):
    return {"15m": 0.25, "1h": 1.0, "4h": 4.0}[ival]

def prep(ival):
    M = pd.read_parquet(f"{core.DATA}/matrix_{ival}.parquet")
    M["sym_cat"] = M["sym"].astype("category")
    feats = [c for c in M.columns if c not in META and c != "sym_cat"]
    return M, feats + ["sym_cat"]

def fit_predict(M, feats, target, rr, tr_mask, te_mask):
    y = M[target]
    tr = tr_mask & y.notna()
    te = te_mask & y.notna()
    dtr = lgb.Dataset(M.loc[tr, feats], label=y[tr].astype(int),
                      categorical_feature=["sym_cat"])
    booster = lgb.train(PARAMS, dtr)
    p = booster.predict(M.loc[te, feats])
    return booster, p, te

def eval_threshold(M, te_idx, p, target, rr, thresh):
    sel = p > thresh
    if sel.sum() == 0:
        return None
    g = M.loc[te_idx].iloc[np.where(sel)[0]] if False else M.loc[te_idx][sel]
    y = g[target].values
    fee = g["feeR"].values
    r = np.where(y == 1, rr, -1.0) - fee
    months = max((g["dt"].max() - g["dt"].min()).days / 30.4, 1e-9)
    return {"thresh": float(thresh), "n": int(len(g)),
            "tpm": round(len(g) / months, 1), "wr": round(float(np.mean(y)), 4),
            "expR": round(float(np.mean(r)), 4), "totR": round(float(np.sum(r)), 1)}

def run_target(M, feats, ival, side, tag):
    target = f"{side}_y_{tag}"
    rr = 1.0 if tag == "11" else 2.0
    emb = pd.Timedelta(hours=EMBARGO_BARS * bar_hours(ival))
    fold_stats = []
    val_p_all, val_idx_all = [], []
    for v0, v1 in FOLDS:
        v0, v1 = pd.Timestamp(v0, tz="UTC"), pd.Timestamp(v1, tz="UTC")
        tr_mask = M["dt"] < (v0 - emb)
        te_mask = (M["dt"] >= v0) & (M["dt"] < v1)
        _, p, te = fit_predict(M, feats, target, rr, tr_mask, te_mask)
        val_p_all.append(p); val_idx_all.append(M.index[te])
        auc_bins = pd.qcut(p, 5, duplicates="drop")
        wr_by_bin = pd.Series(M.loc[te, target].values).groupby(auc_bins, observed=True).mean()
        fold_stats.append({"fold": str(v0.date()),
                           "monotone": round(float(wr_by_bin.iloc[-1] - wr_by_bin.iloc[0]), 4)})
    p_val = np.concatenate(val_p_all)
    idx_val = val_idx_all[0].append(val_idx_all[1:])
    # threshold selection on pooled validation predictions
    best = None
    for th in THRESH_GRID:
        s = eval_threshold(M, idx_val, p_val, target, rr, th)
        if s is None or s["tpm"] < MIN_TPM:
            continue
        if best is None or s["totR"] > best["totR"]:
            best = s
    result = {"ival": ival, "target": target, "folds": fold_stats,
              "val_best": best}
    if best is None:
        result["holdout"] = None
        return result
    # final: train on ALL pre-2025 (minus embargo), evaluate holdout once
    tr_mask = M["dt"] < (core.TEST_START - emb)
    te_mask = M["dt"] >= core.TEST_START
    booster, p, te = fit_predict(M, feats, target, rr, tr_mask, te_mask)
    hold = eval_threshold(M, M.index[te], p, target, rr, best["thresh"])
    result["holdout"] = hold
    imp = sorted(zip(booster.feature_name(), booster.feature_importance("gain")),
                 key=lambda x: -x[1])[:15]
    result["top_features"] = [[f, round(float(g), 0)] for f, g in imp]
    # save holdout trades for portfolio sim
    g = M.loc[M.index[te]][p > best["thresh"]]
    tl = g[["sym", "dt", "entry", "stop_dist", "feeR", target]].copy()
    tl["p"] = p[p > best["thresh"]]
    tl["side"] = side; tl["rr"] = rr
    tl.rename(columns={target: "y"}).to_parquet(
        f"{core.DATA}/trades_{ival}_{side}_{tag}.parquet")
    return result

if __name__ == "__main__":
    ival = sys.argv[1] if len(sys.argv) > 1 else "1h"
    M, feats = prep(ival)
    out = {}
    for side in ("long", "short"):
        for tag in ("11", "21"):
            r = run_target(M, feats, ival, side, tag)
            out[f"{side}_{tag}"] = r
            print(json.dumps(r, indent=1), flush=True)
    with open(f"{core.DATA}/ml_{ival}.json", "w") as f:
        json.dump(out, f, indent=1)
