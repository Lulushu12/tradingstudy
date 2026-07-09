# SANDBOX XRPHA REPORT

Frozen rule per FROZEN_SPEC_XRPHA.md. Sandbox segment only: bars with time < 2024-01-01 00:00 UTC. No number from 2024 onward appears anywhere in this report.

## 1. Census

bars in sandbox: 139736
HA colors: red=68023 green=71712 doji=1
momentum candles: long-side(green,no-lower-wick)=30899 short-side(red,no-upper-wick)=27699

LONG side filters (bar counts, independent):
  mfi>0: 63506
  sha bullish: 71595
  momentum AND in-window: 16506
  jointly (mfi AND sha AND momentum AND window, pre window-consumption dedup): 6096
  signals (joint AND window not yet consumed): 5472
  entries (signals passing stop filter): 1003
  skipped_min_stop: 4365
  skipped_degenerate (stop_d<=0): 104

SHORT side filters (bar counts, independent):
  mfi<0: 76165
  sha bearish: 68140
  momentum AND in-window: 15434
  jointly (mfi AND sha AND momentum AND window, pre window-consumption dedup): 6881
  signals (joint AND window not yet consumed): 6163
  entries (signals passing stop filter): 1242
  skipped_min_stop: 4747
  skipped_degenerate (stop_d<=0): 174

TOTAL: signals=11635 entries=2245 skipped_min_stop=9112 skipped_degenerate=278
open_at_end (marked to market at final sandbox close): 0
(informational) same-bar SL+TP ambiguous bars resolved as SL (worst case): 13

## 2. Pooled result at baseline costs (1bp slip)

pooled: n=2245 exp=-0.1391R (SE 0.0296) win=32.3% PF=0.815 streak=18 (9d)
longs: n=1003 exp=-0.0990R (SE 0.0447) win=33.6% PF=0.865 streak=12 (14d)
shorts: n=1242 exp=-0.1716R (SE 0.0395) win=31.2% PF=0.775 streak=17 (15d)

## 3. Per half-year window (2020H1-2023H2)

2020H1: n=230 exp=-0.2030R (SE 0.0911) win=30.4% PF=0.739 streak=16 (20d)
2020H2: n=316 exp=-0.1346R (SE 0.0789) win=32.3% PF=0.820 streak=15 (11d)
2021H1: n=573 exp=+0.0293R (SE 0.0605) win=37.3% PF=1.043 streak=11 (1d)
2021H2: n=378 exp=-0.2643R (SE 0.0696) win=28.3% PF=0.669 streak=18 (9d)
2022H1: n=294 exp=-0.1663R (SE 0.0815) win=31.6% PF=0.782 streak=15 (10d)
2022H2: n=205 exp=-0.2684R (SE 0.0944) win=28.3% PF=0.665 streak=15 (9d)
2023H1: n=136 exp=-0.0834R (SE 0.1221) win=34.6% PF=0.886 streak=12 (18d)
2023H2: n=113 exp=-0.2189R (SE 0.1292) win=30.1% PF=0.720 streak=8 (10d)

windows with trades: 8, nonnegative: 1, negative: 7

## 4. Cost sweep (slippage bp/fill)

    0 bp: -0.1181R (n=2245)
    1 bp: -0.1391R (n=2245)
    2 bp: -0.1602R (n=2245)
    3 bp: -0.1812R (n=2245)
    5 bp: -0.2234R (n=2245)
   10 bp: -0.3287R (n=2245)
  breakeven slippage: below 0bp (already negative at 0bp)

## 5. Frozen pass bar evaluation

Sandbox pass bar: net expectancy >= +0.15R AND more than half of the half-year windows nonnegative.
  pooled net expectancy: -0.1391R (< +0.15R)
  windows nonnegative: 1/8 (NOT > half)
  => pass bar: NOT MET

Kill checks (K-form):
  K1 pooled expectancy <= 0: -0.1391R -> KILL
  K2 windows negative: 7/8 -> KILL
  K3 breakeven slippage < 3bp: below 0bp (already negative at 0bp) -> KILL
  K4 pooled expectancy <= 0 without best window (2021H1): -0.1969R -> KILL

VERDICT: DEAD
  reason(s): pass bar not met, K1 kill, K2 kill, K3 kill, K4 kill

## Sanity checks
(a) entry-bar-is-signal+900s: 2245/2245 exact; violations=0 (would occur only if a signal bar immediately precedes one of the sandbox's 4 documented small data holes -- positional 'next bar' indexing is used throughout, per the file docstring)
(b) no trade touches time>=2024-01-01: violations=0
(c) independent slow-path recheck of 5 randomly-chosen trades:
    trade #639 (short, t_signal=1611788400): gross_r slow=+2.0000 fast=+2.0000 OK, net_r slow=+1.8737 fast=+1.8737 OK
    trade #87 (short, t_signal=1583086500): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.1618 fast=-1.1618 OK
    trade #1306 (short, t_signal=1632241800): gross_r slow=+2.0000 fast=+2.0000 OK, net_r slow=+1.8848 fast=+1.8848 OK
    trade #1336 (short, t_signal=1633358700): gross_r slow=+2.0000 fast=+2.0000 OK, net_r slow=+1.8835 fast=+1.8835 OK
    trade #1500 (long, t_signal=1641503700): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.1334 fast=-1.1334 OK

## 6. Trade log
per-trade CSV written to /home/user/tradingstudy/HA SHA MFI/sandbox_trades.csv
