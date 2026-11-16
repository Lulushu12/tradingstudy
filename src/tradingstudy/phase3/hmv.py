"""Hypothesis H-MV (PROTOCOL Amendment 2): MCB entries gated by the user's Macro View bias on 10 x the chart TF.
27 configurations, ids P3-013..P3-039.  Usage: uv run python -m tradingstudy.phase3.hmv
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from tradingstudy.backtest.cache import load_cached
from tradingstudy.backtest.signals import stack_signals_v2, wtdiv_signals_v2
from tradingstudy.backtest.stats import deflated_sharpe
from tradingstudy.config import DATA, REPORTS, SYMBOLS
from tradingstudy.features.build import EXEC_TFS, bars_any
from tradingstudy.features.macro import macro_bias
from tradingstudy.phase2.baselines import evaluate, m1_arrays, simulate_coin

OUT = REPORTS / "phase3"
RES = DATA / "results" / "phase3"
FIRST_ID = 13
ENTRIES = ["stackA", "stackB", "wtdiv"]
BIASES = ["lean", "any", "strong"]
TFS = ["15m", "24m", "1h"]


def entry_signals(df: pd.DataFrame, entry: str) -> pd.DataFrame:
    if entry == "stackA":
        return stack_signals_v2(df, "A")
    if entry == "stackB":
        return stack_signals_v2(df, "B")
    return wtdiv_signals_v2(df)


def gated(sig: pd.DataFrame, bias: pd.DataFrame, kind: str) -> pd.DataFrame:
    b = bias.loc[sig.index, f"bias_{kind}"].to_numpy()
    return sig[(b == sig["direction"].to_numpy())]


def config_list(length=50, thresh=60.0, mult=10, first_id=FIRST_ID, prefix="P3"):
    cfgs = []
    for tf in TFS:
        for e in ENTRIES:
            for b in BIASES:
                cfgs.append(dict(family="H-MV", tf=tf, entry=e, bias=b, variant=e, stop="structure", target="2R",
                                 htf=None, mv_len=length, mv_thresh=thresh, mv_mult=mult))
    for i, c in enumerate(cfgs):
        c["id"] = f"{prefix}-{first_id + i:03d}"
    return cfgs


def run(cfgs: list[dict], out_name: str) -> list[dict]:
    t0 = time.time()
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    results, trades = [], []
    cache = {}
    for c in cfgs:
        tf, cm = c["tf"], EXEC_TFS[c["tf"]]
        sims = []
        for s in SYMBOLS:
            key = (s, tf, c["mv_len"], c["mv_thresh"], c["mv_mult"])
            if key not in cache:
                df, _ = load_cached(s, tf, defs="v2")
                htf = bars_any(s, cm * c["mv_mult"], "dev_warmup")
                cache[key] = (df, macro_bias(htf, cm * c["mv_mult"], df.index, c["mv_len"], c["mv_thresh"]))
            df, bias = cache[key]
            sig = gated(entry_signals(df, c["entry"]), bias, c["bias"])
            sims.append(simulate_coin(s, sig, cm, "structure", c["target"], arrays[s]))
        res, f = evaluate(c, pd.concat(sims, ignore_index=True))
        results.append(res)
        trades.append(f)
        w = res["wf"]
        print(f"{c['id']} {tf:3s} {c['entry']:6s} bias={c['bias']:6s} tgt={c['target']:9s} n={w.get('n', 0):5d} "
              f"exp={w.get('exp_R', np.nan):+.3f} gross={w.get('gross_R', np.nan):+.3f} pf={w.get('pf', np.nan):.2f} "
              f"[{time.time() - t0:.0f}s]", flush=True)
    prev = []
    for fn in ("phase2/baseline_results.json", "phase2/baseline_v2_results.json", "phase3/discovery_results.json"):
        prev += json.loads((REPORTS / fn).read_text())["results"]
    if (OUT / "hmv_results.json").exists() and out_name != "hmv_results.json":
        prev += json.loads((OUT / "hmv_results.json").read_text())["results"]
    srs = np.array([r["wf"].get("sr", np.nan) for r in prev + results], dtype=float)
    var_sr, n_trials = float(np.nanvar(srs, ddof=1)), len(prev) + len(results)
    for r in results:
        w = r["wf"]
        r["dsr"] = deflated_sharpe(w.get("sr", np.nan), w.get("n", 0), w.get("skew", 0.0), w.get("kurt", 3.0), n_trials, var_sr)
    RES.mkdir(parents=True, exist_ok=True)
    pd.concat(trades, ignore_index=True).to_parquet(RES / out_name.replace(".json", "_trades.parquet"))
    (OUT / out_name).write_text(json.dumps({"n_trials_total": n_trials, "sr_var_trials": var_sr, "results": results},
                                           indent=1, default=str))
    print("done", f"{time.time() - t0:.0f}s")
    return results


if __name__ == "__main__":
    run(config_list(), "hmv_results.json")
