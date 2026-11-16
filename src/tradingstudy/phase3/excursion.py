"""Descriptive diagnostic (LEDGER E003, counts: no): favourable vs adverse excursion after entry.

For every filled entry (independent simulation, walk-forward test period 2023-01-01..2025-11-14) measure, on 1m bars
from the minute after the fill to 24 h after it, in R (R = the entry's stop distance):
  - MFE (max favourable excursion) and MAE (max adverse excursion);
  - first touch of +x R vs -x R for x in 0.5, 1, 2 (same-minute double touch counted as adverse; neither = timeout).
A control set of random entries (same coins and TFs, random bars and directions, 1.5 ATR stop) shows what "no edge"
looks like in this data (2023-2025 drifted up, which favours longs).
Usage: uv run python -m tradingstudy.phase3.excursion
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.backtest.cache import load_cached
from tradingstudy.backtest.signals import META, _finish, stack_signals_v2
from tradingstudy.backtest.stats import WF_END, WF_START
from tradingstudy.config import REPORTS, SYMBOLS
from tradingstudy.features.build import EXEC_TFS, bars_any
from tradingstudy.features.macro import macro_bias
from tradingstudy.phase2.baselines import m1_arrays, simulate_coin
from tradingstudy.phase3.discovery import pooled_flips
from tradingstudy.phase3.hmv import gated

OUT = REPORTS / "phase3" / "EXCURSION_REPORT.md"
BARRIERS = (0.5, 1.0, 2.0)
DAY_NS = 1440 * 60 * 10**9


@nb.njit(cache=True)
def _excursions(ts, h, l, fill_idx, entry, R, d, barriers):
    n = fill_idx.shape[0]
    nb_ = barriers.shape[0]
    mfe = np.zeros(n); mae = np.zeros(n)
    first = np.zeros((n, nb_), dtype=np.int8)  # +1 favourable first, -1 adverse first (or same minute), 0 neither
    for k in range(n):
        j = fill_idx[k]
        t_end = ts[j] + 1440 * 60 * 10**9
        fav = 0.0; adv = 0.0
        done = np.zeros(nb_, dtype=np.bool_)
        for i in range(j + 1, ts.shape[0]):
            if ts[i] > t_end:
                break
            if d[k] == 1:
                f = (h[i] - entry[k]) / R[k]; a = (entry[k] - l[i]) / R[k]
            else:
                f = (entry[k] - l[i]) / R[k]; a = (h[i] - entry[k]) / R[k]
            fav = max(fav, f); adv = max(adv, a)
            for b in range(nb_):
                if not done[b]:
                    if a >= barriers[b]:
                        first[k, b] = -1; done[b] = True
                    elif f >= barriers[b]:
                        first[k, b] = 1; done[b] = True
        mfe[k] = fav; mae[k] = adv
    return mfe, mae, first


def random_signals(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    pos = np.sort(rng.choice(np.arange(200, len(df)), size=min(n, len(df) - 200), replace=False))
    sig = df.iloc[pos][META].copy()
    sig["direction"] = rng.choice([-1, 1], size=len(sig))
    stop = sig["close"].to_numpy() - sig["direction"].to_numpy() * 1.5 * sig["atr14"].to_numpy()
    return _finish(sig, stop)


def measure(sym: str, sig: pd.DataFrame, minutes: int, A: dict) -> pd.DataFrame:
    if sig.empty:
        return pd.DataFrame()
    r = simulate_coin(sym, sig, minutes, "structure", "2R", A)
    r["entry"] = sig["close"].to_numpy(); r["R"] = sig["stop_dist"].to_numpy()
    t = pd.to_datetime(r["sig_ts"], utc=True)
    r = r[(r["status"] == 0) & (t >= WF_START) & (t < WF_END)]
    if r.empty:
        return r
    mfe, mae, first = _excursions(A["ts"], A["h"], A["l"], r["fill_idx"].to_numpy(np.int64), r["entry"].to_numpy(),
                                  r["R"].to_numpy(), r["direction"].to_numpy(np.int64), np.array(BARRIERS))
    out = r[["coin", "direction", "fee_R"]].copy()
    out["mfe"], out["mae"] = mfe, mae
    for b, x in enumerate(BARRIERS):
        out[f"first_{x}"] = first[:, b]
    return out


def summarize(d: pd.DataFrame) -> dict:
    s = {"n": len(d), "mfe_med": d.mfe.median(), "mae_med": d.mae.median(), "mfe_mean": d.mfe.mean(), "mae_mean": d.mae.mean()}
    for x in BARRIERS:
        c = d[f"first_{x}"]
        s[f"p_fav_{x}"] = (c == 1).sum() / max((c != 0).sum(), 1)
    for x in (1.0, 2.0):
        s[f"reach_fav_{x}"] = (d.mfe >= x).mean()
        s[f"reach_adv_{x}"] = (d.mae >= x).mean()
    s["fee_R"] = d.fee_R.mean()
    return s


def main() -> None:
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    sets = {}
    for tf in ("15m", "24m", "1h"):
        cm = EXEC_TFS[tf]
        for s in SYMBOLS:
            df, ev = load_cached(s, tf, defs="v2")
            bias = macro_bias(bars_any(s, cm * 10, "dev_warmup"), cm * 10, df.index)
            stA = stack_signals_v2(df, "A")
            groups = {"stack A": stA, "stack B": stack_signals_v2(df, "B"), "flips A (pooled)": pooled_flips(df, ev, tf, "A"),
                      "stack A + Macro View lean": gated(stA, bias, "lean"),
                      "CONTROL random": random_signals(df, max(len(stA), 300), seed=hash((s, tf)) % 2**32)}
            for g, sig in groups.items():
                sets.setdefault((g, tf), []).append(measure(s, sig, cm, arrays[s]))
        print("done", tf, flush=True)
    rows = []
    for (g, tf), parts in sets.items():
        d = pd.concat(parts, ignore_index=True)
        for side, dd in (("all", d), ("long", d[d.direction == 1]), ("short", d[d.direction == -1])):
            rows.append({"group": g, "tf": tf, "side": side, **summarize(dd)})
    T = pd.DataFrame(rows)
    T.to_csv(REPORTS / "phase3" / "excursion_table.csv", index=False)
    pct = lambda x: f"{100 * x:.1f}%"
    md = ["# Diagnostic: favourable vs adverse excursion after entry (descriptive, LEDGER E003)", "",
          "Filled entries in the walk-forward test period (2023-01-01 to 2025-11-14), measured on 1m bars over the 24 h after "
          "the fill, in R (the entry's stop distance). 'Fav first at xR' = share of trades that touched +x R before -x R "
          "(same-minute double touch counted as adverse; trades touching neither excluded). A coin flip is 50%. "
          "CONTROL = random bars and directions with a 1.5 ATR stop, same coins and TFs.", "",
          "| Entries | TF | Side | Trades | Fav first 0.5R | Fav first 1R | Fav first 2R | Reach +1R | Reach -1R | Reach +2R | Reach -2R | Median MFE | Median MAE | Fee R |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in T.iterrows():
        md.append(f"| {r['group']} | {r['tf']} | {r['side']} | {r['n']} | {pct(r['p_fav_0.5'])} | {pct(r['p_fav_1.0'])} | {pct(r['p_fav_2.0'])} | "
                  f"{pct(r['reach_fav_1.0'])} | {pct(r['reach_adv_1.0'])} | {pct(r['reach_fav_2.0'])} | {pct(r['reach_adv_2.0'])} | "
                  f"{r['mfe_med']:.2f} | {r['mae_med']:.2f} | {r['fee_R']:.3f} |")
    OUT.write_text("\n".join(md) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
