"""Conditional-edge scanner.

For every bar we precompute the forward outcome of a hypothetical trade entered at
the NEXT bar open with stop = atr_mult*ATR and target = rr*stop, walking forward up
to max_bars. This gives, per bar, whether a LONG (and separately a SHORT) would have
hit target-before-stop. We then slice these outcomes by causal feature conditions to
see which conditions shift win probability above the fee-adjusted breakeven.

Net breakeven winrate at reward:risk = rr, with fee_R = FEE_RT/stop_frac:
    p_be = (1 + fee_R) / (1 + rr)
A condition only has real edge if realized winrate > p_be on BOTH train and test.
"""
import numpy as np
import pandas as pd
import indicators as ind
from engine import FEE_RT

def forward_outcomes(df, atr_mult=1.2, rr=1.0, max_bars=200, resolve="nearest_open"):
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    c = df["close"].values
    atrv = df["atr14"].values
    n = len(df)
    win_L = np.full(n, np.nan); win_S = np.full(n, np.nan)
    stopfrac = np.full(n, np.nan)
    for i in range(n-1):
        ei = i+1
        rdist = atr_mult*atrv[i]
        if not np.isfinite(rdist) or rdist <= 0:
            continue
        entry = o[ei]
        stopfrac[i] = rdist/entry
        # LONG
        stopL = entry-rdist; tgtL = entry+rr*rdist
        stopS = entry+rdist; tgtS = entry-rr*rdist
        resL = resS = None
        end = min(ei+max_bars, n)
        for j in range(ei, end):
            hj, lj, oj = h[j], l[j], o[j]
            if resL is None:
                hs = lj <= stopL; ht = hj >= tgtL
                if hs and ht:
                    resL = 0 if (resolve=="stop_first" or abs(oj-stopL)<=abs(oj-tgtL)) else 1
                elif hs: resL = 0
                elif ht: resL = 1
            if resS is None:
                hs = hj >= stopS; ht = lj <= tgtS
                if hs and ht:
                    resS = 0 if (resolve=="stop_first" or abs(oj-stopS)<=abs(oj-tgtS)) else 1
                elif hs: resS = 0
                elif ht: resS = 1
            if resL is not None and resS is not None:
                break
        win_L[i] = resL if resL is not None else np.nan   # nan = unresolved (timeout)
        win_S[i] = resS if resS is not None else np.nan
    return win_L, win_S, stopfrac

def breakeven_wr(rr, stopfrac_mean):
    fee_R = FEE_RT/stopfrac_mean
    return (1+fee_R)/(1+rr)

