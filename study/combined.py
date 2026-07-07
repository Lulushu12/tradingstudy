"""Combined 'trend rejection/continuation' book on 4H:
  SHORT in a 4H downtrend when ANY of: volume-spike down bar, held resistance
        (prior-week high / prior-day high / 4H swing high) rejection, double-top, or a
        bear rejection candle (shooting star / bear engulfing).
  LONG  is the exact mirror in a 4H uptrend.
OR-combined to raise signal frequency. A bar that would fire both sides is dropped.
Entry next 4H open, stop 1.5*ATR, target rr*stop. Fees 0.08% RT. Train<2025 / Test>=2025.
Finalist re-resolved on the true 15m path.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from engine import simulate_trades, FEE_RT
from finalists import sim_equity, fmt
from confluence import prior_period_levels, active_swing_levels, double_patterns, TF_SEC

def make_combined(df, strong=True, long_mode="full"):
    up=(df["close"]>df["ema200"]); dn=~up
    up50=df["ema50"]>df["ema200"]
    UP = (up&up50) if strong else up
    DN = (dn&(~up50)) if strong else dn
    vol=df.get("vol_ratio", pd.Series(np.nan,index=df.index)); volspike=vol>1.8
    downbar=df["close"]<df["open"]; upbar=df["close"]>df["open"]
    star=df["c_shooting_star"]==1; beng=df["c_bear_engulf"]==1
    hammer=df["c_hammer"]==1; buleng=df["c_bull_engulf"]==1
    # levels (causal)
    PDH,PDL=prior_period_levels(df,"D"); PWH,PWL=prior_period_levels(df,"W")
    swh,swl=active_swing_levels(df,3,3)
    close=df["close"].values; low=df["low"].values; high=df["high"].values
    def tag_lo(l): return pd.Series((low<=l)&(close>l), index=df.index)   # support hold
    def tag_hi(l): return pd.Series((high>=l)&(close<l), index=df.index)  # resistance hold
    dt_sig,db_sig=double_patterns(df)
    dtop=pd.Series(dt_sig==1,index=df.index); dbot=pd.Series(db_sig==1,index=df.index)

    short = DN & (
        (volspike&downbar) | tag_hi(PWH) | tag_hi(PDH) | tag_hi(swh) | dtop |
        star | beng )
    if long_mode == "volspike":
        long_ = UP & (volspike&upbar)
    else:
        long_ = UP & (
            (volspike&upbar) | tag_lo(PWL) | tag_lo(PDL) | tag_lo(swl) | dbot |
            hammer | buleng )
    both = short & long_
    short = short & ~both; long_ = long_ & ~both
    return long_.values, short.values

def wr_report(df, rr, atr_mult=1.5, max_bars=300, strong=True):
    wl,ws,sf=forward_outcomes(df, atr_mult, rr, max_bars)
    d=df.copy(); d["win_L"]=wl; d["win_S"]=ws
    L,S=make_combined(df, strong=strong)
    cut=pd.Timestamp("2024-12-31",tz="UTC"); tr=(d["dt"]<cut).values; te=~tr
    p_be=breakeven_wr(rr, np.nanmean(sf))
    def stat(mask, col, m):
        w=d[col][m&mask].dropna(); return (w.mean() if len(w) else np.nan, len(w))
    print(f"  rr={rr} breakeven={p_be:.1%}")
    for lab,mask,col in [("LONG",L,"win_L"),("SHORT",S,"win_S")]:
        (wtr,ntr),(wte,nte)=stat(mask,col,tr),stat(mask,col,te)
        print(f"    {lab:5} train WR={wtr:.1%} (n={ntr})   test WR={wte:.1%} (n={nte})")
    # combined winrate
    comb_tr=pd.concat([d["win_L"][tr&L], d["win_S"][tr&S]]).dropna()
    comb_te=pd.concat([d["win_L"][te&L], d["win_S"][te&S]]).dropna()
    print(f"    BOTH  train WR={comb_tr.mean():.1%} (n={len(comb_tr)})   "
          f"test WR={comb_te.mean():.1%} (n={len(comb_te)})  "
          f"expR train={comb_tr.mean()*rr-(1-comb_tr.mean())-FEE_RT/np.nanmean(sf):+.3f}")

def build_trades(df, rr, atr_mult=1.5, max_bars=300, strong=True):
    L,S=make_combined(df, strong=strong)
    atrv=df["atr14"].values; idx=np.arange(len(df)); valid=np.isfinite(atrv)&(atrv>0)
    Li=idx[L&valid]; Si=idx[S&valid]
    entries=np.concatenate([Li,Si]); side=np.concatenate([np.ones(len(Li)),-np.ones(len(Si))])
    stop=atr_mult*atrv; stop_d=np.concatenate([stop[Li],stop[Si]]); order=np.argsort(entries)
    return simulate_trades(df, entries[order], side[order], stop_d[order], rr,
                           max_bars=max_bars, resolve="nearest_open").sort_values("entry_time").reset_index(drop=True)

def resolve_15m(df4, rr, atr_mult=1.5, max_hold_hours=300*4, strong=True, long_mode="full"):
    f=pd.read_parquet("data/15m.parquet").sort_values("time").reset_index(drop=True)
    ft=f["time"].values; fh=f["high"].values; fl=f["low"].values; fo=f["open"].values; fc=f["close"].values
    L,S=make_combined(df4, strong=strong, long_mode=long_mode)
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

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    VARIANTS=[("loose","full"),("loose","volspike")]  # loose gate; full-mirror vs selective-long
    for strong_flag,lm in VARIANTS:
        strong = (strong_flag=="strong")
        print(f"\n############ COMBINED BOOK  gate={strong_flag}  long_side={lm} ############")
        for rr in [1.0,2.0]:
            print(f"\n  --- 15m-path equity  rr={rr} ---")
            tr15=resolve_15m(df, rr, strong=strong, long_mode=lm)
            cut=pd.Timestamp("2024-12-31",tz="UTC").timestamp()
            for lab,sub in [("TRAIN",tr15[tr15.entry_time<cut]),("TEST",tr15[tr15.entry_time>=cut])]:
                w=(sub["outcome"]=="target").sum(); r=sub["outcome"].isin(["target","stop"]).sum()
                print(f"    {lab}: n={len(sub)} WR={w/r:.1%} expR={sub['net_R'].mean():+.3f}")
            for mode in ["concurrent","single"]:
                _,m=sim_equity(tr15, mode=mode)
                print(f"    {fmt(m)}")

if __name__=="__main__":
    main()
