"""Stage E: try to kill the short-alt book.

Three attacks:
  E1 gap/squeeze risk -- my sim assumed every stop fills AT the stop price. On alt perps a
     squeeze runs through it. Re-resolve stopped shorts at a realistic adverse fill.
  E2 monthly block bootstrap -- honest significance under correlated, clustered trades.
  E3 cost cliff -- at what slippage does it die?
"""
import numpy as np, pandas as pd
from b_transfer import prep, EMA_N, RR, ATR_MULT, VOL_MULT, MAXBARS

FEE = 0.0010

def signals_gap(d, slip, liq_min=5e7, stop_fill="close"):
    """stop_fill: 'stop' = optimistic (fills at stop), 'close' = fills at the close of the
       bar that broke the stop (models running through a thin book / squeeze)."""
    d = d.reset_index(drop=True); n = len(d)
    if n < EMA_N + 60: return []
    o=d["open"].to_numpy(float); h=d["high"].to_numpy(float); l=d["low"].to_numpy(float)
    c,_,_,atr,ema,vma = prep(d)
    dts=d["dt"].to_numpy(); v=d["volume"].to_numpy(float)
    liq=(pd.Series(d["quote_volume"].to_numpy(float)).rolling(180).median()*6).shift(1).to_numpy()
    up=c>ema; spike=v>VOL_MULT*vma
    sig_l=up&spike&(c>o); sig_s=(~up)&spike&(c<o)
    out=[]; busy=-1
    for i in range(EMA_N, n-1):
        if i<=busy or not(sig_l[i] or sig_s[i]): continue
        if not np.isfinite(atr[i]) or atr[i]<=0: continue
        if not np.isfinite(liq[i]) or liq[i]<liq_min: continue
        s = 1 if sig_l[i] else -1
        ei=i+1; entry=o[ei]*(1+s*slip); rdist=ATR_MULT*atr[i]; sdf=rdist/entry
        if sdf<0.002: continue
        stop=entry-s*rdist; tgt=entry+s*RR*rdist
        res=None; end=min(ei+MAXBARS,n)
        for j in range(ei,end):
            hs=(l[j]<=stop) if s>0 else (h[j]>=stop)
            ht=(h[j]>=tgt) if s>0 else (l[j]<=tgt)
            if hs:
                if stop_fill=="stop": fill=stop
                else:  # fill at the worse of stop and that bar's close (squeeze-through)
                    fill = min(stop,c[j]) if s>0 else max(stop,c[j])
                res=s*(fill-entry)/rdist; xi=j; break
            if ht: res, xi = RR, j; break
        if res is None: xi=end-1; res=s*(c[xi]-entry)/rdist
        busy=xi
        out.append(dict(entry_dt=dts[ei],exit_dt=dts[xi],side=s,gross_R=res,sdf=sdf,
                        fee_R=(FEE+2*slip)/sdf))
    return out

def block_bootstrap(t, n_boot=4000, seed=7):
    """Resample whole calendar months with replacement -> honest CI under clustering."""
    rng = np.random.default_rng(seed)
    t = t.copy(); t["m"] = t.exit_dt.dt.to_period("M")
    groups = [g.netR.to_numpy() for _, g in t.groupby("m")]
    k = len(groups)
    means = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, k, k)
        means[b] = np.concatenate([groups[i] for i in pick]).mean()
    return means, k

if __name__ == "__main__":
    p = pd.read_parquet("panel_4h.parquet")
    fund = pd.read_parquet("funding.parquet")
    syms = [s for s in p.symbol.unique() if s != "BTCUSDT"]
    fmap = {s: g.set_index("dt")["rate"] for s, g in fund.groupby("symbol")}

    def build(slip, stop_fill):
        rows=[]
        for s in syms:
            for t in signals_gap(p[p.symbol==s], slip, stop_fill=stop_fill):
                t["symbol"]=s; rows.append(t)
        t=pd.DataFrame(rows)
        t["entry_dt"]=pd.to_datetime(t.entry_dt,utc=True); t["exit_dt"]=pd.to_datetime(t.exit_dt,utc=True)
        fr=[]
        for _,r in t.iterrows():
            ser=fmap.get(r.symbol)
            if ser is None: fr.append(0.0); continue
            seg=ser.loc[(ser.index>r.entry_dt)&(ser.index<=r.exit_dt)]
            fr.append(seg.sum()*r.side/r.sdf)
        t["funding_R"]=fr; t["netR"]=t.gross_R-t.fee_R-t.funding_R
        return t

    print("="*100)
    print("E1. GAP / SQUEEZE RISK ON STOPS  (short book only, 5bp entry slip)")
    print("="*100)
    opt = build(0.0005, "stop"); pes = build(0.0005, "close")
    for lab, t in [("stops fill AT the stop (optimistic)", opt),
                   ("stops fill at bar close (squeeze-through)", pes)]:
        s = t[t.side==-1]
        worst = s.gross_R.min()
        print(f"{lab:<45} n={len(s)}  E={s.netR.mean():+.3f}R  "
              f"worst single trade {worst:+.2f}R  "
              f"trades losing >1.5R: {(s.gross_R < -1.5).mean():.2%}")
    s_p = pes[pes.side==-1]
    print(f"\n  tail of the pessimistic short book: "
          + "  ".join(f"p{q}={np.percentile(s_p.netR,q):+.2f}R" for q in [0.1,1,5,50,95,99]))
    print(f"  worst 10 trades sum to {np.sort(s_p.netR.values)[:10].sum():+.1f}R "
          f"out of total {s_p.netR.sum():+.0f}R")

    print("\n" + "="*100)
    print("E2. MONTHLY BLOCK BOOTSTRAP (pessimistic stop fills) -- is the edge real?")
    print("="*100)
    for lab, sub in [("SHORT book", s_p), ("LONG book", pes[pes.side==1])]:
        means, k = block_bootstrap(sub)
        lo, hi = np.percentile(means, [2.5, 97.5])
        print(f"{lab:<12} E={sub.netR.mean():+.3f}R  95% CI [{lo:+.3f}, {hi:+.3f}]  "
              f"P(E<=0)={np.mean(means<=0):.3f}   ({k} monthly blocks)")

    print("\n" + "="*100)
    print("E3. COST CLIFF -- where does the short book die? (pessimistic stop fills)")
    print("="*100)
    for slip in [0.0005, 0.0010, 0.0015, 0.0020, 0.0030, 0.0050]:
        t = build(slip, "close"); s = t[t.side==-1]
        tr_ = s[s.exit_dt<'2025-01-01']; te_ = s[s.exit_dt>='2025-01-01']
        print(f"  slippage {slip*1e4:4.0f}bp/side  E={s.netR.mean():+.3f}R  "
              f"train {tr_.netR.mean():+.3f} / test {te_.netR.mean():+.3f}  n={len(s)}")
    pes.to_parquet("trades_pessimistic.parquet")
