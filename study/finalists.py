"""Full backtest of finalist 4H trend-continuation strategies.

Sizing variants:
  - concurrent: every signal risks 1% (many trades open at once) -> higher DD.
  - single:     at most ONE position open; skip signals while in a trade -> DD controllable.
Because each trade risks 1%, single-position floating DD adds <=~1% over realized DD,
so realized-equity DD is a good proxy for true DD (must stay < ~5% to respect 6% cap).
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from engine import simulate_trades, FEE_RT, RISK_FRAC

def make_signals(df, kind):
    up=(df["close"]>df["ema200"]); dn=~up
    up50=df["ema50"]>df["ema200"]
    strong_up=up&up50; strong_dn=dn&(~up50)
    star=df["c_shooting_star"]==1; hammer=df["c_hammer"]==1
    beng=df["c_bear_engulf"]==1; buleng=df["c_bull_engulf"]==1
    vol=df.get("vol_ratio", pd.Series(np.nan,index=df.index)); volspike=vol>1.8
    macd_up=(df["macd"]>0)&(df["macd_hist"]>df["macd_hist"].shift(1))
    macd_dn=(df["macd"]<0)&(df["macd_hist"]<df["macd_hist"].shift(1))
    downbar=df["close"]<df["open"]; upbar=df["close"]>df["open"]
    bear_trig=star|beng|(volspike&downbar)
    bull_trig=hammer|buleng|(volspike&upbar)
    if kind=="volspike":
        L=(up&volspike&upbar); S=(dn&volspike&downbar)
    elif kind=="trig":
        L=(strong_up&bull_trig); S=(strong_dn&bear_trig)
    elif kind=="macd_trig":
        L=(strong_up&macd_up&bull_trig); S=(strong_dn&macd_dn&bear_trig)
    elif kind=="trend":
        L=strong_up; S=strong_dn
    else:
        raise ValueError(kind)
    return L.values, S.values

def build_trades(df, kind, rr, atr_mult=1.5, max_bars=300):
    L,S = make_signals(df, kind)
    atrv=df["atr14"].values; idx=np.arange(len(df))
    valid=np.isfinite(atrv)&(atrv>0)
    Li=idx[L&valid]; Si=idx[S&valid]
    entries=np.concatenate([Li,Si]); side=np.concatenate([np.ones(len(Li)),-np.ones(len(Si))])
    stop=atr_mult*atrv
    stop_d=np.concatenate([stop[Li],stop[Si]])
    order=np.argsort(entries)
    tr=simulate_trades(df, entries[order], side[order], stop_d[order], rr,
                       max_bars=max_bars, resolve="nearest_open")
    return tr.sort_values("entry_time").reset_index(drop=True)

def sim_equity(tr, mode="single", risk=RISK_FRAC, start=10000.0):
    """Return equity curve (per closed trade) + metrics. 'single' skips overlapping."""
    if len(tr)==0: return None,{}
    tr=tr.sort_values("entry_time").reset_index(drop=True)
    equity=start; peak=start; maxdd=0.0
    busy_until=-1
    curve=[]; used=[]
    for _,r in tr.iterrows():
        if mode=="single" and r["entry_time"]<busy_until:
            continue
        pnl=risk*equity*r["net_R"]
        equity+=pnl
        busy_until=r["exit_time"]
        peak=max(peak,equity); maxdd=min(maxdd,(equity-peak)/peak)
        curve.append((r["exit_time"], equity, r["net_R"], r["outcome"]))
        used.append(r)
    c=pd.DataFrame(curve, columns=["time","equity","net_R","outcome"])
    c["dt"]=pd.to_datetime(c["time"],unit="s",utc=True)
    u=pd.DataFrame(used)
    # monthly on realized equity (last equity each month)
    cm=c.set_index("dt")["equity"]
    monthly=cm.resample("ME").last().reindex(
        pd.date_range(cm.index.min().normalize(), cm.index.max(), freq="ME", tz="UTC"))
    monthly=monthly.ffill().pct_change(fill_method=None).dropna()
    # max losing streak
    outs=(u["outcome"]=="target").values if len(u) else np.array([])
    streak=mx=0
    for wgt in outs:
        if wgt: streak=0
        else: streak+=1; mx=max(mx,streak)
    wins=(u["outcome"]=="target").sum(); resolved=u["outcome"].isin(["target","stop"]).sum()
    yrs=(c["time"].iloc[-1]-c["time"].iloc[0])/ (365.25*86400)
    cagr=(equity/start)**(1/yrs)-1 if yrs>0 else np.nan
    m=dict(mode=mode, n=len(u), taken=len(u), wr=wins/resolved if resolved else np.nan,
           expR=u["net_R"].mean(), tot=equity/start-1, cagr=cagr, maxdd=maxdd,
           per_month=len(u)/(yrs*12), mo_mean=monthly.mean(), mo_med=monthly.median(),
           mo_min=monthly.min(), mo_pos=(monthly>0).mean(), max_lose_streak=mx,
           years=yrs)
    return c,m

def fmt(m):
    if not m: return "none"
    return (f"[{m['mode']}] n={m['n']} taken={m['taken']} WR={m['wr']:.1%} "
            f"expR={m['expR']:+.3f} | ret={m['tot']:+.0%} CAGR={m['cagr']:+.1%} "
            f"maxDD={m['maxdd']:.1%} | {m['per_month']:.1f} trades/mo "
            f"mo_mean={m['mo_mean']:+.2%} mo_med={m['mo_med']:+.2%} "
            f"mo_min={m['mo_min']:+.2%} mo_pos={m['mo_pos']:.0%} maxLoseStreak={m['max_lose_streak']}")

def main():
    df=ind.enrich(pd.read_parquet("data/4H.parquet"))
    for kind in ["volspike","trig","macd_trig","trend"]:
        for rr in [1.0,2.0]:
            tr=build_trades(df, kind, rr)
            print(f"\n=== kind={kind} rr={rr}  (full period {df['dt'].iloc[0].date()}..{df['dt'].iloc[-1].date()}) ===")
            for mode in ["concurrent","single"]:
                _,m=sim_equity(tr, mode=mode)
                print("   ",fmt(m))

if __name__=="__main__":
    main()
