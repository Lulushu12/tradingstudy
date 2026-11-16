"""Phase 3 discovery: walk-forward search for readable rules (<= 2 conditions) on the v2 event families.
Declared in PROTOCOL.md ("Phase 3 discovery plan"). Every procedure is logged in LEDGER.md (P3-xxx).
Usage: uv run python -m tradingstudy.phase3.discovery
"""
from __future__ import annotations

import itertools
import json
import time

import numpy as np
import pandas as pd

from tradingstudy.backtest.cache import load_cached
from tradingstudy.backtest.signals import flip_signals_v2, stack_signals_v2
from tradingstudy.backtest.stats import FOLDS, deflated_sharpe
from tradingstudy.config import DATA, DEV_END, REPORTS, SYMBOLS
from tradingstudy.features.build import EXEC_TFS
from tradingstudy.phase2.baselines import evaluate, m1_arrays, simulate_coin

OUT = REPORTS / "phase3"
RES = DATA / "results" / "phase3"
TFS = ["15m", "24m", "1h"]
EMBARGO = pd.Timedelta(days=7)
MIN_TRAIN_TRADES = 100
NUMERIC = ["atr_pctile_30d", "funding_z_rel", "cmf_rel", "cmf4h_rel", "confluence_types", "sr_dist"]
CATEG = {"r1_rel": [-1.0, 0.0, 1.0], "r2_rel": [-1.0, 0.0, 1.0], "htf_near_cross_rel": [0.0, 1.0],
         "htf_mf_rel": [0.0, 1.0], "session": ["asia", "europe", "us", "late"], "fib_exec_in_0618_zone": [0.0, 1.0]}


def pooled_flips(df: pd.DataFrame, ev: pd.DataFrame, tf: str, variant: str) -> pd.DataFrame:
    labels = [tf] + [f"{r}>{tf}" for r, m in (("1h", 60), ("4h", 240)) if m > EXEC_TFS[tf]]
    parts = [flip_signals_v2(df, ev, lab, variant) for lab in labels]
    sig = pd.concat([p for p in parts if len(p)])
    if sig.empty:
        return sig
    g = sig.groupby(level=0)["direction"].agg(["min", "max"])
    keep = g.index[g["min"] == g["max"]]
    sig = sig[sig.index.isin(keep)]
    return sig[~sig.index.duplicated(keep="first")].sort_index()


def attach_features(sig: pd.DataFrame, df: pd.DataFrame, tf: str) -> pd.DataFrame:
    x = df.loc[sig.index]
    d = sig["direction"].to_numpy()
    f = pd.DataFrame(index=sig.index)
    f["r1_rel"] = x["r1_trend"].to_numpy() * d + 0.0
    f["r2_rel"] = x["r2_trend"].to_numpy() * d + 0.0
    f["htf_near_cross_rel"] = np.where(d == 1, x["htf_near_cross_bull"], x["htf_near_cross_bear"]).astype(float)
    f["htf_mf_rel"] = np.where(d == 1, x["htf_mf_rising"], ~x["htf_mf_rising"].astype(bool)).astype(float)
    f["atr_pctile_30d"] = x["atr_pctile_30d"].to_numpy()
    f["session"] = x["session"].to_numpy()
    f["funding_z_rel"] = x["funding_z"].to_numpy() * d
    f["cmf_rel"] = x["cmf"].to_numpy() * d
    f["cmf4h_rel"] = x["cmf_4h"].to_numpy() * d
    f["confluence_types"] = x["confluence_types"].to_numpy()
    f["fib_exec_in_0618_zone"] = x["fib_exec_in_0618_zone"].to_numpy()
    f["sr_dist"] = np.abs(x[f"sr_{tf}_dist_atr"].to_numpy())
    return f


def dataset(family: str, tf: str, variant: str, arrays: dict, target: str = "2R") -> pd.DataFrame:
    rows = []
    for s in SYMBOLS:
        df, ev = load_cached(s, tf, defs="v2")
        sig = stack_signals_v2(df, variant) if family == "stack" else pooled_flips(df, ev, tf, variant)
        if sig.empty:
            continue
        sim = simulate_coin(s, sig, EXEC_TFS[tf], "structure", target, arrays[s])
        feats = attach_features(sig, df, tf).reset_index(drop=True)
        rows.append(pd.concat([sim.reset_index(drop=True), feats.drop(columns=[c for c in feats if c in sim])], axis=1))
    return pd.concat(rows, ignore_index=True)


# ---------------- rule search ----------------
def conditions(train: pd.DataFrame) -> list[tuple]:
    conds = []
    for c in NUMERIC:
        v = train[c].dropna()
        if len(v) < 10:
            continue
        q33, q67 = np.quantile(v, [1 / 3, 2 / 3])
        conds += [(c, "le", q33), (c, "le", q67), (c, "gt", q33), (c, "gt", q67)]
    for c, vals in CATEG.items():
        conds += [(c, "eq", v) for v in vals]
    return conds


def cond_mask(df: pd.DataFrame, cond: tuple) -> np.ndarray:
    c, op, v = cond
    x = df[c]
    if op == "le":
        return (x <= v).to_numpy()
    if op == "gt":
        return (x > v).to_numpy()
    return (x == v).to_numpy()


