"""Validate the VPVR POC-hold-from-above LONG on the true 15m price path, then fold it
into the reference book (full rejection-shorts + volume-spike longs) and re-measure.

POC-hold-from-above long: with a trailing W=300-bar volume profile, price dips to the
point-of-control (low<=POC) but closes back above it and still below the value-area high
(c>POC & c<VAH) -> continuation long. Entry next 4H open, stop 1.5*ATR, target rr*stop,
resolved bar-by-bar on 15m. Train<2025 / Test>=2025.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT
from finalists import sim_equity, fmt
from vpvr import build_profile
from combined import make_combined

def poc_signals(df, W=300):
    poc,vah,val=build_profile(df, W=W)
    c=df["close"].values; l=df["low"].values; h=df["high"].values
    have=np.isfinite(poc)
    L = have & (l<=poc) & (c>poc) & (c<vah)      # POC hold-from-above -> long
    S = have & (h>=poc) & (c<poc) & (c>val)      # POC hold-from-below -> short
    return L, S

def resolve_15m(df4, L, S, rr, atr_mult=1.5, max_hold_hours=300*4):
    f=pd.read_parquet("data/15m.parquet").sort_values("time").reset_index(drop=True)
    ft=f["time"].values; fh=f["high"].values; fl=f["low"].values; fo=f["open"].values; fc=f["close"].values
    o4=df4["open"].values; t4=df4["time"].values; atrv=df4["atr14"].values; n=len(df4); idx=np.arange(n)
    sig=[(i,+1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i]>0]+\
        [(i,-1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i]>0]
    sig.sort(); rows=[]
    for i,s in sig:
        ei=i+1
        if ei>=n: continue
        entry=o4[ei]; rdist=atr_mult*atrv[i]
        stop=entry-s*rdist; tgt=entry+s*rr*rdist; sf=rdist/entry; t_entry=t4[ei]
        a=np.searchsorted(ft,t_entry,"left"); b=np.searchsorted(ft,t_entry+max_hold_hours*3600,"right")
        outcome=None; exitp=None; j=a
        for j in range(a,min(b,len(ft))):
            if s>0: hs=fl[j]<=stop; ht=fh[j]>=tgt
            else:   hs=fh[j]>=stop; ht=fl[j]<=tgt
            if hs and ht:
                outcome,exitp=("stop",stop) if abs(fo[j]-stop)<=abs(fo[j]-tgt) else ("target",tgt); break
            elif hs: outcome,exitp="stop",stop; break
            elif ht: outcome,exitp="target",tgt; break
        if outcome is None: outcome,exitp="timeout",fc[min(j,len(fc)-1)]
        gross=rr if outcome=="target" else (-1.0 if outcome=="stop" else s*(exitp-entry)/rdist)
        rows.append(dict(entry_time=t_entry, exit_time=ft[min(j,len(ft)-1)], side=s,
                         outcome=outcome, gross_R=gross, fee_R=FEE_RT/sf, net_R=gross-FEE_RT/sf,
                         stop_dist_frac=sf, entry_i=0, exit_i=0))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def report(tag, tr15, rr):
    cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
    print(f"\n--- {tag}  rr={rr} ---")
    for lab,sub in [("TRAIN",tr15[tr15.entry_time<cut]),("TEST",tr15[tr15.entry_time>=cut])]:
        w=(sub["outcome"]=="target").sum(); r=sub["outcome"].isin(["target","stop"]).sum()
        wr=w/r if r else float("nan")
        print(f"    {lab}: n={len(sub)} WR={wr:.1%} expR={sub['net_R'].mean():+.3f}")
    for mode in ["single","concurrent"]:
        _,m=sim_equity(tr15, mode=mode)
        print("   ",fmt(m))

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    pocL,pocS=poc_signals(df, W=300)
    for rr in [1.0,2.0]:
        # (1) standalone POC-hold-from-above long, 15m-path
        trL=resolve_15m(df, pocL, np.zeros(len(df),bool), rr)
        report("VPVR POC-hold LONG standalone (15m-path)", trL, rr)
        # (2) reference book: full rejection-shorts + volspike longs, + POC long, drop dual-fire
        baseL,baseS=make_combined(df, strong=False, long_mode="volspike")
        fullL = baseL | pocL
        both = fullL & baseS
        fullL = fullL & ~both; fullS = baseS & ~both
        trBook=resolve_15m(df, fullL, fullS, rr)
        report("REFERENCE book + POC long (15m-path)", trBook, rr)
        # (3) reference book WITHOUT poc long, for comparison
        b2=baseL & ~(baseL&baseS); s2=baseS & ~(baseL&baseS)
        trBase=resolve_15m(df, b2, s2, rr)
        report("REFERENCE book baseline, no POC (15m-path)", trBase, rr)

if __name__=="__main__":
    main()
