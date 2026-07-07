"""VWAP and Heikin-Ashi families, causal, scanned like research.py.

VWAP: daily-anchored (vwap_d), rolling(20), and weekly-anchored. Tested as (a) trend
continuation (pullback to VWAP holds in trend), (b) reclaim (cross back through), and
(c) mean-reversion (price stretched far from VWAP -> fade).

Heikin-Ashi: causal HA candles. Tested as color-flip entries, streak continuation, and
'strong' (wickless) HA candles, on the execution TF; plus HTF-HA regime + execution-TF
flip (HA on 1D gating 4H entries, and HA on 4H gating 1h entries).

Per-bar forward outcome (entry next open, stop 1.5*ATR, target rr*stop) sliced by each
condition, train<2025 vs test>=2025 vs fee breakeven. rr in {1,2}.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from confluence import merge_htf

def ha(df):
    o=df["open"].values; h=df["high"].values; l=df["low"].values; c=df["close"].values
    n=len(df); hc=(o+h+l+c)/4.0; ho=np.empty(n)
    ho[0]=(o[0]+c[0])/2.0
    for i in range(1,n): ho[i]=(ho[i-1]+hc[i-1])/2.0     # recursive, uses only prior bar
    hh=np.maximum.reduce([h,ho,hc]); hl=np.minimum.reduce([l,ho,hc])
    bull=hc>ho
    df["ha_bull"]=bull.astype(int)
    df["ha_strong_bull"]=((hc>ho)&(hl>=np.minimum(ho,hc)-1e-9)&(hl>=ho-1e-9)).astype(int)  # no lower wick
    df["ha_strong_bear"]=((hc<ho)&(hh<=ho+1e-9)).astype(int)                                 # no upper wick
    df["ha_flip_up"]=((bull)&(~np.r_[False,bull[:-1]])).astype(int)   # bear->bull
    df["ha_flip_dn"]=((~bull)&(np.r_[False,bull[:-1]])).astype(int)   # bull->bear
    # streak length (causal)
    st=np.zeros(n,int)
    for i in range(n): st[i]= (st[i-1]+1 if (i>0 and bull[i]==bull[i-1]) else 1)
    df["ha_streak"]=st; df["ha_streak_bull"]=np.where(bull, st, 0)
    df["ha_streak_bear"]=np.where(~bull, st, 0)
    return df

def weekly_vwap(df):
    tp=(df["high"]+df["low"]+df["close"])/3
    wk=df["dt"].dt.to_period("W").astype(str)
    pv=(tp*df["volume"]).groupby(wk).cumsum(); v=df["volume"].groupby(wk).cumsum()
    return (pv/v).values

def scan(tf, htf, rr, max_bars=300):
    df=ha(ind.enrich(pd.read_parquet(f"data/{tf}.parquet")))
    df["wvwap"]=weekly_vwap(df); df["rvwap"]=ind.rolling_vwap(df,20).values
    # HTF Heikin-Ashi regime merged causally
    dh=ha(ind.enrich(pd.read_parquet(f"data/{htf}.parquet")))
    df=merge_htf(df, dh, htf, ["ha_bull"])
    wl,ws,sf=forward_outcomes(df, 1.5, rr, max_bars)
    d=df.copy(); d["win_L"]=wl; d["win_S"]=ws
    cut=pd.Timestamp("2024-12-31",tz="UTC"); tr=(d["dt"]<cut).values; te=~tr
    p_be=breakeven_wr(rr, np.nanmean(sf))
    c=df["close"].values; o=df["open"].values; l=df["low"].values; h=df["high"].values
    atr=df["atr14"].values
    up=(c>df["ema200"].values); dn=~up
    vwd=df["vwap_d"].values; rvw=df["rvwap"].values; wvw=df["wvwap"].values
    pc=np.r_[np.nan,c[:-1]]
    strch=(c-rvw)/atr
    htf_bull=(df[htf+"_ha_bull"].values==1); htf_bear=(df[htf+"_ha_bull"].values==0)
    C={
      # VWAP continuation
      "vwap_d bounce +uptrend (L)":("L",(l<=vwd)&(c>vwd)&up),
      "vwap_d bounce +downtrend (S)":("S",(h>=vwd)&(c<vwd)&dn),
      "vwap_d reclaim (L)":("L",(c>vwd)&(pc<=vwd)),
      "vwap_d lose (S)":("S",(c<vwd)&(pc>=vwd)),
      "wvwap bounce +uptrend (L)":("L",(l<=wvw)&(c>wvw)&up),
      "wvwap bounce +downtrend (S)":("S",(h>=wvw)&(c>=wvw)&dn) if False else ("S",(h>=wvw)&(c<wvw)&dn),
      # VWAP reversion (fade the stretch)
      "rvwap revert far-above (S)":("S",strch>2.0),
      "rvwap revert far-below (L)":("L",strch<-2.0),
      # Heikin-Ashi execution-TF
      "HA flip up +uptrend (L)":("L",(df["ha_flip_up"].values==1)&up),
      "HA flip dn +downtrend (S)":("S",(df["ha_flip_dn"].values==1)&dn),
      "HA streak>=3 bull +uptrend (L)":("L",(df["ha_streak_bull"].values>=3)&up),
      "HA streak>=3 bear +downtrend (S)":("S",(df["ha_streak_bear"].values>=3)&dn),
      "HA strong-bull +uptrend (L)":("L",(df["ha_strong_bull"].values==1)&up),
      "HA strong-bear +downtrend (S)":("S",(df["ha_strong_bear"].values==1)&dn),
      # HTF-HA regime + execution flip
      f"{htf}-HA bull + exec HA flip up (L)":("L",htf_bull&(df["ha_flip_up"].values==1)),
      f"{htf}-HA bear + exec HA flip dn (S)":("S",htf_bear&(df["ha_flip_dn"].values==1)),
      f"{htf}-HA bull + exec strong-bull (L)":("L",htf_bull&(df["ha_strong_bull"].values==1)),
      f"{htf}-HA bear + exec strong-bear (S)":("S",htf_bear&(df["ha_strong_bear"].values==1)),
    }
    print(f"\n===== TF={tf} HTF={htf} rr={rr} | breakeven WR={p_be:.1%} (stopfrac~{np.nanmean(sf):.3%}) =====")
    print(f"  {'condition':44} side  trainWR  n     testWR  n")
    rows=[]
    for name,(side,mask) in C.items():
        mask=np.asarray(mask,bool)
        col=d["win_L"] if side=="L" else d["win_S"]
        wtr=col[tr&mask].dropna(); wte=col[te&mask].dropna()
        okn=len(wtr)>=30 and len(wte)>=20
        ok=okn and wtr.mean()>p_be and wte.mean()>p_be
        rows.append((name,side,wtr.mean() if len(wtr) else np.nan,len(wtr),
                     wte.mean() if len(wte) else np.nan,len(wte),ok))
    rows.sort(key=lambda r:-(min(r[2],r[4]) if np.isfinite(r[2]) and np.isfinite(r[4]) else -1))
    for name,side,trw,ntr,tew,nte,ok in rows:
        tw=f"{trw:.1%}" if np.isfinite(trw) else "  -"; ew=f"{tew:.1%}" if np.isfinite(tew) else "  -"
        print(f"  {name:44} {side:3} {tw:>6} {ntr:5d}  {ew:>6} {nte:5d}{'  <<<' if ok else ''}")

def main():
    for tf,htf in [("4H","1D"),("1h","4H")]:
        for rr in [1.0,2.0]:
            scan(tf, htf, rr)

if __name__=="__main__":
    main()