def search(train: pd.DataFrame) -> dict:
    """Best rule by training expectancy (filled trades' net R) among rules with >= MIN_TRAIN_TRADES trades."""
    t = train[train["status"] == 0]
    y = t["net_R"].to_numpy()
    conds = conditions(t)
    M = np.column_stack([cond_mask(t, c) for c in conds]).astype(np.float64)
    cnt = M.T @ M
    sm = M.T @ (M * y[:, None])
    best = {"rule": (), "n": len(y), "exp": float(y.mean()) if len(y) else -np.inf}
    feat = [c[0] for c in conds]
    for i, j in itertools.combinations_with_replacement(range(len(conds)), 2):
        if i != j and feat[i] == feat[j]:
            continue
        n = cnt[i, j]
        if n < MIN_TRAIN_TRADES:
            continue
        e = sm[i, j] / n
        k = 1 if i == j else 2
        if e > best["exp"] + 1e-12 or (abs(e - best["exp"]) <= 1e-12 and k < len(best["rule"])):
            best = {"rule": (conds[i],) if i == j else (conds[i], conds[j]), "n": int(n), "exp": float(e)}
    return best


def apply_rule(df: pd.DataFrame, rule: tuple) -> np.ndarray:
    m = np.ones(len(df), dtype=bool)
    for c in rule:
        m &= cond_mask(df, c)
    return m


def rule_key(rule: tuple) -> tuple:
    """Same features and directions of conditions (thresholds may differ) = same rule for S10."""
    return tuple(sorted((c, op, v if op == "eq" else None) for c, op, v in rule))


def rule_text(rule: tuple) -> str:
    if not rule:
        return "no filter"
    f = lambda c, op, v: f"{c} {'<=' if op == 'le' else '>' if op == 'gt' else '=='} {v:.3g}" if op != "eq" else f"{c} == {v}"
    return " AND ".join(f(*c) for c in rule)


def run_procedure(cfg: dict, data: pd.DataFrame) -> tuple[dict, pd.DataFrame, list]:
    sig_t = pd.to_datetime(data["sig_ts"], utc=True)
    end_t = pd.to_datetime(data["end_ts"], utc=True)
    picked, folds = [], []
    for name, a, b in FOLDS:
        a, b = pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")
        cut = a - EMBARGO
        train = data[(sig_t < cut) & (end_t < cut)]
        best = search(train)
        test = data[(sig_t >= a) & (sig_t < b)]
        sel = test[apply_rule(test, best["rule"])]
        picked.append(sel)
        folds.append({"fold": name, "rule": rule_text(best["rule"]), "key": rule_key(best["rule"]),
                      "train_n": best["n"], "train_exp": best["exp"], "test_signals": len(test), "test_selected": len(sel)})
    cut = DEV_END - EMBARGO
    final = search(data[(sig_t < cut) & (end_t < cut)])
    fkey = rule_key(final["rule"])
    stability = sum(1 for f in folds if f["key"] == fkey)
    oos = pd.concat(picked, ignore_index=True)
    res, trades = evaluate(cfg, oos)
    res.update({"final_rule": rule_text(final["rule"]), "final_train_n": final["n"], "final_train_exp": final["exp"],
                "rule_stability": stability, "fold_rules": [{k: v for k, v in f.items() if k != "key"} for f in folds]})
    return res, trades, folds


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    cfgs = []
    for fam in ("stack", "flips"):
        for tf in TFS:
            for var in ("A", "B"):
                cfgs.append(dict(family=fam, tf=tf, variant=var, stop="structure", target="2R", htf=None))
    for i, c in enumerate(cfgs):
        c["id"] = f"P3-{i + 1:03d}"
    results, all_trades = [], []
    for c in cfgs:
        data = dataset(c["family"], c["tf"], c["variant"], arrays)
        res, trades, folds = run_procedure(c, data)
        results.append(res)
        all_trades.append(trades)
        w = res["wf"]
        print(f"{c['id']} {c['family']:5s} {c['tf']:3s} {c['variant']} n={w.get('n', 0):5d} exp={w.get('exp_R', np.nan):+.3f} "
              f"gross={w.get('gross_R', np.nan):+.3f} pf={w.get('pf', np.nan):.2f} stab={res['rule_stability']}/6 "
              f"final: {res['final_rule']} [{time.time() - t0:.0f}s]", flush=True)
    prev = []
    for fn in ("baseline_results.json", "baseline_v2_results.json"):
        prev += json.loads((REPORTS / "phase2" / fn).read_text())["results"]
    srs = np.array([r["wf"].get("sr", np.nan) for r in prev + results], dtype=float)
    var_sr, n_trials = float(np.nanvar(srs, ddof=1)), len(prev) + len(results)
    for r in results:
        w = r["wf"]
        r["dsr"] = deflated_sharpe(w.get("sr", np.nan), w.get("n", 0), w.get("skew", 0.0), w.get("kurt", 3.0), n_trials, var_sr)
    pd.concat(all_trades, ignore_index=True).to_parquet(RES / "trades.parquet")
    (OUT / "discovery_results.json").write_text(json.dumps({"n_trials_total": n_trials, "sr_var_trials": var_sr,
                                                            "results": results}, indent=1, default=str))
    print("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
