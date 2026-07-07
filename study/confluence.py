"""Test the three things not covered before:
  A) Richer lowTF+highTF confluence (HTF trend + HTF momentum + not-overextended + LTF trigger)
  B) HTF significant LEVELS (prior day/week high-low, HTF confirmed swings) + LTF entry trigger
  C) Multi-candle chart patterns (double top/bottom, head & shoulders) - causal, from confirmed pivots

Method mirrors research.py: precompute per-bar forward outcome (entry next-bar open,
stop = atr_mult*ATR, target = rr*stop, walk max_bars) once per (TF,rr), then slice by
each condition's boolean mask and compare train vs test winrate against fee breakeven.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from engine import FEE_RT

TF_SEC = {"1D":86400,"4H":14400,"1h":3600,"15m":900,"5m":300,"1m":60}

def merge_htf(df, htf_df, htf_tf, cols):
    dur=TF_SEC[htf_tf]; h=htf_df[["time"]+cols].copy(); h["ct"]=h["time"]+dur
    h=h.sort_values("ct"); left=df[["time"]].copy().sort_values("time")
    m=pd.merge_asof(left, h.drop(columns="time"), left_on="time", right_on="ct", direction="backward")
    m=m.set_index(left.index).sort_index()
    for c in cols: df[htf_tf+"_"+c]=m[c].values
    return df

# ---------- causal HTF swing levels (forward-filled active levels) ----------
def active_swing_levels(df, left=3, right=3, keep=3):
    """Return arrays of the last `keep` confirmed pivot-high and pivot-low prices,
    active from their confirmation bar. Fully causal."""
    ph, pl = ind.pivots(df, left, right)
    n=len(df)
    res_hi=np.full(n, np.nan); res_lo=np.full(n, np.nan)
    hi_hist=[]; lo_hist=[]
    for i in range(n):
        if np.isfinite(ph.iloc[i]): hi_hist.append(ph.iloc[i])
        if np.isfinite(pl.iloc[i]): lo_hist.append(pl.iloc[i])
        # nearest active resistance above / support below current close handled at use-site;
        # here just store most-recent pivot levels
        if hi_hist: res_hi[i]=hi_hist[-1]
        if lo_hist: res_lo[i]=lo_hist[-1]
    return res_hi, res_lo

def prior_period_levels(df, freq="D"):
    """Prior completed day/week high & low, causal (shifted)."""
    p=df.set_index("dt")
    hi=p["high"].resample(freq).max(); lo=p["low"].resample(freq).min()
    # map each bar to PREVIOUS period's hi/lo
    per=df["dt"].dt.to_period("W" if freq=="W" else "D")
    hi_prev=hi.shift(1); lo_prev=lo.shift(1)
    hi_map=hi_prev.copy(); lo_map=lo_prev.copy()
    # build lookup by period
    hi_by=hi_prev; lo_by=lo_prev
    idx_per = per.astype(str).values
    hi_idx = {str(k.to_period("W" if freq=="W" else "D")): v for k,v in zip(hi_prev.index, hi_prev.values)}
    lo_idx = {str(k.to_period("W" if freq=="W" else "D")): v for k,v in zip(lo_prev.index, lo_prev.values)}
    H=np.array([hi_idx.get(k, np.nan) for k in idx_per])
    L=np.array([lo_idx.get(k, np.nan) for k in idx_per])
    return H, L

# ---------- multi-candle chart patterns (causal, signal at completion bar) ----------
def double_patterns(df, left=3, right=3, tol=0.01, span=60):
    """Double top -> short signal at bar where close breaks the intervening trough.
    Double bottom -> long. Signal placed at breakout bar (causal)."""
    ph, pl = ind.pivots(df, left, right)
    n=len(df); dt_sig=np.zeros(n); db_sig=np.zeros(n)
    close=df["close"].values
    hi_idx=[i for i in range(n) if np.isfinite(ph.iloc[i])]
    lo_idx=[i for i in range(n) if np.isfinite(pl.iloc[i])]
    hi_val={i:ph.iloc[i] for i in hi_idx}; lo_val={i:pl.iloc[i] for i in lo_idx}
    # double top: two highs similar, with a low between; neckline = that low
    for a,b in zip(hi_idx[:-1], hi_idx[1:]):
        if b-a>span: continue
        if abs(hi_val[a]-hi_val[b])/hi_val[a] > tol: continue
        mids=[i for i in lo_idx if a< i< b]
        if not mids: continue
        neck=min(lo_val[i] for i in mids)
        # find first bar after b (its confirm at b) where close<neck
        for j in range(b+1, min(b+span, n)):
            if close[j] < neck:
                dt_sig[j]=1; break
    for a,b in zip(lo_idx[:-1], lo_idx[1:]):
        if b-a>span: continue
        if abs(lo_val[a]-lo_val[b])/lo_val[a] > tol: continue
        mids=[i for i in hi_idx if a< i< b]
        if not mids: continue
        neck=max(hi_val[i] for i in mids)
        for j in range(b+1, min(b+span, n)):
            if close[j] > neck:
                db_sig[j]=1; break
    return dt_sig, db_sig

def hs_patterns(df, left=3, right=3, tol=0.03, span=90):
    """Head&Shoulders -> short at neckline break; inverse H&S -> long. Causal."""
    ph, pl = ind.pivots(df, left, right)
    n=len(df); hs=np.zeros(n); ihs=np.zeros(n); close=df["close"].values
    hi_idx=[i for i in range(n) if np.isfinite(ph.iloc[i])]
    lo_idx=[i for i in range(n) if np.isfinite(pl.iloc[i])]
    hv={i:ph.iloc[i] for i in hi_idx}; lv={i:pl.iloc[i] for i in lo_idx}
    # H&S: highs L-S, Head, R-S with head highest, shoulders similar; troughs between = neckline
    for x in range(len(hi_idx)-2):
        a,b,c=hi_idx[x],hi_idx[x+1],hi_idx[x+2]
        if c-a>span: continue
        if not (hv[b]>hv[a] and hv[b]>hv[c]): continue
        if abs(hv[a]-hv[c])/hv[a] > tol: continue
        troughs=[i for i in lo_idx if a<i<c]
        if len(troughs)<1: continue
        neck=np.mean([lv[i] for i in troughs])
        for j in range(c+1, min(c+span, n)):
            if close[j] < neck: hs[j]=1; break
    for x in range(len(lo_idx)-2):
        a,b,c=lo_idx[x],lo_idx[x+1],lo_idx[x+2]
        if c-a>span: continue
        if not (lv[b]<lv[a] and lv[b]<lv[c]): continue
        if abs(lv[a]-lv[c])/lv[a] > tol: continue
        peaks=[i for i in hi_idx if a<i<c]
        if len(peaks)<1: continue
        neck=np.mean([hv[i] for i in peaks])
        for j in range(c+1, min(c+span, n)):
            if close[j] > neck: ihs[j]=1; break
    return hs, ihs

def slice_report(df, tr, te, sf, rr, conds):
    p_be=breakeven_wr(rr, np.nanmean(sf))
    print(f"  net breakeven WR @rr={rr}: {p_be:.1%}   (stopfrac~{np.nanmean(sf):.3%})")
    print(f"  {'condition':40} side trainWR  n     testWR  n")
    rows=[]
    for name,(sidew,mask) in conds.items():
        col=df["win_L"] if sidew=="L" else df["win_S"]
        wtr=col[tr&mask].dropna(); wte=col[te&mask].dropna()
        if len(wtr)<30 or len(wte)<20:
            rows.append((name,sidew,wtr.mean() if len(wtr) else np.nan,len(wtr),
                         wte.mean() if len(wte) else np.nan,len(wte),False)); continue
        ok=(wtr.mean()>p_be and wte.mean()>p_be)
        rows.append((name,sidew,wtr.mean(),len(wtr),wte.mean(),len(wte),ok))
    rows.sort(key=lambda r: -(min(r[2],r[4]) if np.isfinite(r[2]) and np.isfinite(r[4]) else -1))
    for name,sidew,trw,ntr,tew,nte,ok in rows:
        flag="  <<<" if ok else ""
        tw=f"{trw:.1%}" if np.isfinite(trw) else "  -"
        ew=f"{tew:.1%}" if np.isfinite(tew) else "  -"
        print(f"  {name:40} {sidew:3} {tw:>6} {ntr:5d}  {ew:>6} {nte:5d}{flag}")

def run(tf="1h", htf="4H", rr=2.0, atr_mult=1.5, max_bars=300):
    df=ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    htf_df=ind.enrich(pd.read_parquet(f"data/{htf}.parquet"))
    df=merge_htf(df, htf_df, htf, ["close","ema200","ema50","rsi14","atr14"])
    d1=ind.enrich(pd.read_parquet("data/1D.parquet"))
    df=merge_htf(df, d1, "1D", ["close","ema200","rsi14"])
    wl,ws,sf=forward_outcomes(df, atr_mult, rr, max_bars)
    df=df.copy(); df["win_L"]=wl; df["win_S"]=ws; df["sf"]=sf
    cut=pd.Timestamp("2024-12-31",tz="UTC"); tr=(df["dt"]<cut); te=~tr

    # ---- A: richer confluence ----
    up4=df[htf+"_close"]>df[htf+"_ema200"]; up1d=df["1D_close"]>df["1D_ema200"]
    dn4=~up4; dn1d=~up1d
    r4=df[htf+"_rsi14"]
    ltf_bull=(df["c_bull_engulf"]==1)|(df["c_hammer"]==1)
    ltf_bear=(df["c_bear_engulf"]==1)|(df["c_shooting_star"]==1)
    ltf_sweep_up=(df["low"]<df["low"].shift(1).rolling(10).min())&(df["close"]>df["low"].shift(1).rolling(10).min())
    ltf_sweep_dn=(df["high"]>df["high"].shift(1).rolling(10).max())&(df["close"]<df["high"].shift(1).rolling(10).max())
    A={
      "4Hup+1Dup+ltf_bull":("L", up4&up1d&ltf_bull),
      "4Hdn+1Ddn+ltf_bear":("S", dn4&dn1d&ltf_bear),
      "4Hup+1Dup+r4<45+ltf_bull":("L", up4&up1d&(r4<45)&ltf_bull),
      "4Hdn+1Ddn+r4>55+ltf_bear":("S", dn4&dn1d&(r4>55)&ltf_bear),
      "4Hup+1Dup+sweep_up":("L", up4&up1d&ltf_sweep_up),
      "4Hdn+1Ddn+sweep_dn":("S", dn4&dn1d&ltf_sweep_dn),
    }
    print(f"\n########## A) lowTF({tf})+highTF({htf}/1D) confluence ##########")
    slice_report(df, tr, te, sf, rr, A)

    # ---- B: HTF levels + LTF entry ----
    PDH,PDL=prior_period_levels(df,"D"); PWH,PWL=prior_period_levels(df,"W")
    atr=df["atr14"].values; close=df["close"].values; low=df["low"].values; high=df["high"].values
    near=lambda lvl: np.abs(close-lvl)<=0.5*atr
    tag_lo=lambda lvl: (low<=lvl)&(close>lvl)          # tapped level from above, closed back up (support hold)
    tag_hi=lambda lvl: (high>=lvl)&(close<lvl)          # tapped level from below, closed back down (resist hold)
    swh,swl=active_swing_levels(htf_df,3,3)
    # merge htf swing levels onto ltf causally (approx: use htf close-time)
    htf_lv=pd.DataFrame({"time":htf_df["time"].values+TF_SEC[htf],"swh":swh,"swl":swl}).sort_values("time")
    ml=pd.merge_asof(df[["time"]].sort_values("time"), htf_lv, on="time", direction="backward").set_index(df.index)
    SWH=ml["swh"].values; SWL=ml["swl"].values
    B={
      "PDL support hold -> long":("L", pd.Series(tag_lo(PDL),index=df.index)),
      "PDH resist hold -> short":("S", pd.Series(tag_hi(PDH),index=df.index)),
      "PWL support hold -> long":("L", pd.Series(tag_lo(PWL),index=df.index)),
      "PWH resist hold -> short":("S", pd.Series(tag_hi(PWH),index=df.index)),
      "4Hswing sup hold -> long":("L", pd.Series(tag_lo(SWL),index=df.index)),
      "4Hswing res hold -> short":("S", pd.Series(tag_hi(SWH),index=df.index)),
      "PDL hold + 1Dup -> long":("L", pd.Series(tag_lo(PDL),index=df.index)&up1d),
      "PDH hold + 1Ddn -> short":("S", pd.Series(tag_hi(PDH),index=df.index)&dn1d),
      "4Hswing sup hold+4Hup":("L", pd.Series(tag_lo(SWL),index=df.index)&up4),
      "4Hswing res hold+4Hdn":("S", pd.Series(tag_hi(SWH),index=df.index)&dn4),
    }
    print(f"\n########## B) HTF levels + {tf} entry ##########")
    slice_report(df, tr, te, sf, rr, B)

    # ---- C: multi-candle chart patterns ----
    dt_sig,db_sig=double_patterns(df); hs,ihs=hs_patterns(df)
    C={
      "double_top -> short":("S", pd.Series(dt_sig==1,index=df.index)),
      "double_bottom -> long":("L", pd.Series(db_sig==1,index=df.index)),
      "H&S -> short":("S", pd.Series(hs==1,index=df.index)),
      "inverse_H&S -> long":("L", pd.Series(ihs==1,index=df.index)),
      "double_bottom+1Dup":("L", pd.Series(db_sig==1,index=df.index)&up1d),
      "double_top+1Ddn":("S", pd.Series(dt_sig==1,index=df.index)&dn1d),
    }
    print(f"\n########## C) multi-candle chart patterns on {tf} ##########")
    slice_report(df, tr, te, sf, rr, C)

if __name__=="__main__":
    import sys
    tf=sys.argv[1] if len(sys.argv)>1 else "1h"
    rr=float(sys.argv[2]) if len(sys.argv)>2 else 2.0
    htf=sys.argv[3] if len(sys.argv)>3 else "4H"
    run(tf=tf, rr=rr, htf=htf)
