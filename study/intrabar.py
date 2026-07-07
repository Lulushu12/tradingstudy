"""Validate the finalist by resolving each 4H trade with the true 15m price path,
instead of the nearest_open same-bar heuristic. If WR/expR survive, the edge is
credible and not an artifact of intrabar assumptions.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT, RISK_FRAC
from finalists import make_signals, sim_equity

def resolve_15m(df4, kind, rr, atr_mult=1.5, max_hold_hours=300*4):
    f = pd.read_parquet("data/15m.parquet").sort_values("time").reset_index(drop=True)
    ft = f["time"].values; fh=f["high"].values; fl=f["low"].values; fo=f["open"].values
    L,S = make_signals(df4, kind)
    o4=df4["open"].values; t4=df4["time"].values; atrv=df4["atr14"].values
    n=len(df4); rows=[]
    idx=np.arange(n)
    sig = [(i,+1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i]>0] + \
          [(i,-1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i]>0]
    sig.sort()
    for i,s in sig:
        ei=i+1
        if ei>=n: continue
        entry=o4[ei]; rdist=atr_mult*atrv[i]
        if s>0: stop=entry-rdist; tgt=entry+rr*rdist
        else:   stop=entry+rdist; tgt=entry-rr*rdist
        sf=rdist/entry
        t_entry=t4[ei]
        start=np.searchsorted(ft, t_entry, side="left")
        end=np.searchsorted(ft, t_entry+max_hold_hours*3600, side="right")
        outcome=None; exitp=None
        for j in range(start, min(end,len(ft))):
            hj,lj,oj=fh[j],fl[j],fo[j]
            if s>0: hs=lj<=stop; ht=hj>=tgt
            else:   hs=hj>=stop; ht=lj<=tgt
            if hs and ht:
                # nearest-open at 15m granularity (minimal bias)
                if abs(oj-stop)<=abs(oj-tgt): outcome,exitp="stop",stop
                else: outcome,exitp="target",tgt
                break
            elif hs: outcome,exitp="stop",stop; break
            elif ht: outcome,exitp="target",tgt; break
        if outcome is None:
            j=min(end,len(ft))-1
            outcome,exitp="timeout", f["close"].values[j]
        gross = rr if outcome=="target" else (-1.0 if outcome=="stop" else s*(exitp-entry)/rdist)
        feeR=FEE_RT/sf
        rows.append(dict(entry_time=t_entry, exit_time=ft[min(j,len(ft)-1)], side=s,
                         outcome=outcome, gross_R=gross, fee_R=feeR, net_R=gross-feeR,
                         stop_dist_frac=sf))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def main():
    df4=ind.enrich(pd.read_parquet("data/4H.parquet"))
    for kind in ["volspike"]:
        for rr in [1.0,2.0]:
            tr=resolve_15m(df4, kind, rr)
            wins=(tr["outcome"]=="target").sum(); res=tr["outcome"].isin(["target","stop"]).sum()
            print(f"\n=== {kind} rr={rr}  15m-path-resolved  n={len(tr)} ===")
            print(f"    WR={wins/res:.1%}  expR(net)={tr['net_R'].mean():+.3f}  "
                  f"timeouts={(tr['outcome']=='timeout').sum()}")
            for mode in ["concurrent","single"]:
                _,m=sim_equity(tr.assign(entry_i=0,exit_i=0), mode=mode)
                print(f"    [{mode}] taken={m['n']} WR={m['wr']:.1%} expR={m['expR']:+.3f} "
                      f"ret={m['tot']:+.0%} CAGR={m['cagr']:+.1%} maxDD={m['maxdd']:.1%} "
                      f"mo_mean={m['mo_mean']:+.2%} mo_min={m['mo_min']:+.2%} "
                      f"mo_pos={m['mo_pos']:.0%} streak={m['max_lose_streak']}")
            # train/test split
            cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
            for lab,sub in [("TRAIN<2025",tr[tr.entry_time<cut]),("TEST>=2025",tr[tr.entry_time>=cut])]:
                w=(sub["outcome"]=="target").sum(); r=sub["outcome"].isin(["target","stop"]).sum()
                print(f"    {lab}: n={len(sub)} WR={w/r:.1%} expR={sub['net_R'].mean():+.3f}")

if __name__=="__main__":
    main()
