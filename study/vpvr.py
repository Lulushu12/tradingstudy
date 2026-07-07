"""Volume Profile (VPVR / rolling Fixed-Range) strategies, causal.

For each bar we build a volume-at-price profile from a TRAILING window of W closed
bars (bars i-W+1..i, all known at the close of i). Each bar's volume is spread across
the price range it traded [low,high], overlap-weighted onto a fixed log-price grid.
From the profile we derive:
    POC  = price bin with the most volume (point of control)
    VAH/VAL = high/low bounds of the Value Area (central 70% of volume around POC)

Signal read on close of i, entry NEXT bar open, stop=1.5*ATR, target rr*stop.
Families tested:
  ROTATION  (mean-revert inside value): tag VAL and hold -> long toward POC; tag VAH
            and hold -> short toward POC; POC re-test fades.
  BREAKOUT  (acceptance out of value): close accepted beyond VAH -> long continuation;
            beyond VAL -> short; strongest with trend.
Sliced train<2025 / test>=2025 vs fee-adjusted breakeven WR, same as research.py.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from engine import FEE_RT

def build_profile(df, W=150, B=240, va=0.70):
    """Return per-bar arrays: poc, vah, val (prices). NaN until first full window."""
    lo=df["low"].values.astype(float); hi=df["high"].values.astype(float)
    vol=df["volume"].values.astype(float); n=len(df)
    llo=np.log(lo); lhi=np.log(hi)
    edges=np.linspace(llo.min(), lhi.max(), B+1)
    centers=0.5*(edges[:-1]+edges[1:])
    bw=edges[1]-edges[0]
    # per-bar contribution onto grid (overlap-weighted), sparse via loop
    contrib=np.zeros((n,B))
    for i in range(n):
        a=lhi[i]-llo[i]
        if not np.isfinite(vol[i]) or vol[i]<=0:
            continue
        if a<=bw*0.5:                    # bar sits inside ~one bin
            k=min(int((0.5*(llo[i]+lhi[i])-edges[0])/bw), B-1); k=max(k,0)
            contrib[i,k]=vol[i]; continue
        ka=max(int((llo[i]-edges[0])/bw),0); kb=min(int((lhi[i]-edges[0])/bw),B-1)
        seg=edges[ka:kb+2]
        ov=np.minimum(seg[1:],lhi[i])-np.maximum(seg[:-1],llo[i])
        ov=np.clip(ov,0,None); s=ov.sum()
        if s>0: contrib[i,ka:kb+1]=vol[i]*ov/s
    S=np.vstack([np.zeros(B), np.cumsum(contrib,axis=0)])   # S[k]=sum of first k rows
    poc=np.full(n,np.nan); vah=np.full(n,np.nan); val=np.full(n,np.nan)
    for i in range(W-1,n):
        prof=S[i+1]-S[i+1-W]
        tot=prof.sum()
        if tot<=0: continue
        p=int(np.argmax(prof))
        acc=prof[p]; loi=hii=p; tgt=tot*va
        while acc<tgt and (loi>0 or hii<B-1):
            left=prof[loi-1] if loi>0 else -1.0
            right=prof[hii+1] if hii<B-1 else -1.0
            if right>=left: hii+=1; acc+=prof[hii]
            else: loi-=1; acc+=prof[loi]
        poc[i]=np.exp(centers[p]); val[i]=np.exp(edges[loi]); vah[i]=np.exp(edges[hii+1])
    return poc,vah,val

def build(tf="4H", W=150):
    df=ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    poc,vah,val=build_profile(df, W=W)
    df["poc"]=poc; df["vah"]=vah; df["val"]=val
    return df

def run(tf="4H", rr=2.0, W=150, atr_mult=1.5, max_bars=300):
    df=build(tf, W=W)
    wl,ws,sf=forward_outcomes(df, atr_mult, rr, max_bars)
    d=df.copy(); d["win_L"]=wl; d["win_S"]=ws
    cut=pd.Timestamp("2024-12-31",tz="UTC"); tr=(d["dt"]<cut).values; te=~tr
    p_be=breakeven_wr(rr, np.nanmean(sf))
    o=df["open"].values; c=df["close"].values; l=df["low"].values; h=df["high"].values
    poc=df["poc"].values; vah=df["vah"].values; val=df["val"].values
    up=(df["close"]>df["ema200"]).values; dn=~up
    have=np.isfinite(poc)
    pc=df["close"].shift(1).values                 # prior close (causal)

    # ---- ROTATION: tag a value edge and close back inside, room toward POC ----
    rot_L = have & (l<=val) & (c>val) & (c<poc)                 # bought VAL, below POC
    rot_S = have & (h>=vah) & (c<vah) & (c>poc)                 # sold VAH, above POC
    # POC re-test fade: close crosses POC from one side (revert to prior side)
    poc_L = have & (l<=poc) & (c>poc) & (c<vah)                 # held POC from above
    poc_S = have & (h>=poc) & (c<poc) & (c>val)

    # ---- BREAKOUT: acceptance beyond the value area (prior close inside) ----
    brk_L = have & (c>vah) & (pc<=vah)
    brk_S = have & (c<val) & (pc>=val)

    conds={
      "rotation VAL->POC (long)":("L", rot_L),
      "rotation VAH->POC (short)":("S", rot_S),
      "rotation VAL->POC +trend (long)":("L", rot_L&up),
      "rotation VAH->POC +trend (short)":("S", rot_S&dn),
      "POC hold-from-above (long)":("L", poc_L),
      "POC hold-from-below (short)":("S", poc_S),
      "VAH breakout accept (long)":("L", brk_L),
      "VAL breakdown accept (short)":("S", brk_S),
      "VAH breakout +trend (long)":("L", brk_L&up),
      "VAL breakdown +trend (short)":("S", brk_S&dn),
    }
    print(f"\n===== VPVR TF={tf} W={W} rr={rr} | breakeven WR={p_be:.1%} (stopfrac~{np.nanmean(sf):.3%}) =====")
    print(f"  {'condition':40} side  trainWR  n     testWR  n")
    rows=[]
    for name,(sidew,mask) in conds.items():
        col=d["win_L"] if sidew=="L" else d["win_S"]
        m=pd.Series(mask,index=d.index).values
        wtr=col[tr&m].dropna(); wte=col[te&m].dropna()
        okn=len(wtr)>=25 and len(wte)>=15
        ok=okn and wtr.mean()>p_be and wte.mean()>p_be
        rows.append((name,sidew,wtr.mean() if len(wtr) else np.nan,len(wtr),
                     wte.mean() if len(wte) else np.nan,len(wte),ok))
    rows.sort(key=lambda r:-(min(r[2],r[4]) if np.isfinite(r[2]) and np.isfinite(r[4]) else -1))
    for name,sidew,trw,ntr,tew,nte,ok in rows:
        tw=f"{trw:.1%}" if np.isfinite(trw) else "  -"
        ew=f"{tew:.1%}" if np.isfinite(tew) else "  -"
        print(f"  {name:40} {sidew:3} {tw:>6} {ntr:5d}  {ew:>6} {nte:5d}{'  <<<' if ok else ''}")

if __name__=="__main__":
    import sys
    tf=sys.argv[1] if len(sys.argv)>1 else "4H"
    W=int(sys.argv[2]) if len(sys.argv)>2 else 150
    for rr in [1.0,2.0]:
        run(tf=tf, rr=rr, W=W)
