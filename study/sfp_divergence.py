"""Early RSI divergence: signal candle must BE the swing-extreme candle (SFP) or the
candle right after it.

Motivation: the baseline regular divergence (indicators.rsi_divergence) detects the
second swing via a fractal pivot with right=3, so the signal fires 3 bars AFTER the
extreme. By then part of the reversal move is already spent ("exhaustion"). Here the
divergence is only taken when we catch it at the extreme itself:

  offset 0 (SFP candle): bar sweeps ABOVE the last confirmed pivot high (for bearish;
      mirror with lows for bullish), RSI on this bar is LOWER than RSI at that pivot,
      the bar is the highest bar of the new upswing so far, and it CLOSES back below
      the old pivot high -> swing failure pattern. Signal on this bar's close.
  offset 1 (candle right after): previous bar made the divergence high (swept the old
      pivot high with lower RSI, new upswing high) and the current bar fails to exceed
      it -> the extreme is provisionally in place. Signal on this bar's close.

Reference swing = last CONFIRMED fractal pivot (same left/right=3 machinery as the
baseline, fully causal: a pivot is only used from its confirmation bar onward).
Entry next bar open, stop atr_mult*ATR(14), fixed rr target. Train<2025 / Test>=2025.

Two evaluations, matching the repo conventions:
  A) research.py-style conditional winrates on precomputed forward outcomes
     (atr_mult=1.2, rr=1 and rr=2) vs the fee-adjusted breakeven WR.
  B) trend_runner.run_fixed trade sim on 4H (1.5*ATR stop, rr=2), hidden_div.py-style
     train/test report.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from trend_runner import run_fixed

def sfp_divergence(df, left=3, right=3, lookback=40):
    """Returns dict of boolean masks:
       bear0/bull0 = divergence caught ON the extreme candle (swing failure close),
       bear1/bull1 = caught on the candle right after the extreme.
    Causal: reference pivots are used only from their confirmation bar onward; all
    conditions use data up to the signal bar's close."""
    ph, pl = ind.pivots(df, left, right)          # values at confirmation bar
    phv, plv = ph.values, pl.values
    h = df["high"].values; l = df["low"].values; c = df["close"].values
    r = df["rsi14"].values
    n = len(df)
    bear0 = np.zeros(n, bool); bear1 = np.zeros(n, bool)
    bull0 = np.zeros(n, bool); bull1 = np.zeros(n, bool)
    # divergence-extreme flags (bar made a new upswing high above ref pivot w/ lower RSI)
    div_hi = np.zeros(n, bool); div_lo = np.zeros(n, bool)
    ref_hi_p = -1; ref_hi = np.nan; ref_hi_rsi = np.nan; runmax = -np.inf
    ref_lo_p = -1; ref_lo = np.nan; ref_lo_rsi = np.nan; runmin = np.inf
    for t in range(n):
        # adopt pivots confirmed at this bar (pivot bar = t-right; its window includes
        # bar t, so the same bar can never also sweep it -> no ordering conflict)
        if not np.isnan(phv[t]):
            ref_hi_p = t - right; ref_hi = h[ref_hi_p]; ref_hi_rsi = r[ref_hi_p]
            runmax = h[ref_hi_p+1:t].max() if t > ref_hi_p+1 else -np.inf
        if not np.isnan(plv[t]):
            ref_lo_p = t - right; ref_lo = l[ref_lo_p]; ref_lo_rsi = r[ref_lo_p]
            runmin = l[ref_lo_p+1:t].min() if t > ref_lo_p+1 else np.inf
        # ---- bearish: sweep of ref pivot high with weaker RSI ----
        if ref_hi_p >= 0 and (t - ref_hi_p) <= lookback and np.isfinite(ref_hi_rsi):
            if h[t] > ref_hi and h[t] > runmax and r[t] < ref_hi_rsi:
                div_hi[t] = True
                if c[t] < ref_hi:                 # swept + rejected = SFP candle
                    bear0[t] = True
            if t > 0 and div_hi[t-1] and h[t] < h[t-1]:
                bear1[t] = True                   # extreme provisionally in place
            runmax = max(runmax, h[t])
        # ---- bullish: sweep of ref pivot low with stronger RSI ----
        if ref_lo_p >= 0 and (t - ref_lo_p) <= lookback and np.isfinite(ref_lo_rsi):
            if l[t] < ref_lo and l[t] < runmin and r[t] > ref_lo_rsi:
                div_lo[t] = True
                if c[t] > ref_lo:
                    bull0[t] = True
            if t > 0 and div_lo[t-1] and l[t] > l[t-1]:
                bull1[t] = True
            runmin = min(runmin, l[t])
    return dict(bear0=bear0, bear1=bear1, bull0=bull0, bull1=bull1)

