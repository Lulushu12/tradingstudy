"""Hidden RSI divergence (continuation) + expanding volume, with-trend.

Hidden bullish (uptrend continuation LONG): price makes a HIGHER pivot-low while RSI makes
a LOWER low -> trend pausing, momentum reset, likely to resume up.
Hidden bearish (downtrend continuation SHORT): price LOWER pivot-high while RSI HIGHER high.
Both detected at pivot CONFIRMATION bars (causal, same machinery as regular divergence).

'Growing volume into the signal' = volume expanding as the second pivot forms (rolling-3
mean rising, and/or vol_ratio>1) -> conviction behind the continuation. Entry next 4H open,
stop 1.5*ATR. Tested with fixed-2R (WR vs breakeven) and scale-out (half@2R + half 3-ATR
trail). Compared to the volume-spike baseline. Train<2025 / Test>=2025.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT
from research import breakeven_wr
from finalists import make_signals
from trend_runner import run_fixed
from hybrid_exit import run_hybrid

def hidden_divergence(df, left=3, right=3, lookback=40):
    ph,pl=ind.pivots(df,left,right); n=len(df)
    hb=np.zeros(n); hs=np.zeros(n)
    low_idx=[i for i in range(n) if not np.isnan(pl.iloc[i])]
    high_idx=[i for i in range(n) if not np.isnan(ph.iloc[i])]
    lows=df["low"].values; highs=df["high"].values; r=df["rsi14"].values
    for k in range(1,len(low_idx)):
        i=low_idx[k]; j=low_idx[k-1]; pi,pj=i-right,j-right
        if i-j>lookback: continue
        if lows[pi]>lows[pj] and r[pi]<r[pj]: hb[i]=1        # higher low, lower RSI
    for k in range(1,len(high_idx)):
        i=high_idx[k]; j=high_idx[k-1]; pi,pj=i-right,j-right
        if i-j>lookback: continue
        if highs[pi]<highs[pj] and r[pi]>r[pj]: hs[i]=1      # lower high, higher RSI
    return hb,hs

def rep(tag, tr, p_be):
    cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
    out=[]
    for lab,sub in [("TR",tr[tr.entry_time<cut]),("TE",tr[tr.entry_time>=cut])]:
        if not len(sub): out.append(f"{lab}: (none)"); continue
        R=sub["net_R"].values
        wr=(sub["outcome"]=="target").mean() if "target" in set(sub["outcome"]) else (R>0).mean()
        out.append(f"{lab}: n={len(sub)} WR={wr:.1%} expR={R.mean():+.3f}")
    ok = tr[tr.entry_time<cut]["net_R"].mean()>0 and len(tr[tr.entry_time>=cut]) and tr[tr.entry_time>=cut]["net_R"].mean()>0
    print(f"  {tag:46} | "+" | ".join(out)+("   <<<" if ok else ""))

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    hb,hs=hidden_divergence(df); n=len(df)
    hb=hb.astype(bool); hs=hs.astype(bool)
    # recency (signal valid for K bars after confirmation)
    K=4
    hb_r=pd.Series(hb).rolling(K,min_periods=1).max().values.astype(bool)
    hs_r=pd.Series(hs).rolling(K,min_periods=1).max().values.astype(bool)
    up=(df["close"]>df["ema200"]).values; dn=~up
    vr=df.get("vol_ratio",pd.Series(np.nan,index=df.index)).values
    volup=vr>1.0
    v3=pd.Series(df["volume"].values).rolling(3).mean()
    volrise=(v3>v3.shift(3)).values                          # expanding volume
    L0=hb_r; S0=hs_r
    variants={
      "hidden-div (long)":                (L0,               "L"),
      "hidden-div + uptrend (long)":      (L0&up,            "L"),
      "hidden-div + vol_rise (long)":     (L0&volrise,       "L"),
      "hidden-div + uptrend + vol_rise (long)":(L0&up&volrise,"L"),
      "hidden-div + uptrend + vol>avg (long)": (L0&up&volup,  "L"),
      "hidden-div (short)":               (S0,               "S"),
      "hidden-div + downtrend (short)":   (S0&dn,            "S"),
      "hidden-div + vol_rise (short)":    (S0&volrise,       "S"),
      "hidden-div + downtrend + vol_rise (short)":(S0&dn&volrise,"S"),
      "hidden-div + downtrend + vol>avg (short)":(S0&dn&volup,"S"),
    }
    for rr,mode in [(2.0,"fixed"),(2.0,"hybrid")]:
        sfmean=(1.5*df["atr14"]/df["open"].shift(-1)).mean()
        p_be=breakeven_wr(rr, sfmean)
        print(f"\n===== hidden-div 4H  exit={mode} rr={rr}  (breakeven WR~{p_be:.1%}) =====")
        for name,(mask,side) in variants.items():
            L=mask if side=="L" else np.zeros(n,bool)
            S=mask if side=="S" else np.zeros(n,bool)
            tr=run_fixed(df,L,S,rr=rr) if mode=="fixed" else run_hybrid(df,L,S,tp=2.0,k=3.0)
            rep(name, tr, p_be)
    # baseline reference
    print("\n----- reference: volume-spike continuation -----")
    Lv,Sv=make_signals(df,"volspike")
    for mode in ["fixed","hybrid"]:
        tr=run_fixed(df,Lv,Sv,rr=2.0) if mode=="fixed" else run_hybrid(df,Lv,Sv,tp=2.0,k=3.0)
        rep(f"volspike ({mode})", tr, 0.34)

if __name__=="__main__":
    main()
