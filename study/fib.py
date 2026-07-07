"""Fibonacci + S/R + divergence strategies, causal.

Fib legs are built ONLY from confirmed pivots (pivot at bar p is known at p+right).
The 'active leg' at any bar = the two most recent confirmed pivots of opposite type;
its direction defines a continuation trade (up-leg -> long pullback, down-leg -> short
bounce). Retracement prices:  up-leg fib(r)=B-r*(B-A);  down-leg fib(r)=B+r*(A-B).

Golden-pocket entry: price retraces into the 0.5-0.66 zone and closes holding it,
in the leg's direction. Optional confluence: RSI divergence at the zone, and/or a
horizontal S/R level (prior day/week hi-lo, swing) sitting inside the zone.

Scan method = research.py: forward outcome per bar (entry next open, stop=1.5*ATR,
target rr*stop), then slice by condition, train<2025 vs test>=2025, vs fee breakeven.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from engine import FEE_RT
from confluence import prior_period_levels, active_swing_levels, TF_SEC

def active_leg(df, left=3, right=3, min_leg_atr=2.0):
    """Per-bar active fib leg. Returns dirn(+1 up/-1 down/0 none), A(invalidation price),
    zone_lo, zone_hi (price bounds of the 0.5-0.66 retracement pocket)."""
    ph, pl = ind.pivots(df, left, right)
    n=len(df); atrv=df["atr14"].values
    dirn=np.zeros(n); A=np.full(n,np.nan); zlo=np.full(n,np.nan); zhi=np.full(n,np.nan)
    lastH=lastL=np.nan; lastH_pi=lastL_pi=-1
    for i in range(n):
        pvi=i-right
        if np.isfinite(ph.iloc[i]): lastH=ph.iloc[i]; lastH_pi=pvi
        if np.isfinite(pl.iloc[i]): lastL=pl.iloc[i]; lastL_pi=pvi
        if np.isfinite(lastH) and np.isfinite(lastL) and lastH>lastL:
            rng=lastH-lastL
            if not np.isfinite(atrv[i]) or atrv[i]<=0 or rng < min_leg_atr*atrv[i]:
                continue
            if lastH_pi>lastL_pi:   # up leg L->H : long pullback
                B,a=lastH,lastL; dirn[i]=1
                zhi[i]=B-0.5*rng; zlo[i]=B-0.66*rng; A[i]=a
            else:                    # down leg H->L : short bounce
                B,a=lastL,lastH; rng2=a-B; dirn[i]=-1
                zlo[i]=B+0.5*rng2; zhi[i]=B+0.66*rng2; A[i]=a
    return dirn, A, zlo, zhi

def build(tf="4H"):
    df=ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    dirn,A,zlo,zhi=active_leg(df)
    df["fib_dir"]=dirn; df["fib_A"]=A; df["z_lo"]=zlo; df["z_hi"]=zhi
    # horizontal S/R levels
    PDH,PDL=prior_period_levels(df,"D"); PWH,PWL=prior_period_levels(df,"W")
    swh,swl=active_swing_levels(df,3,3)
    df["PDH"],df["PDL"],df["PWH"],df["PWL"],df["swh"],df["swl"]=PDH,PDL,PWH,PWL,swh,swl
    return df

def run(tf="4H", rr=2.0, atr_mult=1.5, max_bars=300):
    df=build(tf)
    wl,ws,sf=forward_outcomes(df, atr_mult, rr, max_bars)
    d=df.copy(); d["win_L"]=wl; d["win_S"]=ws
    cut=pd.Timestamp("2024-12-31",tz="UTC"); tr=(d["dt"]<cut).values; te=~tr
    p_be=breakeven_wr(rr, np.nanmean(sf))
    close=df["close"].values; low=df["low"].values; high=df["high"].values
    up=(df["close"]>df["ema200"]).values; dn=~up
    atr=df["atr14"].values

    # in-zone long: dipped into pocket and closed holding it (bullish)
    inzone_L = (df["fib_dir"]==1).values & (low<=df["z_hi"].values) & (close>=df["z_lo"].values) & (close>df["open"].values)
    inzone_S = (df["fib_dir"]==-1).values & (high>=df["z_lo"].values) & (close<=df["z_hi"].values) & (close<df["open"].values)
    divb=(df["div_bull"]==1).values; divs=(df["div_bear"]==1).values
    # divergence seen within the last K bars (causal rolling OR)
    K=6
    divb_recent=(df["div_bull"].rolling(K,min_periods=1).max()>0).values
    divs_recent=(df["div_bear"].rolling(K,min_periods=1).max()>0).values

    # S/R inside the fib zone (any horizontal level within the pocket)
    def level_in_zone(levels):
        m=np.zeros(len(df),bool)
        for lv in levels:
            v=df[lv].values
            m |= (v>=df["z_lo"].values)&(v<=df["z_hi"].values)
        return m
    sr_in_L = level_in_zone(["PDL","PWL","swl"]) & (df["fib_dir"]==1).values
    sr_in_S = level_in_zone(["PDH","PWH","swh"]) & (df["fib_dir"]==-1).values

    # plain S/R + divergence (no fib)
    tag_lo=lambda lv:(low<=df[lv].values)&(close>df[lv].values)
    tag_hi=lambda lv:(high>=df[lv].values)&(close<df[lv].values)
    srdiv_L=(tag_lo("swl")|tag_lo("PDL")|tag_lo("PWL"))&divb
    srdiv_S=(tag_hi("swh")|tag_hi("PDH")|tag_hi("PWH"))&divs

    conds={
      "fib pocket cont (long)":("L", inzone_L),
      "fib pocket cont (short)":("S", inzone_S),
      "fib pocket + trend (long)":("L", inzone_L&up),
      "fib pocket + trend (short)":("S", inzone_S&dn),
      "fib pocket + div<=6bars (long)":("L", inzone_L&divb_recent),
      "fib pocket + div<=6bars (short)":("S", inzone_S&divs_recent),
      "fib pocket + S/R confluence (long)":("L", sr_in_L & inzone_L),
      "fib pocket + S/R confluence (short)":("S", sr_in_S & inzone_S),
      "S/R + divergence (long)":("L", srdiv_L),
      "S/R + divergence (short)":("S", srdiv_S),
      "divergence only (long)":("L", divb),
      "divergence only (short)":("S", divs),
    }
    print(f"\n===== TF={tf} rr={rr} | breakeven WR={p_be:.1%} (stopfrac~{np.nanmean(sf):.3%}) =====")
    print(f"  {'condition':40} side  trainWR  n     testWR  n")
    rows=[]
    for name,(sidew,mask) in conds.items():
        col=d["win_L"] if sidew=="L" else d["win_S"]
        m=pd.Series(mask,index=d.index).values
        wtr=col[tr&m].dropna(); wte=col[te&m].dropna()
        okn = len(wtr)>=25 and len(wte)>=15
        ok = okn and wtr.mean()>p_be and wte.mean()>p_be
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
    for rr in [1.0,2.0]:
        run(tf=tf, rr=rr)
