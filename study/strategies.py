"""Candidate strategies + evaluation harness.

Each strategy returns (long_sig, short_sig, stop_dist_price) as arrays aligned to df.
Signal is read on bar CLOSE; engine enters next bar open. Stops use ATR or structure.

HTF context is merged causally: an HTF bar with open-time T is only usable after its
close (T+duration), enforced via merge_asof on htf close-time.
"""
import numpy as np
import pandas as pd
import indicators as ind
from engine import simulate_trades, equity_stats, fmt

TF_SEC = {"1D":86400,"4H":14400,"1h":3600,"15m":900,"5m":300,"1m":60}

def load_enriched(tf):
    df = pd.read_parquet(f"data/{tf}.parquet")
    return ind.enrich(df)

def merge_htf(df, htf_df, htf_tf, cols):
    """Attach HTF columns (causal: only closed HTF bars)."""
    dur = TF_SEC[htf_tf]
    h = htf_df[["time"]+cols].copy()
    h["close_time"] = h["time"] + dur
    h = h.sort_values("close_time")
    left = df[["time"]].copy().sort_values("time")
    merged = pd.merge_asof(left, h.drop(columns="time"), left_on="time",
                           right_on="close_time", direction="backward")
    merged = merged.set_index(left.index).sort_index()
    for c in cols:
        df[htf_tf+"_"+c] = merged[c].values
    return df

# ---------------- strategy definitions ----------------
def strat_trend_pullback(df, atr_mult=1.2, htf_prefix=None):
    """Uptrend (close>ema200 & ema50>ema200), pullback tags ema20/ema50 zone,
    bullish reversal candle. Symmetric shorts. Stop = atr_mult*ATR."""
    c = df["close"]; up = (c>df["ema200"]) & (df["ema50"]>df["ema200"])
    dn = (c<df["ema200"]) & (df["ema50"]<df["ema200"])
    if htf_prefix:
        up = up & (df[htf_prefix+"_close"]>df[htf_prefix+"_ema200"])
        dn = dn & (df[htf_prefix+"_close"]<df[htf_prefix+"_ema200"])
    near = (df["low"]<=df["ema20"]) | (df["low"]<=df["ema50"])
    near_s = (df["high"]>=df["ema20"]) | (df["high"]>=df["ema50"])
    rev_up = (df["c_bull_engulf"]==1)|(df["c_hammer"]==1)
    rev_dn = (df["c_bear_engulf"]==1)|(df["c_shooting_star"]==1)
    long_sig = up & near & rev_up
    short_sig = dn & near_s & rev_dn
    stop = atr_mult*df["atr14"]
    return long_sig.values, short_sig.values, stop.values

def strat_rsi_div(df, atr_mult=1.0, htf_prefix=None):
    """RSI regular divergence at confirmed pivot. Optional HTF trend alignment."""
    long_sig = df["div_bull"]==1
    short_sig = df["div_bear"]==1
    if htf_prefix:
        long_sig = long_sig & (df[htf_prefix+"_close"]>df[htf_prefix+"_ema200"])
        short_sig = short_sig & (df[htf_prefix+"_close"]<df[htf_prefix+"_ema200"])
    stop = atr_mult*df["atr14"]
    return long_sig.values, short_sig.values, stop.values

def strat_wt_cross(df, atr_mult=1.2, ob=53, os_=-53, htf_prefix=None):
    """WaveTrend cross up from oversold / down from overbought (Market Cipher style)."""
    wt1, wt2 = df["wt1"], df["wt2"]
    cross_up = (wt1>wt2) & (wt1.shift(1)<=wt2.shift(1)) & (wt1< os_+20)
    cross_dn = (wt1<wt2) & (wt1.shift(1)>=wt2.shift(1)) & (wt1> ob-20)
    long_sig = cross_up; short_sig = cross_dn
    if htf_prefix:
        long_sig = long_sig & (df[htf_prefix+"_close"]>df[htf_prefix+"_ema200"])
        short_sig = short_sig & (df[htf_prefix+"_close"]<df[htf_prefix+"_ema200"])
    stop = atr_mult*df["atr14"]
    return long_sig.values, short_sig.values, stop.values

