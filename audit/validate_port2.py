"""Port validation against a fresh MCB Clone v1 export supplied by the trader.

The export spans 2026-07-05 16:15 to 2026-07-08 UTC, which is INSIDE the
holdout span. That window is hereby burned (recorded in
HOLDOUT_DO_NOT_TOUCH.md) and is used for validation only. This script loads
ONLY the burned file; it never touches holdout/holdout_15m.csv or any
still-quarantined bar.

What the export gives us (plot columns, offset -2 applied by TV at export,
so a non-empty cell at row r means the event CONFIRMED at row r+2 and the
cell value is the oscillator at the pivot row r):
  WT Wave 1 / WT Wave 2 / VWAP / Mny Flow: per-bar values.
  WT Bear/Bull Div: wtIsTop/wtIsBot of the PRIMARY chain (45 / -65). The
    plot fires on every level-passing fractal (color, not value, encodes
    whether a divergence actually fired), so these validate pivot+level
    detection.
  WT 2nd Bear/Bull Div: same for the secondary chain (15 / -40).
  MFI Bear/Bull Div: same for the MFI chain (2.5 / -2.5).
  Bull/Bear Stack: actual stack firings (validates divergence + valuewhen
    reference logic + window arithmetic; export was made with the trader's
    chart inputs).

Port warm-up: TV computed with full prior history; the port starts cold at
the file's first bar. Values are compared after a burn-in; the convergence
profile is printed so the burn-in choice is visible, not assumed.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcb_port import wavetrend, mfi_clone, find_divs

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "burned", "validation_export_BURNED_holdout_span.csv")
BURN = 120


def main():
    df = pd.read_csv(SRC)
    n = len(df)
    # last bar may have been exported mid-formation; exclude it everywhere
    df = df.iloc[:-1].reset_index(drop=True)
    n = len(df)
    print(f"{n} bars, {pd.to_datetime(df['time'].iloc[0], unit='s', utc=True)} "
          f"-> {pd.to_datetime(df['time'].iloc[-1], unit='s', utc=True)} "
          f"(final bar of file dropped as possibly partial)")

    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    o = df["open"].to_numpy(float)
    wt1, wt2 = wavetrend(h, l, c)
    mfi = mfi_clone(o, c)

    print("\n=== VALUE CONVERGENCE (max abs diff per 20-bar block) ===")
    for name, mine, col in (("wt2", wt2, "WT Wave 2"), ("mfi", mfi, "Mny Flow")):
        tv = df[col].to_numpy(float)
        d = np.abs(mine - tv)
        prof = ["%d:%.1e" % (s, np.nanmax(d[s:s + 20])) for s in range(0, 200, 20)]
        print(f"  {name}: {'  '.join(prof)}")

    print(f"\n=== VALUES from bar {BURN} ===")
    ok_all = True
    for name, mine, col in (("wt1", wt1, "WT Wave 1"), ("wt2", wt2, "WT Wave 2"),
                            ("vwap", wt1 - wt2, "VWAP"), ("mfi", mfi, "Mny Flow")):
        tv = df[col].to_numpy(float)
        m, t = mine[BURN:], tv[BURN:]
        good = ~np.isnan(m) & ~np.isnan(t)
        d = np.abs(m[good] - t[good])
        rel = d / np.maximum(np.abs(t[good]), 1.0)
        verdict = "PASS" if rel.max() < 1e-6 else "FAIL"
        ok_all &= verdict == "PASS"
        print(f"  {name:5s} n={good.sum():3d} max_abs={d.max():.3e} "
              f"max_rel={rel.max():.3e}  {verdict}")

    # pivot event columns: non-empty cell at row r => event confirmed at r+2
    chains = {
        "WT primary": (find_divs(wt2, h, l, 45.0, -65.0), "WT Bear Div", "WT Bull Div", wt2),
        "WT secondary": (find_divs(wt2, h, l, 15.0, -40.0), "WT 2nd Bear Div", "WT 2nd Bull Div", wt2),
        "MFI": (find_divs(mfi, h, l, 2.5, -2.5), "MFI Bear Div", "MFI Bull Div", mfi),
    }
    print(f"\n=== PIVOT EVENTS (isTop/isBot incl. level filter) from bar {BURN} ===")
    for name, (chain, bear_col, bull_col, osc) in chains.items():
        for side, col, flags in (("top", bear_col, chain.is_top),
                                 ("bot", bull_col, chain.is_bot)):
            tv_rows = set(np.where(df[col].notna())[0]) & set(range(BURN, n))
            my_rows = set((np.where(flags)[0] - 2).tolist()) & set(range(BURN, n))
            extra_tv = sorted(tv_rows - my_rows)
            extra_my = sorted(my_rows - tv_rows)
            both = sorted(tv_rows & my_rows)
            vd = max((abs(df[col].iloc[r] - osc[r]) for r in both), default=0.0)
            verdict = "PASS" if not extra_tv and not extra_my and vd < 1e-6 else "FAIL"
            ok_all &= verdict == "PASS"
            print(f"  {name:12s} {side}: TV {len(tv_rows):2d} / port {len(my_rows):2d} "
                  f"matched {len(both):2d}  TV-only {extra_tv}  port-only {extra_my}  "
                  f"max value diff {vd:.2e}  {verdict}")

    # stack events per the Pine block (trader's chart inputs; window unknown,
    # try 30 default and 11 spec and report which reproduces the export)
    print("\n=== STACK EVENTS ===")
    tv_bull = sorted(np.where(df["Bull Stack"].notna())[0] + 2)
    tv_bear = sorted(np.where(df["Bear Stack"].notna())[0] + 2)
    print(f"  TV: bull at rows {tv_bull}, bear at rows {tv_bear} (confirmation bars)")
    wt_p, wt_s, mf = chains["WT primary"][0], chains["WT secondary"][0], chains["MFI"][0]
    wt_bull_any = wt_p.bull_div | wt_s.bull_div
    wt_bear_any = wt_p.bear_div | wt_s.bear_div
    for window in (30, 11):
        def stack(wt_ev, mfi_ev):
            last_wt = last_mfi = -10**9
            out = []
            for t in range(n):
                if wt_ev[t]:
                    last_wt = t
                if mfi_ev[t]:
                    last_mfi = t
                if (wt_ev[t] and t - last_mfi <= window) or \
                   (mfi_ev[t] and t - last_wt <= window):
                    out.append(t)
            return out
        b = stack(wt_bull_any, mf.bull_div)
        s = stack(wt_bear_any, mf.bear_div)
        print(f"  port window={window}: bull {b}, bear {s}")

    print(f"\nOVERALL VALUES+PIVOTS: {'PASS' if ok_all else 'FAIL'}")


if __name__ == "__main__":
    main()
