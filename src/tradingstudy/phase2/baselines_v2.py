"""Phase 2 re-run with the Amendment 1 definitions (166 configurations, ids P2-213..P2-378).

Families: B1v2 divergence stack (42), B2v2 same-TF range flip (42), B4 higher-TF range flip (70), B3v2 HTF layer on
B1v2 (12, reference label 2R). Structure stops everywhere. Deflated Sharpe uses N = all 378 Phase 2 configurations.
Usage: uv run python -m tradingstudy.phase2.baselines_v2
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from tradingstudy.backtest.cache import load_cached
from tradingstudy.backtest.signals import TARGETS, flip_signals_v2, stack_signals_v2
from tradingstudy.backtest.stats import deflated_sharpe
from tradingstudy.config import DATA, REPORTS, SYMBOLS
from tradingstudy.features.build import EXEC_TFS
from tradingstudy.phase2.baselines import evaluate, m1_arrays, simulate_coin

OUT = REPORTS / "phase2"
RES = DATA / "results" / "phase2"
TFS = ["15m", "24m", "1h"]
PAIRS = [("1h", "15m"), ("4h", "15m"), ("1h", "24m"), ("4h", "24m"), ("4h", "1h")]
FIRST_ID = 213


def config_list() -> list[dict]:
    cfgs = []
    for tf in TFS:
        for var in ("A", "B"):
            for t in TARGETS:
                cfgs.append(dict(family="B1v2", tf=tf, rtf=None, variant=var, stop="structure", target=t, htf=None))
    for tf in TFS:
        for var in ("A", "B"):
            for t in TARGETS:
                cfgs.append(dict(family="B2v2", tf=tf, rtf=tf, variant=var, stop="structure", target=t, htf=None))
    for rtf, tf in PAIRS:
        for var in ("A", "B"):
            for t in TARGETS:
                cfgs.append(dict(family="B4", tf=tf, rtf=rtf, variant=var, stop="structure", target=t, htf=None))
    for tf in TFS:
        for var in ("A", "B"):
            for h in ("near_cross", "mf_dir"):
                cfgs.append(dict(family="B3v2", tf=tf, rtf=None, variant=var, stop="structure", target="2R", htf=h))
    for i, c in enumerate(cfgs):
        c["id"] = f"P2-{FIRST_ID + i:03d}"
    return cfgs


def main() -> None:
    cfgs = config_list()
    print(f"{len(cfgs)} configurations ({cfgs[0]['id']}..{cfgs[-1]['id']})", flush=True)
    t0 = time.time()
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    groups = {}
    for c in cfgs:
        groups.setdefault((c["family"], c["tf"], c["rtf"], c["variant"], c["htf"]), []).append(c)
    results, trades = [], []
    for (fam, tf, rtf, var, htf), cs in groups.items():
        minutes = EXEC_TFS[tf]
        sigs = {}
        for s in SYMBOLS:
            df, ev = load_cached(s, tf, defs="v2")
            if fam in ("B2v2", "B4"):
                sigs[s] = flip_signals_v2(df, ev, tf if fam == "B2v2" else f"{rtf}>{tf}", var)
            else:
                sigs[s] = stack_signals_v2(df, var, htf)
        for c in cs:
            sims = pd.concat([simulate_coin(s, sigs[s], minutes, "structure", c["target"], arrays[s]) for s in SYMBOLS],
                             ignore_index=True)
            res, f = evaluate(c, sims)
            res["signals"] = int(sum(len(v) for v in sigs.values()))
            res["signals_skipped_stop"] = int(sum(v["stop_dist"].isna().sum() for v in sigs.values()))
            results.append(res)
            trades.append(f)
            w = res["wf"]
            lab = f"{rtf}>{tf}" if fam == "B4" else tf
            print(f"{c['id']} {fam:5s} {lab:7s} {var} {c['target']:10s} {str(htf):10s} n={w.get('n', 0):5d} "
                  f"exp={w.get('exp_R', np.nan):+.3f} gross={w.get('gross_R', np.nan):+.3f} pf={w.get('pf', np.nan):.2f} "
                  f"fee={w.get('fee_R', np.nan):.3f} [{time.time() - t0:.0f}s]", flush=True)
    v1 = json.loads((OUT / "baseline_results.json").read_text())["results"]
    srs = np.array([r["wf"].get("sr", np.nan) for r in v1 + results], dtype=float)
    var_sr = float(np.nanvar(srs, ddof=1))
    n_trials = len(v1) + len(results)
    for r in results:
        w = r["wf"]
        r["dsr"] = deflated_sharpe(w.get("sr", np.nan), w.get("n", 0), w.get("skew", 0.0), w.get("kurt", 3.0), n_trials, var_sr)
    pd.concat(trades, ignore_index=True).to_parquet(RES / "trades_v2.parquet")
    (OUT / "baseline_v2_results.json").write_text(json.dumps({"n_configs": len(results), "n_trials_total": n_trials,
                                                              "sr_var_trials": var_sr, "results": results}, indent=1, default=float))
    print("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
