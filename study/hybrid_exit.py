"""Scale-out exit that captures BTC's trend tail without the lumpiness of a pure trail:
  - Enter on a trend-continuation trigger, next 4H open. Initial stop = 1.5*ATR (=1R).
  - HALF the position exits at a fixed +2R target (the smooth, high-hit-rate win).
  - The OTHER half rides a 3-ATR chandelier trail with no target (harvests runners).
  net_R = 0.5*half1_R + 0.5*half2_R - fees.

Every signal is taken as its own trade -- NO overlap filtering (you can't take them all,
so we measure the strategy's edge across ALL possible entries). Reported both as per-trade
expectancy (edge, size-invariant) and as take-all 'concurrent' equity. Causal: trail set
from bars up to j-1, checked on bar j. Train<2025 / Test>=2025. Compared vs fixed-2R and
pure-trail on the identical entries.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT
from finalists import make_signals, sim_equity, fmt
from trend_runner import run_fixed, run_trailing

def run_hybrid(df, L, S, tp=2.0, k=3.0, atr_mult=1.5):
    o=df["open"].values; h=df["high"].values; l=df["low"].values; c=df["close"].values
    atrv=df["atr14"].values; t=df["time"].values; n=len(df); idx=np.arange(n)
    sig=[(i,+1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i]>0]+\
        [(i,-1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i]>0]
    sig.sort(); rows=[]
    for i,s in sig:
        ei=i+1
        if ei>=n: continue
        entry=o[ei]; rdist=atr_mult*atrv[i]; sf=rdist/entry
        tgt=entry+s*tp*rdist; trail=entry-s*rdist; extreme=entry
        half1=None; half2=None; ej=ei; running=True
        for j in range(ei,n):
            if s>0: stop_hit=l[j]<=trail; tgt_hit=(half1 is None) and (h[j]>=tgt)
            else:   stop_hit=h[j]>=trail; tgt_hit=(half1 is None) and (l[j]<=tgt)
            if stop_hit and tgt_hit:
                if abs(o[j]-trail)<=abs(o[j]-tgt):          # stop resolves first
                    R=s*(trail-entry)/rdist; half1=R; half2=R; ej=j; running=False; break
                else: half1=tp                              # target first, runner lives on
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
        else:
            outcome="win" if (0.5*half1+0.5*half2)>0 else "loss"
        net=0.5*half1+0.5*half2-FEE_RT/sf
        rows.append(dict(entry_time=t[ei], exit_time=t[ej], side=s, outcome=outcome,
                         R=0.5*half1+0.5*half2, net_R=net, half1_R=half1, half2_R=half2,
                         bars=ej-ei, stop_dist_frac=sf, entry_i=0, exit_i=0))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def rstats(tag, tr, show_tail=True):
    cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
    print(f"\n--- {tag} ---")
    for lab,sub in [("TRAIN",tr[tr.entry_time<cut]),("TEST",tr[tr.entry_time>=cut])]:
        if not len(sub): continue
        R=sub["net_R"].values; wr=(R>0).mean()
        extra=(f" maxR={R.max():+.1f} p90R={np.percentile(R,90):+.1f} "
               f"runners(>=5R)={(R>=5).mean():.1%}") if show_tail else ""
        print(f"    {lab}: n={len(sub)} WR={wr:.1%} expR={R.mean():+.3f} medR={np.median(R):+.2f}{extra}")
    for mode in ["concurrent","single"]:            # concurrent = take ALL entries
        _,m=sim_equity(tr.assign(outcome=np.where(tr["net_R"]>0,"target","stop")), mode=mode)
        print("   ",fmt(m))

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    for kind in ["volspike","trig"]:
        L,S=make_signals(df, kind)
        print(f"\n######## entries={kind}  ALL signals taken (n_long={L.sum()} n_short={S.sum()}) ########")
        rstats(f"{kind} FIXED 2R", run_fixed(df,L,S,rr=2.0))
        rstats(f"{kind} TRAIL 3-ATR (no target)", run_trailing(df,L,S,k=3.0))
        rstats(f"{kind} HYBRID (half@2R + half trail 3-ATR)", run_hybrid(df,L,S,tp=2.0,k=3.0))

if __name__=="__main__":
    main()
