"""Facts needed for the Gate 1 proposals. Census and price statistics on the dev period only. No trade outcomes,
returns after signals, or labels are computed here, so nothing in this file counts against the experiment budget.

Usage: uv run python -m tradingstudy.phase1.gate1_facts
"""
from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd

from tradingstudy.config import REPORTS, SYMBOLS
from tradingstudy.data.guard import load_bars
from tradingstudy.features import ta
from tradingstudy.features.build import EXEC_TFS, build_features
from tradingstudy.structure.ranges import ranges_and_flips
from tradingstudy.structure.swings import zigzag

warnings.filterwarnings("ignore")
OUT = REPORTS / "phase1"


def tick_size(close: pd.Series) -> float:
    px = np.unique(np.round(close.to_numpy(), 8))
    d = np.diff(px)
    d = d[d > 1e-12]
    return float(np.round(np.quantile(d, 0.01), 8)) if len(d) else np.nan


def stacks(f: pd.DataFrame, window: int) -> dict:
    """WT regular dot divergence + MF regular pivot divergence, same direction, the later one within `window` bars
    of the earlier. Variant A: both confirmed. Variant B: one confirmed, the other front-run. Event = the later bar."""
    out = {}
    for side in ("bull", "bear"):
        wa = f[f"wtdiv_{side}_reg"].to_numpy(); ma = f[f"mfdiv_{side}_reg"].to_numpy()
        wb = f[f"wtdiv_fr_{side}"].to_numpy(); mb = f[f"mfdiv_fr_{side}"].to_numpy()
        def recent(x):  # x happened within the last `window` bars (inclusive of now)
            return pd.Series(x.astype(float)).rolling(window + 1, min_periods=1).max().to_numpy() > 0
        a = (wa & recent(ma)) | (ma & recent(wa))
        b = (wb & recent(ma)) | (mb & recent(wa))
        out[f"A_{side}"] = int(a.sum()); out[f"B_{side}"] = int(b.sum())
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    facts = {"ticks": {}, "m1_range_pct": {}, "fee_R": [], "census": [], "regimes": {}, "range_flip": []}
    for s in SYMBOLS:
        m1 = load_bars(s, "1m", "dev")
        yearly = {str(y): tick_size(g["close"]) for y, g in m1.groupby(m1.index.year)}
        facts["ticks"][s] = yearly
        rng = ((m1["high"] - m1["low"]) / m1["close"] * 100)
        facts["m1_range_pct"][s] = {"median": round(float(rng.median()), 4), "p90": round(float(rng.quantile(0.9)), 4)}
        print("ticks/range", s, yearly, facts["m1_range_pct"][s], flush=True)
    for s in SYMBOLS:
        for tf, cm in EXEC_TFS.items():
            b = load_bars(s, tf, "dev")
            atr_pct = ta.atr(b["high"], b["low"], b["close"], 14) / b["close"].to_numpy()
            row = {"symbol": s, "tf": tf}
            for m in (1.0, 1.5, 2.0):
                row[f"fee_R_{m}atr_median"] = round(float(np.nanmedian(0.0008 / (m * atr_pct))), 3)
            facts["fee_R"].append(row)
            f = build_features(s, tf)
            days = (b.index[-1] - b.index[0]).days
            c = {"symbol": s, "tf": tf, "days": days,
                 "wt_buy": int(f.wt_buy.sum()), "wt_sell": int(f.wt_sell.sum()),
                 "wtdiv_reg": int(f.wtdiv_bull_reg.sum() + f.wtdiv_bear_reg.sum()),
                 "mfdiv_reg": int(f.mfdiv_bull_reg.sum() + f.mfdiv_bear_reg.sum())}
            for w in (6, 11, 20):
                st = stacks(f, w)
                c[f"stackA_w{w}"] = st["A_bull"] + st["A_bear"]; c[f"stackB_w{w}"] = st["B_bull"] + st["B_bear"]
            facts["census"].append(c)
            if tf == "15m":
                facts["regimes"][s] = {r: f[r].value_counts(normalize=True).round(3).to_dict() for r in ("r1_trend", "r2_trend", "r3_trend")}
            for k in (2.0, 3.0):
                st_, ev, rg = ranges_and_flips(b, zigzag(b, k), tol=1.0, h_min=2.0)
                facts["range_flip"].append({"symbol": s, "tf": tf, "k": k, "days": days, "A": int((ev.variant == 0).sum()),
                                            "B": int((ev.variant == 1).sum()), "ranges": len(rg)})
            print("census", s, tf, flush=True)
    (OUT / "gate1_facts.json").write_text(json.dumps(facts, indent=2, default=str))
    print("wrote", OUT / "gate1_facts.json")


if __name__ == "__main__":
    main()