def variants(df):
    m = sfp_divergence(df)
    up = (df["close"] > df["ema200"]).values; dn = ~up
    base_bull = (df["div_bull"] == 1).values
    base_bear = (df["div_bear"] == 1).values
    V = {}
    V["BASE div_bear (3-bar late)"]      = ("S", base_bear)
    V["SFP bear0 (extreme candle)"]      = ("S", m["bear0"])
    V["SFP bear1 (candle after)"]        = ("S", m["bear1"])
    V["SFP bear0|1"]                     = ("S", m["bear0"] | m["bear1"])
    V["BASE div_bear & dn"]              = ("S", base_bear & dn)
    V["SFP bear0|1 & dn (with-trend)"]   = ("S", (m["bear0"] | m["bear1"]) & dn)
    V["SFP bear0|1 & up (counter)"]      = ("S", (m["bear0"] | m["bear1"]) & up)
    V["BASE div_bull (3-bar late)"]      = ("L", base_bull)
    V["SFP bull0 (extreme candle)"]      = ("L", m["bull0"])
    V["SFP bull1 (candle after)"]        = ("L", m["bull1"])
    V["SFP bull0|1"]                     = ("L", m["bull0"] | m["bull1"])
    V["BASE div_bull & up"]              = ("L", base_bull & up)
    V["SFP bull0|1 & up (with-trend)"]   = ("L", (m["bull0"] | m["bull1"]) & up)
    V["SFP bull0|1 & dn (counter)"]      = ("L", (m["bull0"] | m["bull1"]) & dn)
    return V

def scan(tf, rr, atr_mult=1.2, min_n=25):
    df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    wl, ws, sf = forward_outcomes(df, atr_mult, rr)
    df = df.copy(); df["win_L"] = wl; df["win_S"] = ws
    tr = df["dt"] < pd.Timestamp("2024-12-31", tz="UTC"); te = ~tr
    p_be = breakeven_wr(rr, np.nanmean(sf))
    print(f"\n===== A) conditional WR  TF={tf} rr={rr} atr_mult={atr_mult} "
          f"(net breakeven WR={p_be:.1%}) =====")
    print(f"  {'variant':34} side  trainWR    n    testWR    n")
    for name, (side, mask) in variants(df).items():
        col = df["win_L"] if side == "L" else df["win_S"]
        wtr = col[tr & mask].dropna(); wte = col[te & mask].dropna()
        if len(wtr) < min_n or len(wte) < min_n:
            print(f"  {name:34} {side:4}  (too few: n_tr={len(wtr)} n_te={len(wte)})")
            continue
        flag = "  <<<" if (wtr.mean() > p_be and wte.mean() > p_be) else ""
        print(f"  {name:34} {side:4} {wtr.mean():7.1%} {len(wtr):5d} "
              f"{wte.mean():7.1%} {len(wte):5d}{flag}")

def make_30m():
    """Synthesize a 30m frame by resampling the 15m data (no native 30m export)."""
    import os
    if os.path.exists("data/30m.parquet"):
        return
    df = pd.read_parquet("data/15m.parquet").set_index("dt")
    r = df.resample("30min").agg(open=("open", "first"), high=("high", "max"),
                                 low=("low", "min"), close=("close", "last"),
                                 volume=("volume", "sum")).dropna(subset=["open"])
    r = r.reset_index()
    r["time"] = ((r["dt"] - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1)).astype("int64")
    r.to_parquet("data/30m.parquet")
    print(f"built data/30m.parquet: {len(r)} bars {r['dt'].iloc[0]} -> {r['dt'].iloc[-1]}")

def trade_sim(tf="4H", rr=2.0, atr_mult=1.5, df=None):
    if df is None:
        df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    n = len(df)
    sfmean = (atr_mult*df["atr14"]/df["open"].shift(-1)).mean()
    p_be = breakeven_wr(rr, sfmean)
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    yrs = (df["time"].iloc[-1]-df["time"].iloc[0])/86400/365.25
    print(f"\n===== B) trade sim {tf}  run_fixed {atr_mult}*ATR stop rr={rr} "
          f"(stop~{sfmean:.3%} of price, feeR~{0.0008/sfmean:.2f}, "
          f"breakeven WR~{p_be:.1%}) =====")
    for name, (side, mask) in variants(df).items():
        L = mask if side == "L" else np.zeros(n, bool)
        S = mask if side == "S" else np.zeros(n, bool)
        t = run_fixed(df, L, S, rr=rr, atr_mult=atr_mult)
        out = []
        for lab, sub in [("TR", t[t.entry_time < cut]), ("TE", t[t.entry_time >= cut])]:
            if not len(sub):
                out.append(f"{lab}: (none)"); continue
            R = sub["net_R"].values
            wr = (sub["outcome"] == "target").mean()
            out.append(f"{lab}: n={len(sub):4d} WR={wr:5.1%} expR={R.mean():+.3f}")
        ok = (len(t[t.entry_time < cut]) and len(t[t.entry_time >= cut])
              and t[t.entry_time < cut]["net_R"].mean() > 0
              and t[t.entry_time >= cut]["net_R"].mean() > 0)
        freq = len(t)/(yrs*12)
        print(f"  {name:34} | " + " | ".join(out) +
              f" | {freq:5.1f}/mo" + ("   <<<" if ok else ""))

if __name__ == "__main__":
    import sys
    tfs = sys.argv[1:]
    if not tfs:                       # original 4H/1h study
        for tf in ["4H", "1h"]:
            for rr in [1.0, 2.0]:
                scan(tf, rr)
        trade_sim("4H", rr=2.0)
        trade_sim("4H", rr=1.0)
    else:
        # lower-TF pass: trade sim only (the per-bar scan is O(n*max_bars) pure
        # python -- impractical at 190k-530k bars; run_fixed walks signals only)
        for tf in tfs:
            if tf == "30m":
                make_30m()
            df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
            for rr in [2.0, 1.0]:
                trade_sim(tf, rr=rr, df=df)
            if tf in ("15m", "5m"):   # wider-stop fee-mitigation check
                for rr in [2.0, 1.0]:
                    trade_sim(tf, rr=rr, atr_mult=3.0, df=df)
