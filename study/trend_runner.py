"""Capture BTC's trendiness: enter on a trend-continuation trigger, then instead of a
fixed 2R target, RIDE with a chandelier (ATR trailing) stop and let winners run. Cut
losers at the initial 1.5*ATR (=1R). No target, no time cap (exit only on the trail).

Win rate falls (you give back open profit on reversals) but expectancy can rise because
a few trades run many R. We measure the full R-distribution and the fat tail, and compare
against the fixed-2R baseline on the same entries. Causal: trail is set from bars up to
j-1 and checked on bar j (no intrabar look-ahead). Entry next 4H open. Train<2025/Test.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT
from finalists import make_signals, sim_equity, fmt

def run_trailing(df, L, S, k=3.0, atr_mult=1.5, use_entry_atr=False):
    """Chandelier trail. k = trail distance in ATRs. Returns per-trade DataFrame."""
    o=df["open"].values; h=df["high"].values; l=df["low"].values; c=df["close"].values
    atrv=df["atr14"].values; t=df["time"].values; n=len(df); idx=np.arange(n)
    sig=[(i,+1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i]>0]+\
        [(i,-1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i]>0]
    sig.sort(); rows=[]
    for i,s in sig:
        ei=i+1
        if ei>=n: continue
        entry=o[ei]; rdist=atr_mult*atrv[i]; sf=rdist/entry
        trail=entry-s*rdist                      # initial hard stop = 1R
        extreme=entry; exitp=None; ej=ei; running=True
        for j in range(ei,n):
            # 1) check current trail (known from bars up to j-1) against this bar
            if s>0:
                if l[j]<=trail: exitp=min(o[j],trail) if o[j]<trail else trail; ej=j; running=False; break
            else:
                if h[j]>=trail: exitp=max(o[j],trail) if o[j]>trail else trail; ej=j; running=False; break
            # 2) update extreme + ratchet trail from this bar's close info
            ka=atrv[i] if use_entry_atr else (atrv[j] if np.isfinite(atrv[j]) else atrv[i])
            if s>0:
                extreme=max(extreme,h[j]); trail=max(trail, extreme-k*ka)
            else:
                extreme=min(extreme,l[j]); trail=min(trail, extreme+k*ka)
            ej=j
        if running:                              # right-censored: mark to last close
            exitp=c[ej]; outcome="run_open"
        else:
            outcome="win" if s*(exitp-entry)>0 else "loss"
        R=s*(exitp-entry)/rdist
        rows.append(dict(entry_time=t[ei], exit_time=t[ej], side=s, outcome=outcome,
                         R=R, net_R=R-FEE_RT/sf, bars=ej-ei, stop_dist_frac=sf,
                         entry_i=0, exit_i=0))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def run_fixed(df, L, S, rr=2.0, atr_mult=1.5, max_bars=300):
    """Fixed rr-target baseline on the SAME entries (4H-bar nearest-open resolve)."""
    o=df["open"].values; h=df["high"].values; l=df["low"].values; c=df["close"].values
    atrv=df["atr14"].values; t=df["time"].values; n=len(df); idx=np.arange(n)
    sig=[(i,+1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i]>0]+\
        [(i,-1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i]>0]
    sig.sort(); rows=[]
    for i,s in sig:
        ei=i+1
        if ei>=n: continue
        entry=o[ei]; rdist=atr_mult*atrv[i]; sf=rdist/entry
        stop=entry-s*rdist; tgt=entry+s*rr*rdist; outcome=None; exitp=None; ej=ei
        for j in range(ei,min(ei+max_bars,n)):
            hs=(l[j]<=stop) if s>0 else (h[j]>=stop); ht=(h[j]>=tgt) if s>0 else (l[j]<=tgt)
            ej=j
            if hs and ht: outcome,exitp=("stop",stop) if abs(o[j]-stop)<=abs(o[j]-tgt) else ("target",tgt); break
            elif hs: outcome,exitp="stop",stop; break
            elif ht: outcome,exitp="target",tgt; break
        if outcome is None: outcome,exitp="timeout",c[ej]
        R=s*(exitp-entry)/rdist
        rows.append(dict(entry_time=t[ei], exit_time=t[ej], side=s, outcome=outcome,
                         R=R, net_R=R-FEE_RT/sf, bars=ej-ei, stop_dist_frac=sf,
                         entry_i=0, exit_i=0))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def rstats(tag, tr):
    cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
    print(f"\n--- {tag} ---")
    for lab,sub in [("TRAIN",tr[tr.entry_time<cut]),("TEST",tr[tr.entry_time>=cut])]:
        if not len(sub): continue
        R=sub["net_R"].values
        wr=(R>0).mean()
        tot=R.sum(); top=np.sort(R)[::-1]; top10=top[:max(1,len(R)//10)].sum()
        print(f"    {lab}: n={len(sub)} WR={wr:.1%} expR={R.mean():+.3f} "
              f"medR={np.median(R):+.2f} maxR={R.max():+.1f} "
              f"p90R={np.percentile(R,90):+.1f} runners(>=5R)={ (R>=5).mean():.1%} "
              f"top10%_share={top10/tot:.0%}")
    for mode in ["single","concurrent"]:
        c,m=sim_equity(tr.assign(outcome=np.where(tr["net_R"]>0,"target","stop")), mode=mode)
        print("   ",fmt(m))

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    for kind in ["volspike","trig"]:
        L,S=make_signals(df, kind)
        print(f"\n######## entries={kind}  (n_long={L.sum()} n_short={S.sum()}) ########")
        rstats(f"{kind} FIXED 2R", run_fixed(df,L,S,rr=2.0))
        for k in [2.0,3.0,4.0]:
            rstats(f"{kind} TRAIL k={k}ATR (no target)", run_trailing(df,L,S,k=k))

if __name__=="__main__":
    main()
