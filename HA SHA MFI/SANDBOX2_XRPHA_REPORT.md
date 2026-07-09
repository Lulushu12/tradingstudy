# SANDBOX2 XRPHA REPORT (CANDIDATE 2: convergence rule)

Frozen rule per FROZEN_SPEC_XRPHA.md, 'CANDIDATE 2: convergence rule' section. Sandbox segment only: bars with time < 2024-01-01 00:00 UTC. No number from 2024 onward appears anywhere in this report.

## 1. Census

bars in sandbox: 139736
HA colors: red=68023 green=71712 doji=1
momentum candles: long-side(green,no-lower-wick)=30899 short-side(red,no-upper-wick)=27699

LONG side filters (bar counts, independent):
  mfi>0: 63506
  sha bullish: 71595
  momentum AND in-window: 16506
  jointly (armed [momentum-with-mfi>0 seen in window] AND green AND sha AND window, pre window-consumption dedup): 7680
  signals (joint AND window not yet consumed): 6824
  entries (signals passing stop filter): 1142
  skipped_min_stop: 5528
  skipped_degenerate (stop_d<=0): 154

SHORT side filters (bar counts, independent):
  mfi<0: 76165
  sha bearish: 68140
  momentum AND in-window: 15434
  jointly (armed [momentum-with-mfi<0 seen in window] AND red AND sha AND window, pre window-consumption dedup): 8683
  signals (joint AND window not yet consumed): 7682
  entries (signals passing stop filter): 1430
  skipped_min_stop: 5996
  skipped_degenerate (stop_d<=0): 256

TOTAL: signals=14506 entries=2572 skipped_min_stop=11524 skipped_degenerate=410

Path split (t==k 'old' path reduces exactly to candidate 1; t>k 'new' path is the convergence extension):
  long: old=782 new=360
  short: old=975 new=455
  total: old=1757 new=815
open_at_end (marked to market at final sandbox close): 0
(informational) same-bar SL+TP ambiguous bars resolved as SL (worst case): 15

## 2. Pooled result at baseline costs (1bp slip)

pooled: n=2572 exp=-0.1340R (SE 0.0277) win=32.5% PF=0.821 streak=20 (9d)
longs: n=1142 exp=-0.0918R (SE 0.0420) win=33.9% PF=0.875 streak=16 (36d)
shorts: n=1430 exp=-0.1676R (SE 0.0368) win=31.4% PF=0.780 streak=20 (15d)

## 2b. Path split at baseline costs (path_old: t==k, reduces to candidate 1; path_new: t>k, the convergence extension)

path_old: n=1757 exp=-0.1056R (SE 0.0338) win=33.4% PF=0.857 streak=21 (22d)
path_new: n=815 exp=-0.1951R (SE 0.0485) win=30.7% PF=0.748 streak=13 (24d)

## 3. Per half-year window (2020H1-2023H2)

2020H1: n=256 exp=-0.2025R (SE 0.0863) win=30.5% PF=0.739 streak=18 (20d)
2020H2: n=360 exp=-0.1378R (SE 0.0739) win=32.2% PF=0.816 streak=14 (5d)
2021H1: n=664 exp=+0.0510R (SE 0.0565) win=38.1% PF=1.076 streak=11 (1d)
2021H2: n=428 exp=-0.2454R (SE 0.0658) win=29.0% PF=0.690 streak=20 (9d)
2022H1: n=334 exp=-0.1908R (SE 0.0759) win=30.8% PF=0.753 streak=12 (7d)
2022H2: n=240 exp=-0.2697R (SE 0.0873) win=28.3% PF=0.664 streak=17 (9d)
2023H1: n=158 exp=-0.0985R (SE 0.1131) win=34.2% PF=0.867 streak=9 (7d)
2023H2: n=132 exp=-0.2117R (SE 0.1198) win=30.3% PF=0.729 streak=10 (10d)

windows with trades: 8, nonnegative: 1, negative: 7

## 4. Cost sweep (slippage bp/fill)

    0 bp: -0.1127R (n=2572)
    1 bp: -0.1340R (n=2572)
    2 bp: -0.1553R (n=2572)
    3 bp: -0.1765R (n=2572)
    5 bp: -0.2191R (n=2572)
   10 bp: -0.3256R (n=2572)
  breakeven slippage: below 0bp (already negative at 0bp)

## 5. Frozen pass bar evaluation

Sandbox pass bar: net expectancy >= +0.15R AND more than half of the half-year windows nonnegative.
  pooled net expectancy: -0.1340R (< +0.15R)
  windows nonnegative: 1/8 (NOT > half)
  => pass bar: NOT MET

