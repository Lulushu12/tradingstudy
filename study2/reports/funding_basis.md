# Funding / Basis Study (train only: dt < 2025-01-01)

Protocol: pooled 6 perps, matrix_1h & matrix_4h. Net R = (rr if y==1 else -1) - feeR.
Stats = mean net R (mR), naive t (mean/sem, overlapping bars -> inflated; see §6), win rate.
Base rates (all bars): 1h L11 -0.070 / S11 -0.033 / L21 -0.071 / S21 -0.030; 4h L11 -0.048 / S11 +0.001 / L21 -0.010 / S21 -0.052. Everything is judged vs these.

## 1. Contrarian funding — mostly ABSENT / inverted
- F_rate_z30d deciles: no monotonic contrarian gradient either TF. Top decile (z>1.1) shorts are ~base rate (1h S21 -0.032; 4h S21 -0.088 = worse than base). z>2 shorts: 1h S21 -0.033 (t=-2.3), 4h S21 -0.160 (t=-5.8). z>3 1h S11 +0.019 (t=1.3) — only weak hint, sign-flips by year.
- Raw threshold F_rate>0.05%/8h (F_extreme_pos): shorts LOSE (1h S21 -0.025; 4h S21 -0.089 t=-4.5). At 4h the same flag favors LONGS (L21 +0.072 t=3.5) — extreme positive funding marks 2020-21 bull continuation, not reversal. Signals cluster 2020-21 (0 in 2022) -> regime proxy.
- Mirror F_rate<-0.02% (F_extreme_neg): contrarian LONG works: 1h L21 +0.062 (t=4.0), 4h L11 +0.035 / L21 +0.049; deeper F_rate<-0.05%: 1h L21 +0.126 (t=4.3, n=2473), 4h L21 +0.178 (t=3.0), L11 +0.111 (t=2.8). Asymmetry: only crowd-SHORT extremes are fadeable. But per-year: 2020 & 2023 carry it (1h: 2021 -0.03, 2022 -0.01); per-sym 4h: BTC/ETH/XRP negative, SOL/LINK/DOT positive.

## 2. F_cum3d vs instantaneous F_rate
- Deciles: mid-positive buckets (0.0004-0.0008) are where shorts look best (1h S21 +0.03, 4h +0.06); top decile is long-favorable — non-monotone, uninterpretable as positioning stretch.
- Extremes: F_cum3d>q95(0.006): 4h L21 +0.145 (t=5.6) but 97% of signals in 2020-21; ex-2021 mR +0.08 t=1.6. F_cum3d<q05(-0.0011): nothing (all four side/rr combos negative at 1h; 4h mixed, BTC-long +0.64 vs ETH -0.36 — noise).
- Verdict: F_cum3d does NOT beat F_rate. Deep raw F_rate<-0.05% is the cleaner gauge; cum3d mostly re-labels the 2020-21 regime.

## 3. Basis (B_prem_z)
- Deciles flat both TFs. Premium blowout (z>2): mean reversion FAILS — shorts below base (1h S21 -0.078 t=-5.4; 4h S21 -0.175 t=-6.3). z>3 same. Perp-rich is continuation/chop, not a short.
- Discount blowout (z<-2): longs negative too. Only z<-3 (1h, n=1297, 0.5% of bars): L11 +0.066 (t=2.4), all 6 symbols positive (BTC +0.12 ... DOT +0.01), years + except 2021 (-0.16). Modest, one-sided (short21 there = -0.187, confirming upward snap-back).

## 4. Squeeze setups
- SHORT-SQUEEZE long: F_rate<-0.0002 & T_ret_24h>0.02 (shorts paying AND losing):
  4h L21 +0.191 (t=3.2, n=595): 2020 +0.26, 2021 +0.69, 2022 -0.20, 2023 +0.85, 2024 -0.16(n=14); syms + except XRP(-0.33)/DOT(0.00); ex-BTC +0.16 t=2.6. 1h weaker (+0.059 t=2.0, 2022 -0.23).
  Loose version (T_ret_24h>0) diluted: 4h +0.14, 2022 -0.22. Strictness helps.