def strat_bb_reversion(df, atr_mult=1.0, htf_prefix=None):
    """Close back inside lower/upper band after poking outside (mean reversion)."""
    below = df["close"].shift(1) < df["bb_lo"].shift(1)
    back = df["close"] > df["bb_lo"]
    above = df["close"].shift(1) > df["bb_up"].shift(1)
    backd = df["close"] < df["bb_up"]
    long_sig = below & back
    short_sig = above & backd
    stop = atr_mult*df["atr14"]
    return long_sig.values, short_sig.values, stop.values

def strat_sweep_reclaim(df, lookback=10, atr_mult=1.0, htf_prefix=None):
    """Liquidity sweep: bar low breaks prior N-bar low then closes back above it
    (failed breakdown -> long). Symmetric for highs -> short."""
    prior_low = df["low"].shift(1).rolling(lookback).min()
    prior_high = df["high"].shift(1).rolling(lookback).max()
    long_sig = (df["low"] < prior_low) & (df["close"] > prior_low)
    short_sig = (df["high"] > prior_high) & (df["close"] < prior_high)
    if htf_prefix:
        long_sig = long_sig & (df[htf_prefix+"_close"]>df[htf_prefix+"_ema200"])
        short_sig = short_sig & (df[htf_prefix+"_close"]<df[htf_prefix+"_ema200"])
    stop = atr_mult*df["atr14"]
    return long_sig.values, short_sig.values, stop.values

STRATS = {
    "trend_pullback": strat_trend_pullback,
    "rsi_div": strat_rsi_div,
    "wt_cross": strat_wt_cross,
    "bb_reversion": strat_bb_reversion,
    "sweep_reclaim": strat_sweep_reclaim,
}

def run_strategy(df, fn, rr, resolve="nearest_open", max_bars=400, **kw):
    long_sig, short_sig, stop = fn(df, **kw)
    idx = np.arange(len(df))
    valid = np.isfinite(stop) & (df["atr14"].values>0)
    L = idx[(long_sig) & valid]
    S = idx[(short_sig) & valid]
    entries = np.concatenate([L,S])
    side = np.concatenate([np.ones(len(L)), -np.ones(len(S))])
    stop_d = np.concatenate([stop[L], stop[S]])
    order = np.argsort(entries)
    tr = simulate_trades(df, entries[order], side[order], stop_d[order], rr,
                         max_bars=max_bars, resolve=resolve)
    return tr

def split_mask(df, train_end="2024-12-31"):
    return df["dt"] < pd.Timestamp(train_end, tz="UTC")

def evaluate_all(tf, htf_tf=None, rrs=(1.0,2.0), resolve="nearest_open"):
    df = load_enriched(tf)
    htf_prefix = None
    if htf_tf:
        htf = load_enriched(htf_tf)
        df = merge_htf(df, htf, htf_tf, ["close","ema200"])
        htf_prefix = htf_tf
    tr_mask = split_mask(df).values
    print(f"\n===== TF={tf}  HTF={htf_tf}  bars={len(df)}  "
          f"{df['dt'].iloc[0].date()}..{df['dt'].iloc[-1].date()} =====")
    for name, fn in STRATS.items():
        kw = {}
        if htf_prefix and name in ("trend_pullback","rsi_div","wt_cross","sweep_reclaim"):
            kw["htf_prefix"] = htf_prefix
        for rr in rrs:
            try:
                tr = run_strategy(df, fn, rr, resolve=resolve, **kw)
            except Exception as e:
                print(f"  {name:16} rr={rr}  ERROR {e}"); continue
            if len(tr)==0:
                print(f"  {name:16} rr={rr}  no trades"); continue
            tri = tr[tr["entry_time"] < df.loc[tr_mask.sum()-1,"time"] if tr_mask.sum()>0 else 0]
            # split by date
            cutoff = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
            train = tr[tr["entry_time"] < cutoff]
            test  = tr[tr["entry_time"] >= cutoff]
            mtr,_ = equity_stats(train); mte,_ = equity_stats(test)
            print(f"  {name:16} rr={rr}")
            print(f"      TRAIN {fmt(mtr)}")
            print(f"      TEST  {fmt(mte)}")

if __name__ == "__main__":
    import sys
    tf = sys.argv[1] if len(sys.argv)>1 else "1h"
    htf = sys.argv[2] if len(sys.argv)>2 else None
    evaluate_all(tf, htf)
