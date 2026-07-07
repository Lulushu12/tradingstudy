"""Deep-dive on 4H trend-continuation leads with per-year WR stability."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import indicators as ind
from research import forward_outcomes, breakeven_wr
from engine import FEE_RT

def build(tf="4H", atr_mult=1.5):
    df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    return df

def outcomes(df, rr, atr_mult=1.5, max_bars=300):
    wl, ws, sf = forward_outcomes(df, atr_mult, rr, max_bars)
    df = df.copy(); df["win_L"]=wl; df["win_S"]=ws; df["sf"]=sf
    df["year"]=df["dt"].dt.year
    return df

def report(df, name, sidew, mask, rr):
    col = df["win_L"] if sidew=="L" else df["win_S"]
    sub = df[mask]
    w = col[mask].dropna()
    if len(w)==0:
        print(f"  {name}: no data"); return
    sf = df["sf"][mask].dropna().mean()
    feeR = FEE_RT/sf
    p_be = (1+feeR)/(1+rr)
    # expectancy net R
    wr = w.mean()
    expR = wr*rr - (1-wr)*1 - feeR
    # per year
    yr = sub.groupby("year").apply(lambda g: (col.loc[g.index].dropna().mean(),
                                              col.loc[g.index].notna().sum()))
    ys = "  ".join(f"{y}:{v[0]:.0%}({v[1]})" for y,v in yr.items() if v[1]>=10)
    print(f"  {name:34} {sidew} rr={rr} WR={wr:.1%} n={len(w)} expR={expR:+.3f} "
          f"be={p_be:.1%} feeR={feeR:.3f}")
    print(f"       by year: {ys}")

def main():
    df = build()
    up=(df["close"]>df["ema200"]); dn=~up
    up50=df["ema50"]>df["ema200"]; dn50=~up50
    strong_up = up&up50; strong_dn = dn&dn50
    star=df["c_shooting_star"]==1; hammer=df["c_hammer"]==1
    beng=df["c_bear_engulf"]==1; buleng=df["c_bull_engulf"]==1
    vol = df.get("vol_ratio", pd.Series(np.nan,index=df.index))
    volspike = vol>1.8
    macd_up=(df["macd"]>0)&(df["macd_hist"]>df["macd_hist"].shift(1))
    macd_dn=(df["macd"]<0)&(df["macd_hist"]<df["macd_hist"].shift(1))
    downbar=df["close"]<df["open"]; upbar=df["close"]>df["open"]

    # trigger = any bearish rejection/momentum candle
    bear_trig = star | beng | (volspike&downbar)
    bull_trig = hammer | buleng | (volspike&upbar)

    for rr in (1.0, 2.0):
        dfo = outcomes(df, rr)
        print(f"\n===== 4H rr={rr} =====")
        report(dfo, "strong_dn only", "S", strong_dn.values, rr)
        report(dfo, "strong_up only", "L", strong_up.values, rr)
        report(dfo, "strong_dn + bear_trig", "S", (strong_dn&bear_trig).values, rr)
        report(dfo, "strong_up + bull_trig", "L", (strong_up&bull_trig).values, rr)
        report(dfo, "strong_dn + macd_dn", "S", (strong_dn&macd_dn).values, rr)
        report(dfo, "strong_up + macd_up", "L", (strong_up&macd_up).values, rr)
        report(dfo, "strong_dn + macd_dn + bear_trig", "S", (strong_dn&macd_dn&bear_trig).values, rr)
        report(dfo, "strong_up + macd_up + bull_trig", "L", (strong_up&macd_up&bull_trig).values, rr)
        report(dfo, "trend_dn + volspike down", "S", (dn&volspike&downbar).values, rr)
        report(dfo, "trend_up + volspike up", "L", (up&volspike&upbar).values, rr)

if __name__=="__main__":
    main()
