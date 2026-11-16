"""Phase 2: run the frozen baselines (PROTOCOL sections 5, 8). Every configuration is logged in LEDGER.md.

Families: B1 divergence stack (98 configs), B2 plain range flip (98), B3 HTF layer filters on B1 (16, reference label).
Evaluation window = the walk-forward test period 2023-01-01 to 2025-11-14 (baselines have no fitted parameters,
so the rule is identical in every fold). 2022 is reported separately for information.
Usage: uv run python -m tradingstudy.phase2.baselines
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from tradingstudy.backtest import engine as E
from tradingstudy.backtest.cache import load_cached
from tradingstudy.backtest.costs import SLIPPAGE, tick_for
from tradingstudy.backtest.portfolio import run_portfolio
from tradingstudy.backtest.signals import TARGETS, flip_signals, stack_signals, target_prices
from tradingstudy.backtest.stats import FOLDS, WF_END, WF_START, core, deflated_sharpe, prop_monte_carlo, summarize
from tradingstudy.config import DATA, DEV_START, REPORTS, SYMBOLS
from tradingstudy.data.guard import load_bars
from tradingstudy.features.build import EXEC_TFS

OUT = REPORTS / "phase2"
RES = DATA / "results" / "phase2"
NON_BTC = [s for s in SYMBOLS if s != "BTC"]


def stops_for(tf: str) -> list[float]:
    return [2.0] if tf == "6m" else [1.5, 2.0]


def config_list() -> list[dict]:
    cfgs = []
    for fam in ("B1", "B2"):
        for tf in EXEC_TFS:
            for var in ("A", "B"):
                for m in stops_for(tf):
                    for t in TARGETS:
                        cfgs.append(dict(family=fam, tf=tf, variant=var, stop=m, target=t, htf=None))
    for tf in EXEC_TFS:
        for var in ("A", "B"):
            for h in ("near_cross", "mf_dir"):
                cfgs.append(dict(family="B3", tf=tf, variant=var, stop=stops_for(tf)[0], target="2R", htf=h))
    for i, c in enumerate(cfgs):
        c["id"] = f"P2-{i + 1:03d}"
    return cfgs


def m1_arrays(sym: str) -> dict:
    m = load_bars(sym, "1m", "dev")
    return {"ts": m.index.as_unit("ns").asi8, "o": m["open"].to_numpy(), "h": m["high"].to_numpy(),
            "l": m["low"].to_numpy(), "c": m["close"].to_numpy()}


def simulate_coin(sym: str, sig: pd.DataFrame, minutes: int, stop: float, target: str, A: dict) -> pd.DataFrame:
    if sig.empty:
        return pd.DataFrame()
    sig_ts = (sig.index + pd.Timedelta(minutes=minutes)).as_unit("ns").asi8
    start = np.searchsorted(A["ts"], sig_ts, side="left")
    sd = sig["stop_dist"].to_numpy(np.float64) if stop == "structure" else stop * sig["atr14"].to_numpy()
    tgt = target_prices(sig, sd, target)
    ticks = np.array([tick_for(sym, y) for y in sig.index.year], dtype=float)
    slip = np.full(len(sig), SLIPPAGE[sym])
    out = E.simulate(A["ts"], A["o"], A["h"], A["l"], A["c"], start.astype(np.int64), sig_ts.astype(np.int64),
                     sig["direction"].to_numpy(np.int64), sig["close"].to_numpy(np.float64), sd.astype(np.float64),
                     tgt.astype(np.float64), ticks, slip, E.FEE_RATE)
    r = pd.DataFrame(out, columns=E.COLS)
    r["status"] = r["status"].astype(int)
    r["coin"] = sym
    r["sig_ts"] = sig_ts
    r["direction"] = sig["direction"].to_numpy()
    r["r1_rel"] = sig["r1_trend"].to_numpy() * r["direction"] + 0.0  # + 0.0 turns -0.0 into 0.0
    r["r2_rel"] = sig["r2_trend"].to_numpy() * r["direction"] + 0.0
    r["session"] = sig["session"].to_numpy()
    for c in ("fill_ts", "end_ts"):
        r[c] = r[c].fillna(r["sig_ts"]).astype("int64")
    return r


def breakdown(f: pd.DataFrame, col: str) -> dict:
    return {str(k): {"n": int(len(g)), "exp_R": round(float(g["net_R"].mean()), 4)} for k, g in f.groupby(col)}


def evaluate(cfg: dict, sims: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    s, acct = run_portfolio(sims)
    t = pd.to_datetime(s["sig_ts"], utc=True)
    wf = s[(t >= WF_START) & (t < WF_END)]
    y22 = s[(t >= DEV_START) & (t < WF_START)]
    days = (WF_END - WF_START).days
    res = {**cfg, "wf": summarize(wf, days), "y2022": summarize(y22, 365), "account_full_dev": acct}
    f = wf[wf["taken"] & (wf["status"] == E.FILLED)].copy()
    ft = pd.to_datetime(f["fill_ts"], utc=True)
    res["folds"] = {name: core(f.loc[(ft >= a) & (ft < b), "net_R"]).get("exp_R", np.nan) for name, a, b in FOLDS}
    res["folds_n"] = {name: int(((ft >= a) & (ft < b)).sum()) for name, a, b in FOLDS}
    coins = {c: core(g["net_R"]) for c, g in f.groupby("coin")}
    res["coins"] = {c: {"n": v["n"], "exp_R": v.get("exp_R"), "total_R": v.get("total_R")} for c, v in coins.items()}
    tot = f["net_R"].sum()
    res["max_coin_share"] = float(max((v.get("total_R", 0) for v in coins.values()), default=0) / tot) if tot > 0 else np.nan
    res["coins_positive"] = int(sum(1 for v in coins.values() if v.get("exp_R", -1) > 0))
    res["nonbtc_positive"] = int(sum(1 for c, v in coins.items() if c != "BTC" and v.get("exp_R", -1) > 0))
    res["regime_r1"] = breakdown(f, "r1_rel")
    res["regime_r2"] = breakdown(f, "r2_rel")
    res["session"] = breakdown(f, "session")
    res["mc"] = prop_monte_carlo(f, WF_START, WF_END, paths=10_000) if len(f) else {}
    f["config_id"] = cfg["id"]
    return res, f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    cfgs = config_list()
    print(f"{len(cfgs)} configurations", flush=True)
    t0 = time.time()
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    results, trades = [], []
    groups = {}
    for c in cfgs:
        groups.setdefault((c["family"], c["tf"], c["variant"], c["htf"]), []).append(c)
    for (fam, tf, var, htf), cs in groups.items():
        minutes = EXEC_TFS[tf]
        sigs = {}
        for s in SYMBOLS:
            df, ev = load_cached(s, tf)
            sigs[s] = flip_signals(df, ev, tf, var) if fam == "B2" else stack_signals(df, var, htf)
        for c in cs:
            sims = pd.concat([simulate_coin(s, sigs[s], minutes, c["stop"], c["target"], arrays[s]) for s in SYMBOLS],
                             ignore_index=True)
            res, f = evaluate(c, sims)
            res["signals"] = int(sum(len(v) for v in sigs.values()))
            results.append(res)
            trades.append(f)
            w = res["wf"]
            print(f"{c['id']} {fam} {tf} {var} stop{c['stop']} {c['target']:10s} {str(htf):10s} n={w.get('n', 0):5d} "
                  f"exp={w.get('exp_R', np.nan):+.3f} pf={w.get('pf', np.nan):.2f} fee={w.get('fee_R', np.nan):.3f} "
                  f"fill={w.get('fill_rate', np.nan):.2f} [{time.time() - t0:.0f}s]", flush=True)
    # deflated Sharpe with N = number of configurations evaluated so far (all 212 count)
    srs = np.array([r["wf"].get("sr", np.nan) for r in results], dtype=float)
    var_sr = float(np.nanvar(srs, ddof=1))
    for r in results:
        w = r["wf"]
        r["dsr"] = deflated_sharpe(w.get("sr", np.nan), w.get("n", 0), w.get("skew", 0.0), w.get("kurt", 3.0), len(results), var_sr)
    pd.concat(trades, ignore_index=True).to_parquet(RES / "trades.parquet")
    (OUT / "baseline_results.json").write_text(json.dumps({"n_configs": len(results), "sr_var_trials": var_sr,
                                                           "results": results}, indent=1, default=float))
    print("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
