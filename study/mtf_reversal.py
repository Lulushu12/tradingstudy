"""HTF value-area extreme + LTF reversal trigger -> ride back to POC.

Idea: on the HIGHER timeframe (4H) price is stretched to an edge of the rolling volume
profile (close >= VAH for shorts, <= VAL for longs). On the LOWER timeframe (1h) we wait
for a confirmed reversal signal (bearish/bullish RSI divergence, or a momentum roll-over),
then enter and ride toward the HTF POC (the volume magnet / middle of value).

Stop = m*ATR(4H) beyond entry (a HTF-level invalidation, so fee drag stays low). Target =
current HTF POC. 1R = stop distance, so a win = (entry-POC)/stop_dist R (variable, often
several R because POC is far). Causal: HTF levels come from the last CLOSED 4H bar
(merge_asof on close-time); LTF divergence uses confirmed pivots. Train<2025 / Test>=2025.

Crucially we split by HTF regime: 'at VAH in a 4H DOWNtrend' is really the known
rally-into-resistance rejection-short; 'at VAH in a 4H UPtrend' is the true counter-trend
fade the idea proposes. They behave very differently.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import FEE_RT
from vpvr import build_profile

def load_mtf(htf="4H", ltf="1h", W=300):
    d4=ind.enrich(pd.read_parquet(f"data/{htf}.parquet"))
    poc,vah,val=build_profile(d4, W=W)
    d4["poc"],d4["vah"],d4["val"]=poc,vah,val
    d1=ind.enrich(pd.read_parquet(f"data/{ltf}.parquet"))
    # causal map: last CLOSED htf bar for each ltf bar
    ct4=(d4["time"]+ {"4H":14400,"1D":86400,"1h":3600}[htf]).values
    j=np.searchsorted(ct4, d1["time"].values, side="right")-1
    ok=j>=0
    for col in ["poc","vah","val","close","ema200"]:
        arr=np.full(len(d1),np.nan); arr[ok]=d4[col].values[j[ok]]; d1["h_"+col]=arr
    return d1

def resolve(d1, entL, entS, m_stop=1.5, max_bars=400):
    o=d1["open"].values; h=d1["high"].values; l=d1["low"].values; c=d1["close"].values
    atr1=d1["atr14"].values                # HTF-scale stop = m_stop*atr1*2 (1h->4H ~x2)
    poc=d1["h_poc"].values; t=d1["time"].values; n=len(d1); idx=np.arange(n)
    sig=[(i,+1) for i in idx if entL[i]]+[(i,-1) for i in idx if entS[i]]
    sig.sort(); rows=[]
    for i,s in sig:
        ei=i+1
        if ei>=n or not np.isfinite(atr1[i]) or atr1[i]<=0 or not np.isfinite(poc[i]): continue
        entry=o[ei]; rdist=m_stop*atr1[i]*2.0        # ~HTF-scale stop
        tgt=poc[i]
        if s>0 and not (tgt>entry): continue          # need room UP to POC
        if s<0 and not (tgt<entry): continue          # need room DOWN to POC
        stop=entry-s*rdist; sf=rdist/entry
        outcome=None; exitp=None; ej=ei; mfe=0.0
        for j in range(ei,min(ei+max_bars,n)):
            ej=j
            mfe=max(mfe, (h[j]-entry) if s>0 else (entry-l[j]))
            hs=(l[j]<=stop) if s>0 else (h[j]>=stop)
            ht=(h[j]>=tgt) if s>0 else (l[j]<=tgt)
            if hs and ht: outcome,exitp=("stop",stop) if abs(o[j]-stop)<=abs(o[j]-tgt) else ("target",tgt); break
            elif hs: outcome,exitp="stop",stop; break
            elif ht: outcome,exitp="target",tgt; break
        if outcome is None: outcome,exitp="timeout",c[ej]
        R=s*(exitp-entry)/rdist
        rows.append(dict(entry_time=t[ei], side=s, outcome=outcome, R=R, net_R=R-FEE_RT/sf,
                         win_target=(tgt-entry)/(s*rdist), mfe_R=mfe/rdist, bars=ej-ei,
                         stop_dist_frac=sf))
    return pd.DataFrame(rows)

def rep(tag, tr):
    cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
    print(f"\n--- {tag} ---")
    if not len(tr): print("    (no trades)"); return
    for lab,sub in [("TRAIN",tr[tr.entry_time<cut]),("TEST",tr[tr.entry_time>=cut])]:
        if not len(sub): print(f"    {lab}: (none)"); continue
        R=sub["net_R"].values; reachPOC=(sub["outcome"]=="target").mean()
        print(f"    {lab}: n={len(sub)} reachPOC={reachPOC:.1%} expR={R.mean():+.3f} "
              f"medR={np.median(R):+.2f} avgWinTgt={sub['win_target'].mean():.1f}R "
              f"medMFE={sub['mfe_R'].median():.1f}R")

def main():
    d1=load_mtf("4H","1h",W=300)
    dn4=d1["h_close"].values<d1["h_ema200"].values; up4=~dn4
    atVAH=d1["close"].values>=d1["h_vah"].values
    atVAL=d1["close"].values<=d1["h_val"].values
    divb=(d1["div_bull"].values==1); divs=(d1["div_bear"].values==1)
    K=8
    divb_r=(d1["div_bull"].rolling(K,min_periods=1).max().values>0)
    divs_r=(d1["div_bear"].rolling(K,min_periods=1).max().values>0)
    # LTF momentum roll-over (confirmed short-term downtrend on 1h)
    roll_dn=(d1["ema50"].values<d1["ema200"].values)&(d1["close"].values<d1["ema50"].values)
    roll_up=(d1["ema50"].values>d1["ema200"].values)&(d1["close"].values>d1["ema50"].values)

    tests={
      "SHORT @VAH + 1h bear-div (any 4H trend)": (np.zeros(len(d1),bool), atVAH&divs_r),
      "SHORT @VAH + bear-div + 4H UPtrend (true fade)": (np.zeros(len(d1),bool), atVAH&divs_r&up4),
      "SHORT @VAH + bear-div + 4H DOWNtrend (rejection)": (np.zeros(len(d1),bool), atVAH&divs_r&dn4),
      "SHORT @VAH + 1h roll-over (downtrend)": (np.zeros(len(d1),bool), atVAH&roll_dn),
      "LONG  @VAL + 1h bull-div (any 4H trend)": (atVAL&divb_r, np.zeros(len(d1),bool)),
      "LONG  @VAL + bull-div + 4H DOWNtrend (true fade)": (atVAL&divb_r&dn4, np.zeros(len(d1),bool)),
      "LONG  @VAL + bull-div + 4H UPtrend (support)": (atVAL&divb_r&up4, np.zeros(len(d1),bool)),
      "LONG  @VAL + 1h roll-up (uptrend)": (atVAL&roll_up, np.zeros(len(d1),bool)),
    }
    print("HTF=4H value area (W=300) | LTF=1h trigger | target=HTF POC | stop~HTF-scale ATR")
    for name,(eL,eS) in tests.items():
        tr=resolve(d1, eL, eS, m_stop=1.5, max_bars=400)
        rep(name, tr)

if __name__=="__main__":
    main()