Kill checks (K-form):
  K1 pooled expectancy <= 0: -0.1340R -> KILL
  K2 windows negative: 7/8 -> KILL
  K3 breakeven slippage < 3bp: below 0bp (already negative at 0bp) -> KILL
  K4 pooled expectancy <= 0 without best window (2021H1): -0.1983R -> KILL

VERDICT: DEAD
  reason(s): pass bar not met, K1 kill, K2 kill, K3 kill, K4 kill

## Sanity checks
(a) entry-bar-is-signal+900s: 2572/2572 exact; violations=0 (would occur only if a signal bar immediately precedes one of the sandbox's 4 documented small data holes -- positional 'next bar' indexing is used throughout, per the file docstring)
(b) no trade touches time>=2024-01-01: violations=0
(c) independent slow-path recheck of 5 randomly-chosen trades:
    trade #732 (long, t_signal=1611993600): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.0825 fast=-1.0825 OK
    trade #99 (short, t_signal=1583024400): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.1638 fast=-1.1638 OK
    trade #1497 (long, t_signal=1632379500): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.1381 fast=-1.1381 OK
    trade #1531 (short, t_signal=1633545900): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.1223 fast=-1.1223 OK
    trade #1718 (long, t_signal=1641942000): gross_r slow=-1.0000 fast=-1.0000 OK, net_r slow=-1.1478 fast=-1.1478 OK

(d) candidate 1 subsumption check: every candidate 1 entry should appear in candidate 2's entry set UNLESS its window was already consumed by an earlier candidate-2 new-path (t>k) completion.
    candidate 1 entries: 2245
    candidate 1 entries missing from candidate 2: 13
    MISSING (explained): dir=long t_signal=6105 e=6106 window_anchor=6102 -- window already consumed at t_signal=6104 by an earlier candidate-2 new-path entry (t_momentum=6103, e=6105)
    MISSING (explained): dir=long t_signal=17502 e=17503 window_anchor=17499 -- window already consumed at t_signal=17501 by an earlier candidate-2 new-path entry (t_momentum=17500, e=17502)
    MISSING (explained): dir=short t_signal=34083 e=34084 window_anchor=34080 -- window already consumed at t_signal=34082 by an earlier candidate-2 new-path entry (t_momentum=34081, e=34083)
    MISSING (explained): dir=long t_signal=37610 e=37611 window_anchor=37607 -- window already consumed at t_signal=37609 by an earlier candidate-2 new-path entry (t_momentum=37608, e=37610)
    MISSING (explained): dir=long t_signal=37680 e=37681 window_anchor=37677 -- window already consumed at t_signal=37679 by an earlier candidate-2 new-path entry (t_momentum=37678, e=37680)
    MISSING (explained): dir=long t_signal=42348 e=42349 window_anchor=42345 -- window already consumed at t_signal=42347 by an earlier candidate-2 new-path entry (t_momentum=42346, e=42348)
    MISSING (explained): dir=long t_signal=43449 e=43450 window_anchor=43446 -- window already consumed at t_signal=43448 by an earlier candidate-2 new-path entry (t_momentum=43447, e=43449)
    MISSING (explained): dir=long t_signal=47018 e=47019 window_anchor=47015 -- window already consumed at t_signal=47017 by an earlier candidate-2 new-path entry (t_momentum=47016, e=47018)
    MISSING (explained): dir=short t_signal=47637 e=47638 window_anchor=47634 -- window already consumed at t_signal=47636 by an earlier candidate-2 new-path entry (t_momentum=47635, e=47637)
    MISSING (explained): dir=long t_signal=55932 e=55933 window_anchor=55929 -- window already consumed at t_signal=55931 by an earlier candidate-2 new-path entry (t_momentum=55930, e=55932)
    MISSING (explained): dir=short t_signal=73684 e=73685 window_anchor=73681 -- window already consumed at t_signal=73683 by an earlier candidate-2 new-path entry (t_momentum=73682, e=73684)
    MISSING (explained): dir=short t_signal=85528 e=85529 window_anchor=85525 -- window already consumed at t_signal=85527 by an earlier candidate-2 new-path entry (t_momentum=85526, e=85528)
    MISSING (explained): dir=short t_signal=126685 e=126686 window_anchor=126682 -- window already consumed at t_signal=126684 by an earlier candidate-2 new-path entry (t_momentum=126683, e=126685)
    unexplained missing entries: 0 (OK, all explained by earlier new-path consumption)

## 6. Trade log
per-trade CSV written to /home/user/tradingstudy/HA SHA MFI/sandbox2_trades.csv
