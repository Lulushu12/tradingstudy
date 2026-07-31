"""Stage D: kill the two biases in Stage C, then stress the result.

FIX 1 (look-ahead in universe selection): Stage C picked symbols whose FULL-HISTORY
median volume > $50M. That is knowing the winners in advance. Here liquidity is
point-in-time: a signal is only tradeable if the TRAILING 30-day median quote volume
at that bar already exceeded the threshold.

FIX 2 (regime): report per-year and per-alt-regime, since a short-only book in an
alt bear market is a regime bet, not a system.

Also: effective number of independent bets, and capital capacity.
"""
import numpy as np, pandas as pd
from b_transfer import prep, EMA_N, RR, ATR_MULT, VOL_MULT, MAXBARS
from c_portfolio import portfolio

FEE, SLIP = 0.0010, 0.0005
LIQ_MIN = 5e7          # $50M/day, evaluated point-in-time

def signals_pit(d, liq_min=LIQ_MIN):
    d = d.reset_index(drop=True); n = len(d)
    if n < EMA_N + 60: return []
    o = d["open"].to_numpy(float); h = d["high"].to_numpy(float); l = d["low"].to_numpy(float)
    c, _, _, atr, ema, vma = prep(d)
    dts = d["dt"].to_numpy(); v = d["volume"].to_numpy(float)
    # trailing 30d (=180 4h bars) median daily quote volume, shifted so bar i uses only past
    qv = pd.Series(d["quote_volume"].to_numpy(float))
    liq = (qv.rolling(180).median() * 6).shift(1).to_numpy()
    up = c > ema; spike = v > VOL_MULT * vma
    sig_l = up & spike & (c > o); sig_s = (~up) & spike & (c < o)
    out = []; busy = -1
    for i in range(EMA_N, n - 1):
        if i <= busy or not (sig_l[i] or sig_s[i]): continue
        if not np.isfinite(atr[i]) or atr[i] <= 0: continue
        if not np.isfinite(liq[i]) or liq[i] < liq_min: continue
        s = 1 if sig_l[i] else -1
        ei = i + 1; entry = o[ei]*(1+s*SLIP); rdist = ATR_MULT*atr[i]; sdf = rdist/entry
        if sdf < 0.002: continue
        stop = entry - s*rdist; tgt = entry + s*RR*rdist
        res = None; end = min(ei+MAXBARS, n)
        for j in range(ei, end):
            hs = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            ht = (h[j] >= tgt) if s > 0 else (l[j] <= tgt)
            if hs: res, xi = -1.0, j; break
            if ht: res, xi = RR, j; break
        if res is None: xi = end-1; res = s*(c[xi]-entry)/rdist
        busy = xi
        out.append(dict(entry_dt=dts[ei], exit_dt=dts[xi], side=s, gross_R=res, sdf=sdf,
                        fee_R=(FEE+2*SLIP)/sdf, bars=xi-ei, liq=liq[i]))
    return out

