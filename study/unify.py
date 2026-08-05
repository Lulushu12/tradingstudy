"""Task 5 — unify the SFP star with the held-swing-resistance short.

The confluence pass's '4H swing resistance hold -> short' (61%/64% @1:1, n~104)
is structurally the star minus the RSI condition: both are a failed sweep of the
last confirmed 4H pivot high inside a downtrend. Decompose the family:

  SWEEP   = bar sweeps above the last confirmed pivot high and is the highest bar
            of the new upswing (offset 0, closes back below = rejection; offset 1 =
            the bar after the sweep extreme), in a 4H downtrend  [no RSI condition]
  STAR    = SWEEP & RSI divergence (RSI at sweep < RSI at the swept pivot)
  NODIV   = SWEEP & ~divergence (rejections where RSI made a HIGHER high too)

If NODIV performs like STAR, the RSI leg is incidental and the tradeable sample
roughly doubles. If STAR >> NODIV, the divergence is load-bearing. Long mirror
included. Exits: fixed 2R/3R + half@1R->BE + 3-ATR trail. Train/test + yearly.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from trend_runner import run_fixed
from sfp_exits import run_half1R_trail
from sfp_walkforward import yearly

def sweep_masks(df, left=3, right=3, lookback=40):
    """Like sfp_divergence but split by the RSI condition. Returns dict of masks."""
    ph, pl = ind.pivots(df, left, right)
    phv, plv = ph.values, pl.values
    h = df["high"].values; l = df["low"].values; c = df["close"].values
    r = df["rsi14"].values
    n = len(df)
    out = {k: np.zeros(n, bool) for k in
           ["swp_bear0", "swp_bear1", "div_bear0", "div_bear1",
            "swp_bull0", "swp_bull1", "div_bull0", "div_bull1"]}
    new_hi = np.zeros(n, bool); hi_div = np.zeros(n, bool)
    new_lo = np.zeros(n, bool); lo_div = np.zeros(n, bool)
    ref_hi_p = -1; ref_hi = np.nan; ref_hi_rsi = np.nan; runmax = -np.inf
    ref_lo_p = -1; ref_lo = np.nan; ref_lo_rsi = np.nan; runmin = np.inf
    for t in range(n):
        if not np.isnan(phv[t]):
            ref_hi_p = t - right; ref_hi = h[ref_hi_p]; ref_hi_rsi = r[ref_hi_p]
            runmax = h[ref_hi_p+1:t].max() if t > ref_hi_p+1 else -np.inf
        if not np.isnan(plv[t]):
            ref_lo_p = t - right; ref_lo = l[ref_lo_p]; ref_lo_rsi = r[ref_lo_p]
            runmin = l[ref_lo_p+1:t].min() if t > ref_lo_p+1 else np.inf
        if ref_hi_p >= 0 and (t - ref_hi_p) <= lookback:
            if h[t] > ref_hi and h[t] > runmax:
                new_hi[t] = True
                hi_div[t] = r[t] < ref_hi_rsi
                if c[t] < ref_hi:
                    out["swp_bear0"][t] = True
                    out["div_bear0"][t] = hi_div[t]
            if t > 0 and new_hi[t-1] and h[t] < h[t-1]:
                out["swp_bear1"][t] = True
                out["div_bear1"][t] = hi_div[t-1]
            runmax = max(runmax, h[t])
        if ref_lo_p >= 0 and (t - ref_lo_p) <= lookback:
            if l[t] < ref_lo and l[t] < runmin:
                new_lo[t] = True
                lo_div[t] = r[t] > ref_lo_rsi
                if c[t] > ref_lo:
                    out["swp_bull0"][t] = True
                    out["div_bull0"][t] = lo_div[t]
            if t > 0 and new_lo[t-1] and l[t] > l[t-1]:
                out["swp_bull1"][t] = True
                out["div_bull1"][t] = lo_div[t-1]
            runmin = min(runmin, l[t])
    return out

def tt(tag, tr):
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    out = []
    for lab, sub in [("TR", tr[tr.entry_time < cut]), ("TE", tr[tr.entry_time >= cut])]:
        if not len(sub):
            out.append(f"{lab}: (none)"); continue
        R = sub["net_R"].values
        out.append(f"{lab}: n={len(sub):3d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f}")
    print(f"    {tag:28} | " + " | ".join(out))

def main(asset="btc"):
    if asset == "xrp":
        from xrp_validation import load_xrp_4h
        df = ind.enrich(load_xrp_4h())
        print("===== XRP =====")
    elif asset == "eth":
        from eth_validation import load_eth_4h
        df = ind.enrich(load_eth_4h())
        print("===== ETH =====")
    else:
        df = ind.enrich(pd.read_parquet("data/4H.parquet"))
    n = len(df)
    M = sweep_masks(df)
    dn = (df["close"] < df["ema200"]).values
    up = ~dn
    swp_bear = (M["swp_bear0"] | M["swp_bear1"]) & dn
    star     = (M["swp_bear0"] & M["div_bear0"]) | (M["swp_bear1"] & M["div_bear1"])
    star &= dn
    nodiv    = swp_bear & ~star
    swp_bull = (M["swp_bull0"] | M["swp_bull1"]) & up
    star_b   = ((M["swp_bull0"] & M["div_bull0"]) | (M["swp_bull1"] & M["div_bull1"])) & up
    nodiv_b  = swp_bull & ~star_b
    Lz = np.zeros(n, bool)
    print(f"short family: SWEEP={int(swp_bear.sum())}  STAR(div)={int(star.sum())}  "
          f"NODIV={int(nodiv.sum())}")
    print(f"long  family: SWEEP={int(swp_bull.sum())}  STAR(div)={int(star_b.sum())}  "
          f"NODIV={int(nodiv_b.sum())}")
    for name, mask, side in [("SWEEP short (unified)", swp_bear, "S"),
                             ("STAR short (with div)", star, "S"),
                             ("NODIV short (no div)", nodiv, "S"),
                             ("SWEEP long (unified)", swp_bull, "L"),
                             ("STAR long (with div)", star_b, "L"),
                             ("NODIV long (no div)", nodiv_b, "L")]:
        L = mask if side == "L" else Lz
        S = mask if side == "S" else Lz
        print(f"\n  == {name}  (n={int(mask.sum())}) ==")
        tt("fixed 2R", run_fixed(df, L, S, rr=2.0))
        tt("fixed 3R", run_fixed(df, L, S, rr=3.0))
        tt("half@1R->BE+trail", run_half1R_trail(df, L, S, k=3.0))
    print("\n===== yearly, unified SWEEP short, trail exit =====")
    yearly("SWEEP short half@1R+trail", run_half1R_trail(df, Lz, swp_bear, k=3.0))
    yearly("SWEEP long  half@1R+trail", run_half1R_trail(df, swp_bull, Lz, k=3.0))

if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "btc")
