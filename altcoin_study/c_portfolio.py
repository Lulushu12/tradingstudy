"""Stage C: portfolio-level simulation across the liquid alt universe.

Fixes the fatal flaw in Stage B's t-stats: 75 alt perps are NOT 75 independent bets.
Simulates real concurrency, compounding, funding carry, and a cap on simultaneous risk.
"""
import numpy as np, pandas as pd
from b_transfer import prep, EMA_N, RR, ATR_MULT, VOL_MULT, MAXBARS

FEE, SLIP = 0.0010, 0.0005

def signals_for(d, fee, slip):
    d = d.reset_index(drop=True); n = len(d)
    if n < EMA_N + 30: return []
    o = d["open"].to_numpy(float); h = d["high"].to_numpy(float); l = d["low"].to_numpy(float)
    c, _, _, atr, ema, vma = prep(d)
    dts = d["dt"].to_numpy(); v = d["volume"].to_numpy(float)
    up = c > ema; spike = v > VOL_MULT * vma
    sig_l = up & spike & (c > o); sig_s = (~up) & spike & (c < o)
    out = []; busy = -1
    for i in range(EMA_N, n - 1):
        if i <= busy or not (sig_l[i] or sig_s[i]): continue
        if not np.isfinite(atr[i]) or atr[i] <= 0: continue
        s = 1 if sig_l[i] else -1
        ei = i + 1; entry = o[ei] * (1 + s * slip); rdist = ATR_MULT * atr[i]
        sdf = rdist / entry
        if sdf < 0.002: continue
        stop = entry - s * rdist; tgt = entry + s * RR * rdist
        res = None; end = min(ei + MAXBARS, n)
        for j in range(ei, end):
            hs = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            ht = (h[j] >= tgt) if s > 0 else (l[j] <= tgt)
            if hs: res, xi = -1.0, j; break
            if ht: res, xi = RR, j; break
        if res is None:
            xi = end - 1; res = s * (c[xi] - entry) / rdist
        busy = xi
        out.append(dict(entry_dt=dts[ei], exit_dt=dts[xi], side=s, gross_R=res,
                        sdf=sdf, fee_R=(fee + 2*slip)/sdf, bars=xi-ei))
    return out

def portfolio(tr, risk=0.005, max_conc=8, label="", equity0=100.0):
    """Sequential equity sim. Positions opened only if concurrency slot free."""
    tr = tr.sort_values("entry_dt").reset_index(drop=True)
    eq = equity0; open_pos = []; curve = []; taken = []
    for _, r in tr.iterrows():
        t0 = r.entry_dt
        realised = [p for p in open_pos if p[0] <= t0]
        for p in sorted(realised, key=lambda x: x[0]):
            eq *= (1 + p[1] * risk); curve.append((p[0], eq))
        open_pos = [p for p in open_pos if p[0] > t0]
        if len(open_pos) >= max_conc:
            continue
        netR = r.gross_R - r.fee_R - r.funding_R
        open_pos.append((r.exit_dt, netR)); taken.append(netR)
    for p in sorted(open_pos, key=lambda x: x[0]):
        eq *= (1 + p[1] * risk); curve.append((p[0], eq))
    cv = pd.DataFrame(curve, columns=["dt","equity"])
    cv["dt"] = pd.to_datetime(cv.dt, utc=True)
    peak = cv.equity.cummax(); dd = (cv.equity/peak - 1)
    yrs = (cv.dt.max()-cv.dt.min()).days/365.25
    cagr = (cv.equity.iloc[-1]/equity0)**(1/yrs) - 1
    taken = np.array(taken)
    # longest losing streak
    ls = mx = 0
    for x in taken:
        ls = ls+1 if x < 0 else 0; mx = max(mx, ls)
    m = cv.set_index("dt")["equity"].resample("ME").last().ffill().pct_change().dropna()
    print(f"{label:<40} n={len(taken):<6} E={taken.mean():+.3f}R  WR={(taken>0).mean():5.1%}  "
          f"CAGR={cagr:+7.1%}  maxDD={dd.min():7.1%}  Calmar={cagr/abs(dd.min()):5.2f}  "
          f"mo+={(m>0).mean():4.0%}  streak={mx}")
    return cv, taken, m

if __name__ == "__main__":
    p = pd.read_parquet("panel_4h.parquet")
    u = pd.read_parquet("universe.parquet")
    fund = pd.read_parquet("funding.parquet")

    big = [s for s in u[u.adv_usd > 5e7].index if s != "BTCUSDT"]
    print(f"tradeable universe (>$50M median daily volume): {len(big)} symbols\n")

    rows = []
    for s in big:
        for t in signals_for(p[p.symbol == s], FEE, SLIP):
            t["symbol"] = s; rows.append(t)
    tr = pd.DataFrame(rows)
    tr["entry_dt"] = pd.to_datetime(tr.entry_dt, utc=True)
    tr["exit_dt"] = pd.to_datetime(tr.exit_dt, utc=True)

    # ---- funding carry while position is open (short earns positive funding) ----
    fmap = {s: g.set_index("dt")["rate"] for s, g in fund[fund.symbol.isin(big)].groupby("symbol")}
    fr = []
    for _, r in tr.iterrows():
        ser = fmap.get(r.symbol)
        if ser is None: fr.append(0.0); continue
        seg = ser.loc[(ser.index > r.entry_dt) & (ser.index <= r.exit_dt)]
        pay = seg.sum() * r.side          # long pays positive funding
        fr.append(pay / r.sdf)            # convert to R
    tr["funding_R"] = fr
    print(f"total signals: {len(tr)}   median hold {tr.bars.median():.0f} bars "
          f"({tr.bars.median()*4:.0f}h)   mean funding drag {tr.funding_R.mean():+.4f}R\n")

    print("=" * 118)
    print("PORTFOLIO RESULTS  (0.5% risk/trade, max 8 concurrent, 10bp fee + 5bp slip, funding modelled)")
    print("=" * 118)
    both = portfolio(tr, label="alt basket, long+short")
    shorts = portfolio(tr[tr.side == -1], label="alt basket, SHORT only")
    longs = portfolio(tr[tr.side == 1], label="alt basket, LONG only")
    btc_tr = pd.DataFrame([dict(**t, symbol="BTCUSDT", funding_R=0.0)
                           for t in signals_for(p[p.symbol=="BTCUSDT"], FEE, SLIP)])
    btc_tr["entry_dt"]=pd.to_datetime(btc_tr.entry_dt,utc=True); btc_tr["exit_dt"]=pd.to_datetime(btc_tr.exit_dt,utc=True)
    portfolio(btc_tr, label="BTC only (the old study)")

    print("\n--- concurrency / risk-cap sensitivity (short-only) ---")
    for mc in [3, 5, 8, 12, 20]:
        portfolio(tr[tr.side==-1], max_conc=mc, label=f"  max_conc={mc}")
    print("\n--- out-of-sample split (short-only, train<2025 / test>=2025) ---")
    for lab, sub in [("train (2020-2024)", tr[(tr.side==-1)&(tr.exit_dt<'2025-01-01')]),
                     ("test  (2025-2026)", tr[(tr.side==-1)&(tr.exit_dt>='2025-01-01')])]:
        portfolio(sub, label=f"  {lab}")

    cv, taken, m = shorts
    cv.to_parquet("curve_short.parquet"); tr.to_parquet("alt_trades.parquet")
    print("\nmonthly return distribution (short-only): "
          f"median {m.median():+.2%}  worst {m.min():+.2%}  best {m.max():+.2%}")