if __name__ == "__main__":
    p = pd.read_parquet("panel_4h.parquet")
    fund = pd.read_parquet("funding.parquet")
    syms = [s for s in p.symbol.unique() if s not in ("BTCUSDT",)]

    rows = []
    for s in syms:
        for t in signals_pit(p[p.symbol == s]):
            t["symbol"] = s; rows.append(t)
    tr = pd.DataFrame(rows)
    tr["entry_dt"] = pd.to_datetime(tr.entry_dt, utc=True)
    tr["exit_dt"] = pd.to_datetime(tr.exit_dt, utc=True)
    print(f"POINT-IN-TIME universe: {tr.symbol.nunique()} symbols ever qualified, "
          f"{len(tr)} signals (Stage C look-ahead version had 15046 from 74 symbols)")

    fmap = {s: g.set_index("dt")["rate"] for s, g in fund.groupby("symbol")}
    fr = []
    for _, r in tr.iterrows():
        ser = fmap.get(r.symbol)
        if ser is None: fr.append(0.0); continue
        seg = ser.loc[(ser.index > r.entry_dt) & (ser.index <= r.exit_dt)]
        fr.append(seg.sum()*r.side / r.sdf)
    tr["funding_R"] = fr
    tr["netR"] = tr.gross_R - tr.fee_R - tr.funding_R
    tr.to_parquet("alt_trades_pit.parquet")

    print("\n" + "="*118)
    print("D1. PORTFOLIO, POINT-IN-TIME UNIVERSE (0.5% risk, max 8 concurrent)")
    print("="*118)
    portfolio(tr, label="long+short")
    sh = portfolio(tr[tr.side==-1], label="SHORT only")
    portfolio(tr[tr.side==1], label="LONG only")

    print("\n" + "="*118)
    print("D2. PER-YEAR EXPECTANCY (net R per trade) -- is this a system or a regime bet?")
    print("="*118)
    tr["yr"] = tr.exit_dt.dt.year
    # alt regime proxy: TOTAL alt basket equal-weight index vs its own 200-bar EMA
    idx = (p[p.symbol.isin(tr.symbol.unique())]
           .assign(ret=lambda x: x.groupby("symbol")["close"].pct_change())
           .groupby("dt")["ret"].mean().fillna(0))
    altidx = (1+idx).cumprod()
    regime = (altidx > altidx.ewm(span=200, adjust=False).mean()).rename("alt_bull")
    tr = tr.join(regime, on="entry_dt")

    piv = tr.pivot_table(index="yr", columns=tr.side.map({1:"long",-1:"short"}),
                         values="netR", aggfunc=["mean","size"])
    print(piv.round(3).to_string())
    print("\nby alt-market regime (alt index above/below its EMA200):")
    print(tr.groupby([tr.alt_bull.map({True:"ALT BULL",False:"ALT BEAR"}),
                      tr.side.map({1:"long",-1:"short"})])["netR"]
            .agg(["size","mean"]).round(3).to_string())

    print("\n" + "="*118)
    print("D3. HOW MANY INDEPENDENT BETS IS THIS REALLY?")
    print("="*118)
    s = tr[tr.side==-1].copy()
    s["day"] = s.entry_dt.dt.floor("D")
    per_day = s.groupby("day").agg(n=("netR","size"), m=("netR","mean"))
    # if trades were independent, day-mean variance would shrink as 1/n
    obs_var = per_day.m.var()
    ind_var = (s.netR.var() / per_day.n).mean()
    eff = s.netR.var()/obs_var if obs_var > 0 else np.nan
    print(f"short trades: {len(s)} over {len(per_day)} active days "
          f"(mean {per_day.n.mean():.1f} signals/day, max {per_day.n.max()})")
    print(f"variance of daily mean R: observed {obs_var:.3f} vs {ind_var:.3f} if independent")
    print(f"-> effective independent bets per active day ~ {eff:.2f} (naive count {per_day.n.mean():.1f})")
    infl = np.sqrt(ind_var/obs_var) if obs_var>0 else np.nan
    naive_t = s.netR.mean()/(s.netR.std()/np.sqrt(len(s)))
    print(f"-> naive t-stat {naive_t:.1f} is inflated ~{1/infl:.1f}x by correlation; "
          f"corrected t ~ {naive_t*infl:.1f}")

    print("\n" + "="*118)
    print("D4. CAPACITY (how much money can this actually run?)")
    print("="*118)
    med_sdf = tr.sdf.median()
    print(f"median stop distance: {med_sdf:.2%} of price -> notional per trade = "
          f"{0.005/med_sdf:.2f}x equity at 0.5% risk")
    for adv_cap in [0.005, 0.01, 0.02]:
        # position notional must stay under adv_cap * that symbol's daily volume
        max_notional = (tr.liq.quantile(0.25) * adv_cap)
        eq = max_notional / (0.005/med_sdf)
        print(f"  at {adv_cap:.1%} of daily volume per position, 25th-pct symbol "
              f"(${tr.liq.quantile(0.25)/1e6:.0f}M/d): max ${max_notional/1e6:.2f}M notional "
              f"-> account ceiling ~${eq/1e6:.1f}M")