def scan_conditions(tf, atr_mult=1.2, rr=1.0, max_bars=200, min_n=60):
    df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    wl, ws, sf = forward_outcomes(df, atr_mult, rr, max_bars)
    df = df.copy()
    df["win_L"] = wl; df["win_S"] = ws; df["sf"] = sf
    cutoff = pd.Timestamp("2024-12-31", tz="UTC")
    tr = df["dt"] < cutoff
    te = ~tr
    p_be = breakeven_wr(rr, np.nanmean(sf))
    print(f"\n##### TF={tf} atr_mult={atr_mult} rr={rr} maxBars={max_bars} "
          f"| stopfrac~{np.nanmean(sf):.3%} feeR~{FEE_RT/np.nanmean(sf):.3f} "
          f"| net breakeven WR={p_be:.1%} #####")
    # baseline
    for lab, sel in [("ALL_LONG", df["win_L"]), ("ALL_SHORT", df["win_S"])]:
        wtr = sel[tr].dropna(); wte = sel[te].dropna()
        print(f"  {lab:26} train WR={wtr.mean():.1%} (n={len(wtr)})   test WR={wte.mean():.1%} (n={len(wte)})")

    # candidate causal conditions -> (long?, boolean mask)
    C = {}
    up = (df["close"]>df["ema200"]); dn=~up
    up50 = df["ema50"]>df["ema200"]
    C["trend_up (c>ema200)"]       = ("L", up)
    C["trend_dn (c<ema200)"]       = ("S", dn)
    C["strong_up (c>ema200&50>200)"]=("L", up&up50)
    C["strong_dn"]                  =("S", dn&(~up50))
    C["rsi<30"]                     =("L", df["rsi14"]<30)
    C["rsi>70"]                     =("S", df["rsi14"]>70)
    C["rsi<30 & up"]                =("L",(df["rsi14"]<30)&up)
    C["rsi>70 & dn"]                =("S",(df["rsi14"]>70)&dn)
    C["div_bull"]                   =("L", df["div_bull"]==1)
    C["div_bear"]                   =("S", df["div_bear"]==1)
    C["div_bull & up"]              =("L",(df["div_bull"]==1)&up)
    C["div_bear & dn"]              =("S",(df["div_bear"]==1)&dn)
    C["bull_engulf & up"]           =("L",(df["c_bull_engulf"]==1)&up)
    C["bear_engulf & dn"]           =("S",(df["c_bear_engulf"]==1)&dn)
    C["hammer & up"]                =("L",(df["c_hammer"]==1)&up)
    C["star & dn"]                  =("S",(df["c_shooting_star"]==1)&dn)
    if "vol_ratio" in df:
        C["volspike bull & up"]     =("L",(df["vol_ratio"]>2)&(df["c_bull"]==1)&up)
        C["volspike bear & dn"]     =("S",(df["vol_ratio"]>2)&(df["c_bull"]==0)&dn)
    # momentum breakout
    donch_hi = df["high"].shift(1).rolling(20).max()
    donch_lo = df["low"].shift(1).rolling(20).min()
    C["donchian20 breakout up"]     =("L", df["close"]>donch_hi)
    C["donchian20 breakout dn"]     =("S", df["close"]<donch_lo)
    C["macd>0 & rising & up"]       =("L",(df["macd"]>0)&(df["macd_hist"]>df["macd_hist"].shift(1))&up)
    C["macd<0 & falling & dn"]      =("S",(df["macd"]<0)&(df["macd_hist"]<df["macd_hist"].shift(1))&dn)
    # bollinger squeeze breakout
    bw = (df["bb_up"]-df["bb_lo"])/df["bb_mid"]
    squeeze = bw < bw.rolling(50).quantile(0.2)
    C["bb squeeze->up"]             =("L", squeeze.shift(1).fillna(False)&(df["close"]>df["bb_up"]))
    C["bb squeeze->dn"]             =("S", squeeze.shift(1).fillna(False)&(df["close"]<df["bb_lo"]))

    rows=[]
    for name,(sidew,mask) in C.items():
        col = df["win_L"] if sidew=="L" else df["win_S"]
        wtr = col[tr & mask].dropna(); wte = col[te & mask].dropna()
        if len(wtr)<min_n or len(wte)<min_n:
            continue
        rows.append((name, sidew, wtr.mean(), len(wtr), wte.mean(), len(wte)))
    rows.sort(key=lambda r: -min(r[2],r[4]))
    print(f"  {'condition':32} side  trainWR   n     testWR   n   (breakeven {p_be:.1%})")
    for name,sidew,trw,ntr,tew,nte in rows:
        flag = "  <<<" if (trw>p_be and tew>p_be) else ""
        print(f"  {name:32} {sidew:4} {trw:6.1%} {ntr:5d}  {tew:6.1%} {nte:5d}{flag}")

if __name__ == "__main__":
    import sys
    tf = sys.argv[1] if len(sys.argv)>1 else "1h"
    rr = float(sys.argv[2]) if len(sys.argv)>2 else 1.0
    am = float(sys.argv[3]) if len(sys.argv)>3 else 1.2
    scan_conditions(tf, atr_mult=am, rr=rr)
