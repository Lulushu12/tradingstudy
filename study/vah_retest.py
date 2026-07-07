"""Value-area edge as a support/resistance FLIP, with-trend continuation (breakout-retest).

LONG:  price has accepted ABOVE the VAH, then pulls back and RETESTS the VAH from above
       (bar's low tags VAH) but CLOSES back above it (continuation/hold). Enter next open,
       stop just BELOW the VAH (structural invalidation). Mirror SHORT at the VAL.

This is with-trend (unlike the failed fade): the level flips from resistance to support
and we ride the continuation. Because the stop sits right at the level, 1R is small and the
upside is open, so we test both a fixed-2R exit (win-rate vs fee breakeven) and the scale-out
(half @2R + half on a 3-ATR trail) to see the ride. Causal, entry next 4H open, train/test.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT
from vpvr import build_profile

def sim(df, entries, sides, stops, mode="fixed", rr=2.0, tp=2.0, k=3.0, max_bars=400):
    o=df["open"].values; h=df["high"].values; l=df["low"].values; c=df["close"].values
    atrv=df["atr14"].values; t=df["time"].values; n=len(df)
    rows=[]
    for i,s,stopP in zip(entries,sides,stops):
        ei=i+1
        if ei>=n: continue
        entry=o[ei]; rdist=abs(entry-stopP)
        if rdist<=0 or not np.isfinite(rdist): continue
        sf=rdist/entry
        if mode=="fixed":
            stop=entry-s*rdist; tgt=entry+s*rr*rdist; outcome=None; exitp=None; ej=ei
            for j in range(ei,min(ei+max_bars,n)):
                ej=j; hs=(l[j]<=stop) if s>0 else (h[j]>=stop); ht=(h[j]>=tgt) if s>0 else (l[j]<=tgt)
                if hs and ht: outcome,exitp=("stop",stop) if abs(o[j]-stop)<=abs(o[j]-tgt) else ("target",tgt); break
                elif hs: outcome,exitp="stop",stop; break
                elif ht: outcome,exitp="target",tgt; break
            if outcome is None: outcome,exitp="timeout",c[ej]
            R=s*(exitp-entry)/rdist
            rows.append(dict(entry_time=t[ei],side=s,outcome=outcome,net_R=R-FEE_RT/sf,stop_dist_frac=sf))
        else:  # hybrid scale-out
            tgt=entry+s*tp*rdist; trail=entry-s*rdist; extreme=entry
            half1=None; half2=None; ej=ei; running=True
            for j in range(ei,min(ei+max_bars,n)):
                if s>0: stop_hit=l[j]<=trail; tgt_hit=(half1 is None) and (h[j]>=tgt)
                else:   stop_hit=h[j]>=trail; tgt_hit=(half1 is None) and (l[j]<=tgt)
                if stop_hit and tgt_hit:
                    if abs(o[j]-trail)<=abs(o[j]-tgt): R=s*(trail-entry)/rdist; half1=R; half2=R; ej=j; running=False; break
                    else: half1=tp
                elif stop_hit:
                    R=s*(trail-entry)/rdist
                    if half1 is None: half1=R
                    half2=R; ej=j; running=False; break
                elif tgt_hit: half1=tp
                ka=atrv[j] if np.isfinite(atrv[j]) else atrv[i]
                if s>0: extreme=max(extreme,h[j]); trail=max(trail,extreme-k*ka)
                else:   extreme=min(extreme,l[j]); trail=min(trail,extreme+k*ka)
                ej=j
            if running:
                R=s*(c[ej]-entry)/rdist
                if half1 is None: half1=R
                half2=R; outcome="run_open"
            else: outcome="win" if (0.5*half1+0.5*half2)>0 else "loss"
            net=0.5*half1+0.5*half2-FEE_RT/sf
            rows.append(dict(entry_time=t[ei],side=s,outcome=outcome,net_R=net,stop_dist_frac=sf))
    return pd.DataFrame(rows)

def rep(tag, tr, p_be=None):
    cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
    print(f"\n--- {tag} ---")
    if not len(tr): print("    (no trades)"); return
    for lab,sub in [("TRAIN",tr[tr.entry_time<cut]),("TEST",tr[tr.entry_time>=cut])]:
        if not len(sub): print(f"    {lab}: (none)"); continue
        R=sub["net_R"].values
        wr=(sub["outcome"]=="target").mean() if "target" in set(sub["outcome"]) else (R>0).mean()
        flag=""
        if p_be is not None: flag="  <<<" if (R>0).mean()>0 and wr>p_be else ""
        print(f"    {lab}: n={len(sub)} WR/hit={wr:.1%} expR={R.mean():+.3f} medR={np.median(R):+.2f}{flag}")

def signals(df, W=300, tol=0.15, buf=0.25, tight_days=8):
    poc,vah,val=build_profile(df, W=W)
    c=df["close"].values; o=df["open"].values; h=df["high"].values; l=df["low"].values
    atrv=df["atr14"].values; n=len(df)
    up=(c>df["ema200"].values); dn=~up
    prev_above=np.r_[False, c[:-1]>vah[:-1]]     # accepted above VAH on prior bar
    prev_below=np.r_[False, c[:-1]<val[:-1]]
    tolA=tol*atrv
    # LONG retest of VAH from above: dip tags VAH, close holds above, was above before, bullish
    Lmask=np.isfinite(vah)&prev_above&(l<=vah+tolA)&(c>vah)&(c>o)
    Lstop=vah-buf*atrv
    # SHORT retest of VAL from below
    Smask=np.isfinite(val)&prev_below&(h>=val-tolA)&(c<val)&(c<o)
    Sstop=val+buf*atrv
    return Lmask,Lstop,Smask,Sstop,up,dn

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    for W in [300,150]:
        Lm,Ls,Sm,Ss,up,dn=signals(df, W=W)
        idx=np.arange(len(df))
        sets={
          "LONG VAH-retest (any trend)":  (idx[Lm],           +1, Ls[Lm]),
          "LONG VAH-retest + uptrend":    (idx[Lm&up],        +1, Ls[Lm&up]),
          "SHORT VAL-retest (any trend)": (idx[Sm],           -1, Ss[Sm]),
          "SHORT VAL-retest + downtrend": (idx[Sm&dn],        -1, Ss[Sm&dn]),
        }
        print(f"\n================= VPVR retest  W={W}  =================")
        for rr in [2.0]:
            print(f"\n##### FIXED {rr}R exit #####")
            for name,(ii,s,st) in sets.items():
                tr=sim(df, ii, np.full(len(ii),s), st, mode="fixed", rr=rr)
                rep(f"{name}  [fixed {rr}R]", tr)
        print(f"\n##### HYBRID (half@2R + half trail 3ATR) #####")
        for name,(ii,s,st) in sets.items():
            tr=sim(df, ii, np.full(len(ii),s), st, mode="hybrid")
            rep(f"{name}  [hybrid]", tr)

if __name__=="__main__":
    main()
