import pandas as pd, numpy as np

MKT = '/home/user/tradingstudy/postmortem/mkt'
PAIRS = ['BTC','ETH','SOL','XRP','LINK','AVAX','SUI','DOGE']
TZ = 3 * 3600 * 1000  # trades are UTC+3

def load(p, tf):
    df = pd.read_csv(f'{MKT}/{p}_{tf}.csv')
    df['dt'] = pd.to_datetime(df.ts + TZ, unit='ms')  # local UTC+3 clock
    return df.set_index('dt')

def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def wavetrend(df, ch=9, avg=12, ma=3):
    hlc3 = (df.high + df.low + df.close) / 3
    esa = ema(hlc3, ch)
    d = ema((hlc3 - esa).abs(), ch)
    ci = (hlc3 - esa) / (0.015 * d)
    wt1 = ema(ci, avg)
    wt2 = wt1.rolling(ma).mean()
    return wt1, wt2

trades = pd.read_csv('/home/user/tradingstudy/postmortem/trades_net.csv', parse_dates=['entry_dt','exit_dt'])

print('=== WEEK RETURNS PER PAIR (close 8/18 20:00 -> 8/25 17:00 local) ===')
for p in PAIRS:
    df = load(p, '1h')
    span = df.loc['2026-08-18 20:00':'2026-08-25 17:00']
    r = span.close.iloc[-1] / span.close.iloc[0] - 1
    lo = span.low.min(); hi = span.high.max()
    print(f"{p:5s} {r*100:+6.1f}%   range {(hi/lo-1)*100:5.1f}%")

print('\n=== DAILY RETURNS PER PAIR (local days) ===')
rows = {}
for p in PAIRS:
    df = load(p, '1h')
    daily = df.close.resample('D').last().pct_change() * 100
    rows[p] = daily.loc['2026-08-19':'2026-08-25']
dr = pd.DataFrame(rows).round(1)
dr.index = dr.index.strftime('%m-%d')
print(dr.to_string())

print('\n=== 1H RETURN CORRELATION (test week) ===')
rets = pd.DataFrame({p: load(p,'1h').loc['2026-08-18':'2026-08-25'].close.pct_change() for p in PAIRS})
c = rets.corr()
print(f"mean pairwise corr: {c.values[np.triu_indices(8,1)].mean():.2f}")

# WT on 1H and 4H at each trade entry
wt = {}
for p in PAIRS:
    df1 = load(p, '1h')
    _, wt2_1h = wavetrend(df1)
    df4 = df1.resample('4h').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    _, wt2_4h = wavetrend(df4)
    wt[p] = (wt2_1h, wt2_4h)

def at(series, t):
    s = series.loc[:t]
    return s.iloc[-1] if len(s) else np.nan

trades['wt1h'] = [at(wt[r.pair][0], r.entry_dt) for r in trades.itertuples()]
trades['wt4h'] = [at(wt[r.pair][1], r.entry_dt) for r in trades.itertuples()]

# market drift during holding period
drift = []
for r in trades.itertuples():
    df = load(r.pair, '15m')
    seg = df.loc[r.entry_dt:r.exit_dt]
    drift.append((seg.close.iloc[-1]/seg.close.iloc[0]-1)*100 if len(seg) > 1 else np.nan)
trades['mkt_drift_pct'] = drift

print('\n=== TRADES WITH HTF WT CONTEXT ===')
t = trades.sort_values('exit_dt')
print(t[['n','pair','dir','entry_dt','exit_type','net','wt1h','wt4h','mkt_drift_pct']].to_string(
    index=False, formatters={'net':'{:7.2f}'.format,'wt1h':'{:6.0f}'.format,'wt4h':'{:6.0f}'.format,'mkt_drift_pct':'{:6.2f}'.format}))

print('\n=== SHORTS vs 4H WT ===')
sh = t[t.dir=='S']
print(sh[['n','pair','entry_dt','net','wt1h','wt4h']].to_string(index=False, formatters={'net':'{:7.2f}'.format,'wt1h':'{:6.0f}'.format,'wt4h':'{:6.0f}'.format}))
print(f"\nshorts taken with 4H wt2 > 0 (bullish side): {(sh.wt4h>0).sum()} of {len(sh)}, net on those: {sh[sh.wt4h>0].net.sum():.2f}")
print(f"longs taken with 4H wt2 > 0: {(t[t.dir=='L'].wt4h>0).sum()} of {len(t[t.dir=='L'])}")

print('\n=== COUNTERFACTUALS ===')
print(f"actual net: {t.net.sum():+8.2f}")
print(f"longs only: {t[t.dir=='L'].net.sum():+8.2f}  ({len(t[t.dir=='L'])} trades)")
print(f"shorts only: {t[t.dir=='S'].net.sum():+8.2f}  ({len(t[t.dir=='S'])} trades)")
t.to_csv('/home/user/tradingstudy/postmortem/trades_ctx.csv', index=False)
