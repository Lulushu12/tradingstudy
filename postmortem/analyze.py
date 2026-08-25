import pandas as pd

df = pd.read_csv('/home/user/tradingstudy/postmortem/trades.csv', parse_dates=['entry_dt','exit_dt'])
FEE = 0.00004  # 0.004% per side as stated by trader

sign = df['dir'].map({'L': 1, 'S': -1})
df['gross'] = (df['exit_notional'] - df['entry_notional']) * sign
df['fees'] = (df['entry_notional'] + df['exit_notional']) * FEE
df['net'] = df['gross'] - df['fees']
df = df.sort_values('exit_dt').reset_index(drop=True)
df['equity'] = 10000 + df['net'].cumsum()

pd.set_option('display.width', 200)
print(df[['n','pair','dir','entry_dt','exit_dt','exit_type','gross','net','equity','note']].to_string(
    formatters={'gross':'{:8.2f}'.format,'net':'{:8.2f}'.format,'equity':'{:9.2f}'.format}))

print('\n=== TOTALS ===')
print(f"trades: {len(df)}  gross: {df.gross.sum():.2f}  fees: {df.fees.sum():.2f}  net: {df.net.sum():.2f}")
print(f"final equity: {df.equity.iloc[-1]:.2f}  peak: {df.equity.max():.2f} at trade {df.equity.idxmax()+1} ({df.loc[df.equity.idxmax(),'exit_dt']})")
wins = df[df.net > 0]; losses = df[df.net <= 0]
print(f"wins: {len(wins)} ({len(wins)/len(df)*100:.0f}%)  avg win: {wins.net.mean():.2f}  avg loss: {losses.net.mean():.2f}")
print(f"profit factor: {wins.net.sum()/-losses.net.sum():.2f}")

print('\n=== BY DAY (exit date) ===')
byday = df.groupby(df.exit_dt.dt.date).agg(n=('net','size'), net=('net','sum'), wins=('net', lambda s: (s>0).sum()))
print(byday.to_string(formatters={'net':'{:8.2f}'.format}))

print('\n=== BY PAIR ===')
print(df.groupby('pair').agg(n=('net','size'), net=('net','sum'), wins=('net', lambda s:(s>0).sum())).sort_values('net').to_string(formatters={'net':'{:8.2f}'.format}))

print('\n=== BY DIRECTION ===')
print(df.groupby('dir').agg(n=('net','size'), net=('net','sum'), wins=('net', lambda s:(s>0).sum())).to_string(formatters={'net':'{:8.2f}'.format}))

print('\n=== STREAKS (chronological W/L string) ===')
seq = ''.join('W' if x > 0 else 'L' for x in df.net)
print(seq)
import itertools
runs = [(k, len(list(g))) for k, g in itertools.groupby(seq)]
print('runs:', runs)
print('longest L streak:', max((l for k,l in runs if k=='L'), default=0))

print('\n=== RISK PER TRADE (|net| of SL exits as proxy) ===')
sl = df[df.exit_type=='SL']
print(sl[['n','pair','net']].to_string(formatters={'net':'{:8.2f}'.format}))

print('\n=== HOLD TIMES ===')
df['mins'] = (df.exit_dt - df.entry_dt).dt.total_seconds()/60
print(f"median hold: {df.mins.median():.0f} min   win median: {df[df.net>0].mins.median():.0f}   loss median: {df[df.net<=0].mins.median():.0f}")
df.to_csv('/home/user/tradingstudy/postmortem/trades_net.csv', index=False)
