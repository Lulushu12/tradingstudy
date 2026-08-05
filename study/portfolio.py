"""Task 3 — portfolio assembly: volume-spike + SFP star short + SFP bull mirror.

Three 4H streams, each already validated separately:
  A) volume-spike trend continuation, fixed 2R (the original finalist);
  B) SFP star short (bear divergence + downtrend), half@1R->BE + 3-ATR trail;
  C) SFP bull mirror (bull divergence + uptrend), same exit.

Questions: how correlated are their monthly returns, what does the combined
stream deliver at 1% and at 0.5% risk per trade, and does the 6% max-DD cap hold.
Sizing via finalists.sim_equity in both 'concurrent' (take everything) and
'single' (one position at a time across the whole book) modes.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from trend_runner import run_fixed
from finalists import build_trades, sim_equity, fmt
from sfp_divergence import sfp_divergence
from sfp_exits import run_half1R_trail

import sys
USE_SWEEP = "star" not in sys.argv[1:]   # default: unified sweep family streams

def norm(tr, name):
    t = tr.copy()
    t["outcome"] = np.where(t["net_R"] > 0, "target", "stop")
    t["strat"] = name
    return t[["entry_time", "exit_time", "net_R", "outcome", "strat"]]

def monthly_R(t):
    d = pd.to_datetime(t["entry_time"], unit="s", utc=True).dt.to_period("M")
    return t.groupby(d)["net_R"].sum()

def main():
    df = ind.enrich(pd.read_parquet("data/4H.parquet"))
    n = len(df)
    Lz = np.zeros(n, bool)
    if USE_SWEEP:
        from unify import sweep_masks
        M = sweep_masks(df)
        dn = (df["close"] < df["ema200"]).values
        short_m = (M["swp_bear0"] | M["swp_bear1"]) & dn
        long_m = (M["swp_bull0"] | M["swp_bull1"]) & ~dn
        b_name, c_name = "sweepShort", "sweepLong"
    else:
        m = sfp_divergence(df)
        dn = (df["close"] < df["ema200"]).values
        short_m = (m["bear0"] | m["bear1"]) & dn
        long_m = (m["bull0"] | m["bull1"]) & ~dn
        b_name, c_name = "starShort", "bullMirror"

    A = norm(build_trades(df, "volspike", 2.0), "volspike2R")
    B = norm(run_half1R_trail(df, Lz, short_m, k=3.0), b_name)
    C = norm(run_half1R_trail(df, long_m, Lz, k=3.0), c_name)
    combo = pd.concat([A, B, C]).sort_values("entry_time").reset_index(drop=True)

    print("===== per-stream (concurrent, 1% risk) =====")
    for t, name in [(A, "A volspike 2R"), (B, f"B {b_name}"), (C, f"C {c_name}")]:
        _, met = sim_equity(t, mode="concurrent")
        print(f"  {name:15}", fmt(met))

    print("\n===== monthly net-R correlations =====")
    M = pd.concat([monthly_R(A).rename("A"), monthly_R(B).rename("B"),
                   monthly_R(C).rename("C")], axis=1).fillna(0.0)
    print(M.corr().round(2).to_string())
    both_neg = ((M["A"] < 0) & (M["B"] < 0)).mean()
    print(f"  months A and B both negative: {both_neg:.0%}   "
          f"(A neg: {(M['A']<0).mean():.0%}, B neg: {(M['B']<0).mean():.0%})")
    all_neg = ((M["A"] < 0) & (M["B"] < 0) & (M["C"] < 0)).mean()
    print(f"  months all three negative: {all_neg:.0%}")

    # overlap: star trades opened while a volspike trade is running
    a_iv = list(zip(A["entry_time"], A["exit_time"]))
    b_open = B["entry_time"].values
    overl = np.mean([any(s <= t < e for s, e in a_iv) for t in b_open])
    print(f"  star entries occurring inside an open volspike trade: {overl:.0%}")

    print("\n===== combined book =====")
    for mode in ["concurrent", "single"]:
        for risk in [0.01, 0.005]:
            _, met = sim_equity(combo, mode=mode, risk=risk)
            print(f"  risk={risk:.1%} ", fmt(met))

    print("\n===== combined, per year (concurrent 1%) =====")
    t = combo.copy()
    t["year"] = pd.to_datetime(t["entry_time"], unit="s", utc=True).dt.year
    for y, sub in t.groupby("year"):
        R = sub["net_R"].values
        print(f"  {y}: n={len(sub):3d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f} sumR={R.sum():+.1f}")

if __name__ == "__main__":
    main()
