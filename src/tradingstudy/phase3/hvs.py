"""Hypothesis H-VS (PROTOCOL Amendment 3): 4h volume-spike trend continuation, all 9 coins.
Core configurations P3-040..P3-043; stability neighbours only if a core configuration is positive out of sample.
Usage: uv run python -m tradingstudy.phase3.hvs [neighbours]
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
import pandas as pd

from tradingstudy.backtest import engine as E
from tradingstudy.backtest.costs import SLIPPAGE, tick_for
from tradingstudy.backtest.stats import deflated_sharpe
from tradingstudy.config import DATA, REPORTS, SYMBOLS
from tradingstudy.data.guard import clip_scope, load_bars
from tradingstudy.features import context, ta
from tradingstudy.phase2.baselines import evaluate, m1_arrays

OUT = REPORTS / "phase3"
RES = DATA / "results" / "phase3"
H4 = 240
LONG_HOLD_MIN = 300 * H4
MIN_NS = 60 * 10**9


def signals(sym: str, vol_mult: float = 1.8, ema_len: int = 200, stop_atr: float = 1.5) -> pd.DataFrame:
    """Original rules on closed 4h bars (computed with warm-up, returned for dev bars only)."""
    b = load_bars(sym, "4h", "dev_warmup")
    ema = ta.ema(b["close"], ema_len)
    vr = b["volume"].to_numpy() / pd.Series(b["volume"]).rolling(20).mean().to_numpy()
    atr = ta.atr(b["high"], b["low"], b["close"], 14)
    c, o = b["close"].to_numpy(), b["open"].to_numpy()
    long_ = (c > ema) & (vr > vol_mult) & (c > o)
    short = (c < ema) & (vr > vol_mult) & (c < o)
    d = np.where(long_, 1, np.where(short, -1, 0))
    d1 = load_bars(sym, "1D", "dev_warmup")
    reg = context.trend_regimes(b, d1, b.index, H4)
    ses = context.session(b.index, H4)
    sig = pd.DataFrame({"close": c, "atr14": atr, "direction": d, "stop_dist": stop_atr * atr,
                        "r1_trend": reg["r1_trend"].to_numpy(), "r2_trend": reg["r2_trend"].to_numpy(),
                        "session": ses["session"].to_numpy()}, index=b.index)
    sig = clip_scope(sig, "4h", "dev")
    return sig[sig["direction"] != 0]


def simulate(sym: str, sig: pd.DataFrame, A: dict, target_r: float, market: bool, hold_min: int) -> pd.DataFrame:
    sig_ts = (sig.index + pd.Timedelta(minutes=H4)).as_unit("ns").asi8
    start = np.searchsorted(A["ts"], sig_ts, side="left").astype(np.int64)
    d = sig["direction"].to_numpy(np.int64)
    e = sig["close"].to_numpy(np.float64)
    sd = sig["stop_dist"].to_numpy(np.float64)
    tgt = np.full(len(sig), target_r) if market else e + d * target_r * sd
    ticks = np.array([tick_for(sym, y) for y in sig.index.year], dtype=float)
    out = E.simulate_ex(A["ts"], A["o"], A["h"], A["l"], A["c"], start, sig_ts.astype(np.int64), d, e, sd,
                        tgt.astype(np.float64), ticks, np.full(len(sig), SLIPPAGE[sym]), E.FEE_RATE,
                        E.DAY_NS, hold_min * MIN_NS, market)
    r = pd.DataFrame(out, columns=E.COLS)
    r["status"] = r["status"].astype(int)
    r["coin"] = sym
    r["sig_ts"] = sig_ts
    r["direction"] = d
    r["r1_rel"] = sig["r1_trend"].to_numpy() * d + 0.0
    r["r2_rel"] = sig["r2_trend"].to_numpy() * d + 0.0
    r["session"] = sig["session"].to_numpy()
    for col in ("fill_ts", "end_ts"):
        r[col] = r[col].fillna(r["sig_ts"]).astype("int64")
    return r


def core_configs() -> list[dict]:
    base = dict(family="H-VS", tf="4h", vol_mult=1.8, ema_len=200, stop_atr=1.5, target_r=2.0, stop="1.5xATR", target="2R", htf=None)
    specs = [("C1 original: market entry, 50-day hold", True, LONG_HOLD_MIN),
             ("C2 brief: limit at close, 24h timeout", False, 1440),
             ("C3 limit at close, 50-day hold", False, LONG_HOLD_MIN),
             ("C4 market entry, 24h timeout", True, 1440)]
    return [dict(base, id=f"P3-{40 + i:03d}", variant=name, market=m, hold_min=h) for i, (name, m, h) in enumerate(specs)]


def run(cfgs: list[dict], out_name: str) -> list[dict]:
    t0 = time.time()
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    results, trades = [], []
    for c in cfgs:
        sims = []
        for s in SYMBOLS:
            sig = signals(s, c["vol_mult"], c["ema_len"], c["stop_atr"])
            sims.append(simulate(s, sig, arrays[s], c["target_r"], c["market"], c["hold_min"]))
        res, f = evaluate(c, pd.concat(sims, ignore_index=True))
        results.append(res)
        trades.append(f)
        w = res["wf"]
        print(f"{c['id']} {c['variant']:42s} n={w.get('n', 0):5d} exp={w.get('exp_R', np.nan):+.3f} gross={w.get('gross_R', np.nan):+.3f} "
              f"pf={w.get('pf', np.nan):.2f} per_day={w.get('trades_per_day', np.nan):.2f} [{time.time() - t0:.0f}s]", flush=True)
    prev = []
    for fn in ("phase2/baseline_results.json", "phase2/baseline_v2_results.json", "phase3/discovery_results.json",
               "phase3/hmv_results.json"):
        prev += json.loads((REPORTS / fn).read_text())["results"]
    if out_name != "hvs_results.json" and (OUT / "hvs_results.json").exists():
        prev += json.loads((OUT / "hvs_results.json").read_text())["results"]
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
    if len(sys.argv) > 1 and sys.argv[1] == "neighbours":
        raise SystemExit("neighbours are declared only after a positive core result; run from a reviewed script")
    run(core_configs(), "hvs_results.json")