- LONG-SQUEEZE short (F_rate>0.0005 & T_ret_24h<0): does NOT work — 4h S21 -0.162 (t=-5.0); the same condition favors LONGS (4h L21 +0.127 t=3.6). Mild variant same. Asymmetric: only short squeezes are tradeable.

## 5. Funding-trend alignment (F_x_trend = F_rate * sign(EMA200 dist))
- "Stubborn longs" (downtrend & F_rate>0.0002) -> SHORT: fails. 1h S21 -0.026; 4h S21 -0.063; year signs flip (2020 +0.27/+0.47, 2021 -0.15/-0.31). No signal.
- "Stubborn shorts" (uptrend & F_rate<-0.0001) -> LONG: works at 4h: L21 +0.195 (t=3.7, n=796), positive ALL full years incl. 2022 bear (2020 +0.05, 2021 +0.26, 2022 +0.18, 2023 +0.46); ex-BTC +0.15 t=2.8; syms: BTC +0.72, SOL +0.51, DOT +0.23, LINK +0.11, XRP -0.16, ETH -0.61. 1h version fails (-0.049).
- F_x_trend<-0.0002 as a raw bucket: 4h L21 +0.146 (t=3.6) — the long side again; generic short-the-misalignment story is dead.

## 6. Non-overlapping re-check (real resolution times from klines; one open trade per symbol)
| Rule | med hold | trades | tr/mo (6 syms) | mR | t | per-year |
|---|---|---|---|---|---|---|
| A: 4h uptrend & F_rate<-0.0001, L 2:1 | 8 bars (~34h) | 190 | 3.2 | +0.093 | 0.88 | 20:+0.06 21:+0.13 22:-0.08 23:+0.48 24(n5):-1.02 |
| B: 1h B_prem_z<-3, L 1:1 | 5 bars (~5h) | 811 | 14.0 | +0.037 | 1.06 | 20:+0.11 21:-0.06 22:-0.01 23:+0.24 24:-0.02 |
| C: 4h squeeze strict, L 2:1 | 11 bars (~44h) | 182 | 3.4 | +0.221 | 2.01 | 20:+0.30 21:+0.61 22:-0.23 23:+0.94 |
| D: 1h F_rate<-0.05%, L 2:1 | 11 bars (~11h) | 254 | 5.1 | +0.147 | 1.59 | 20:+0.24 21:-0.04 22:-0.03 23:+0.77 |
Pooled t-stats above were 2-4x inflated by signal clustering (799 -> 190 independent trades for A). Only the squeeze rule keeps t~2 on independent trades; rule A's 2022 robustness evaporates (was clustering in a few good runs).

## Verdicts
| Finding | Verdict |
|---|---|
| Contrarian SHORT vs extreme positive funding (any threshold, any TF) | **artifact** — inverted; crowd-long extremes continue up |
| Contrarian LONG vs extreme negative funding (F_rate<-0.05%) | **fragile** — real asymmetry, but 2020/2023-driven; t=1.6 non-overlap |
| F_cum3d as improvement over F_rate | **artifact** — regime relabeling; ex-2021 nothing |
| B_prem_z>2/3 premium-blowout short | **artifact** — continuation, never reverts within horizon |
| B_prem_z<-3 discount-snap long 1:1 (1h) | **fragile** — all 6 syms positive but mR +0.04, t=1.1 non-overlap |
| Short-squeeze long: 4h F_rate<-0.0002 & T_ret_24h>0.02, 2:1 | **fragile-to-robust** — best of study: non-overlap +0.22R, t=2.0, 3.4 tr/mo, but -0.23R in 2022; needs a bear-regime filter before deployment |
| Long-squeeze short (mirror) | **artifact** — signals long, not short |
| Funding-against-trend short (stubborn longs) | **artifact** |
| Stubborn-shorts-in-uptrend long (4h) | **fragile** — pooled t=3.7 melts to 0.9 on independent trades |

Bottom line: funding/basis extremes here are regime thermometers more than contrarian triggers. The only
directional edge is the negative-funding/long family (short squeeze); everything short-side is dead on train.
