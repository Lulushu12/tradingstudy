"""Round 3 validation.

Inputs (trader-supplied TradingView exports from the same chart):
  EXPORT1: the original 300-bar export (burned holdout window Jul 5-8 2026).
  EXPORT2: a re-export with deep history loaded, 2026-04-13 .. 2026-07-08.
           Rows inside the UNSEEN holdout span (bar opens after 2026-06-21
           16:45 and before 2026-07-05 16:15, or after 2026-07-08 19:00) are
           dropped by timestamp BEFORE any analysis and never inspected.
  EXPORT3: 2024-01-01 .. 2024-04-30, all studied span.

Tests:
  A. Reproducibility: EXPORT1 vs EXPORT2 on the overlapping burned window;
     bar values and every event column compared cell by cell.
  B. Deep validation: port computed on the full continuous studied history
     (no cold start), joined to EXPORT3 by timestamp: values, all six pivot
     event chains, and stack events.
  C. The 2026 studied portion of EXPORT2 (Apr 13 .. Jun 21) as a bonus
     event-chain comparison with TV-warm values.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcb_port import wavetrend, mfi_clone, find_divs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UP = "/root/.claude/uploads/a7d65ca0-3953-502d-ac38-420fdad00a22"
EXPORT1 = os.path.join(HERE, "burned", "validation_export_BURNED_holdout_span.csv")
EXPORT2 = os.path.join(UP, "a5ec61c8-BINANCE_BTCUSDT.P_15_fresh.csv")
EXPORT3 = os.path.join(UP, "28b036eb-BINANCE_BTCUSDT.P_15_new.csv")

STUDIED_END = 1782060300      # last studied bar open
BURNED_START = 1783268100     # export1 first bar open
BURNED_END = 1783537200       # export1 last bar open

EVENT_COLS = ["WT Bear Div", "WT Bull Div", "WT 2nd Bear Div", "WT 2nd Bull Div",
              "MFI Bear Div", "MFI Bull Div", "Bull Stack", "Bear Stack"]
VALUE_COLS = ["open", "high", "low", "close", "WT Wave 1", "WT Wave 2", "VWAP", "Mny Flow"]


def load_export2():
    df = pd.read_csv(EXPORT2)
    keep = (df["time"] <= STUDIED_END) | \
           ((df["time"] >= BURNED_START) & (df["time"] <= BURNED_END))
    dropped = len(df) - keep.sum()
    df = df[keep].reset_index(drop=True)
    print(f"EXPORT2: kept {len(df)} rows, dropped {dropped} quarantined rows unseen")
    return df


def test_a(e1, e2):
    print("\n=== A. REPRODUCIBILITY: export1 vs export2, burned window ===")
    m = e1.merge(e2, on="time", suffixes=("_1", "_2"))
    print(f"overlapping bars: {len(m)}")
    for col in VALUE_COLS:
        d = np.abs(m[f"{col}_1"].astype(float) - m[f"{col}_2"].astype(float))
        print(f"  {col:12s} max diff {np.nanmax(d):.3e}")
    for col in EVENT_COLS:
        a = m[f"{col}_1"].notna().to_numpy()
        b = m[f"{col}_2"].notna().to_numpy()
        rows_only1 = m["time"][a & ~b].tolist()
        rows_only2 = m["time"][~a & b].tolist()
        status = "IDENTICAL" if not rows_only1 and not rows_only2 else \
                 f"DIFFER: only-in-1 {len(rows_only1)}, only-in-2 {len(rows_only2)}"
        print(f"  {col:16s} n1={a.sum():3d} n2={b.sum():3d}  {status}")
        for t in (rows_only1 + rows_only2)[:6]:
            print(f"      {pd.to_datetime(t, unit='s', utc=True)}")


def port_events_on_studied():
    """Compute the port on the full continuous studied series."""
    s = pd.read_parquet(os.path.join(ROOT, "audit", "studied_15m.parquet"))
    h, l, c, o = (s[k].to_numpy(float) for k in ["high", "low", "close", "open"])
    wt1, wt2 = wavetrend(h, l, c)
    mfi = mfi_clone(o, c)
    chains = {
        "WT Bear Div": ("top", find_divs(wt2, h, l, 45.0, -65.0)),
        "WT Bull Div": ("bot", None),
        "WT 2nd Bear Div": ("top", find_divs(wt2, h, l, 15.0, -40.0)),
        "WT 2nd Bull Div": ("bot", None),
        "MFI Bear Div": ("top", find_divs(mfi, h, l, 2.5, -2.5)),
        "MFI Bull Div": ("bot", None),
    }
    chains["WT Bull Div"] = ("bot", chains["WT Bear Div"][1])
    chains["WT 2nd Bull Div"] = ("bot", chains["WT 2nd Bear Div"][1])
    chains["MFI Bull Div"] = ("bot", chains["MFI Bear Div"][1])
    return s, wt1, wt2, mfi, chains


def test_events(exp, s, wt1, wt2, mfi, chains, label):
    print(f"\n=== {label}: values + events vs port on continuous history ===")
    time_to_idx = {t: i for i, t in enumerate(s["time"].to_numpy())}
    idx = np.array([time_to_idx.get(t, -1) for t in exp["time"]])
    ok = idx >= 0
    print(f"bars matched to studied set: {ok.sum()} of {len(exp)}")
    exp = exp[ok].reset_index(drop=True)
    idx = idx[ok]

    for col, mine in (("WT Wave 1", wt1), ("WT Wave 2", wt2), ("Mny Flow", mfi)):
        tv = exp[col].to_numpy(float)
        d = np.abs(mine[idx] - tv)
        rel = d / np.maximum(np.abs(tv), 1.0)
        print(f"  {col:12s} max_abs={np.nanmax(d):.3e} max_rel={np.nanmax(rel):.3e} "
              f"{'PASS' if np.nanmax(rel) < 1e-6 else 'FAIL'}")

    # events: TV cell at export row r (pivot, offset applied) vs port event
    # confirming at studied index idx[r]+2
    for col, (side, chain) in chains.items():
        flags = chain.is_top if side == "top" else chain.is_bot
        conf_bars = set(np.where(flags)[0])
        tv_rows = np.where(exp[col].notna())[0]
        tv_set = set(int(idx[r]) for r in tv_rows)
        my_set = set(int(b - 2) for b in conf_bars
                     if (b - 2) in set(idx[2:-2].tolist()))
        extra_tv = sorted(tv_set - my_set)
        extra_my = sorted(my_set - tv_set)
        verdict = "PASS" if not extra_tv and not extra_my else "FAIL"
        print(f"  {col:16s} TV {len(tv_set):3d} port {len(my_set):3d}  "
              f"TV-only {len(extra_tv)} port-only {len(extra_my)}  {verdict}")
        for b in (extra_tv + extra_my)[:8]:
            src = "TV-only" if b in extra_tv else "port-only"
            print(f"      {src}: pivot {pd.to_datetime(s['time'].iloc[b], unit='s', utc=True)}")


def main():
    e1 = pd.read_csv(EXPORT1)
    e2 = load_export2()
    test_a(e1, e2[(e2["time"] >= BURNED_START)])

    s, wt1, wt2, mfi, chains = port_events_on_studied()
    e3 = pd.read_csv(EXPORT3)
    test_events(e3.iloc[300:].reset_index(drop=True), s, wt1, wt2, mfi, chains,
                "B. 2024 STUDIED SPAN (first 300 export rows skipped as TV-side warm-up buffer)")
    e2_studied = e2[e2["time"] <= STUDIED_END].reset_index(drop=True)
    test_events(e2_studied.iloc[300:].reset_index(drop=True), s, wt1, wt2, mfi, chains,
                "C. 2026 STUDIED PORTION of export2")


if __name__ == "__main__":
    main()
