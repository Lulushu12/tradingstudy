# Positioning family — deep dive (TRAIN ONLY: dt < 2025-01-01; metrics span 2022-01-19 .. 2024-12-31)

Method notes. Net R = (rr if y==1 else -1) − feeR. Mean feeR: 1h ≈ 0.051R, 4h ≈ 0.024R (4h trades are ~2x cheaper in R).
Overlap correction: per symbol, bars walked in time order; a signal is taken only if no trade is open; occupancy = actual
bars-to-barrier-touch recomputed from klines with the exact core.py barrier logic (median hold: ~5 bars at 1:1, ~8 at 2:1,
both TFs). All trade stats below are NON-OVERLAPPING unless marked "bar". tr/mo = portfolio trades/month over 36 months.

Caveat found immediately: pooled M_glsr thresholds are NOT symbol-neutral. Per-symbol q80 of M_glsr: BTC 2.06, ETH 2.61,
LINK 3.0, SOL 3.4, XRP 3.9, DOT 4.8. A pooled cut (q80 = 3.57) means BTC almost never fires and DOT supplies ~half the
sample. GLSR results are therefore alt-heavy by construction; M_glsr_z is the symbol-neutral variant for production.

## 1. Stability of the two headline conditions (non-overlapping trades)

GLSR q80 (M_glsr >= 3.57) -> SHORT
| TF, rr | all: n / wr / netR | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| 1h 1:1 | 4771 / .527 / +0.003 | +0.048 | −0.072 | +0.012 |
| 1h 2:1 | 2591 / .366 / +0.049 | +0.133 | −0.055 | +0.044 |
| 4h 1:1 | 1325 / .545 / +0.066 | +0.163 | −0.001 | +0.035 |
| 4h 2:1 |  687 / .394 / +0.161 | +0.400 | −0.023 | +0.102 |
Per symbol (4h 2:1): DOT +0.06 (n=312), ETH +0.11, LINK +0.63, SOL +0.12, XRP +0.22, BTC n=4. 2023 is flat-to-negative
everywhere at q80; on 1h the 1:1 edge disappears entirely after overlap correction (+0.003 ≈ zero). Edge is real but thin
at q80 and lives in the alts.

M_tlsr_acct_z <= −1.5 -> LONG
| TF, rr | all: n / wr / netR | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| 1h 1:1 | 1874 / .538 / +0.025 | −0.066 (n=137) | +0.047 | +0.016 |
| 1h 2:1 | 1122 / .390 / +0.122 | −0.030 (n=90) | +0.186 | +0.074 |
| 4h 1:1 |  687 / .560 / +0.094 | −0.114 (n=51) | +0.120 | +0.100 |
| 4h 2:1 |  445 / .422 / +0.241 | −0.223 (n=34) | +0.359 | +0.192 |
Per symbol (4h 2:1): BTC +0.58, DOT +0.12, ETH +0.22, LINK +0.21, SOL +0.37, XRP +0.01 — positive on 6/6 (XRP flat).
2022 is negative but nearly empty (signal barely fires in the bear year); 2023 and 2024 both solidly positive, all TFs.

## 2. Threshold sweeps (bar-level wr/netR + non-overlap wr and 2:1 netR)

M_glsr -> SHORT, 4h: (thr | bar wr11/net11 | bar wr21/net21 | novl tr/mo | novl wr11 | novl wr21 | novl net21)
3.5 | .556/+0.086 | .374/+0.097 | 38 | .548 | .400 | +0.178
4.0 | .567/+0.110 | .392/+0.152 | 26 | .560 | .409 | +0.204
4.5 | .577/+0.129 | .408/+0.201 | 16 | .574 | .429 | +0.263
5.0 | .592/+0.160 | .419/+0.233 | 10 | .610 | .471 | +0.389
Monotone improvement with threshold (good sign). 1:1 wr crosses 60% and 2:1 approaches 47% at M_glsr >= 5.0 on 4h,
at ~10 (1:1) / ~5 (2:1) trades/mo. On 1h the same sweep tops out at novl wr11 ≈ .548, net21 ≈ +0.13-0.15 — much weaker.
At GLSR >= 4.5, 4h 2:1: n=301, per-year netR +0.48 / +0.09 / +0.13 — positive all three years, but DOT+XRP = 70% of trades.

M_tlsr_acct_z -> LONG, 4h:
−0.5 | .542/+0.057 | .393/+0.151 | 50 | .531 | .388 | +0.138
−1.0 | .579/+0.131 | .429/+0.259 | 34 | .558 | .422 | +0.239
−1.5 | .595/+0.163 | .448/+0.318 | 19 | .560 | .422 | +0.241
−2.0 | .605/+0.182 | .480/+0.413 |  9 | .559 | .429 | +0.261
Plateau from −1.0 onward after overlap correction (bar-level keeps rising because extreme episodes contain many
overlapping bars). Bar 2:1 wr touches 48% at −2.0 (~9 sig/mo). On 1h: −2.0 gives novl net21 +0.159 at 13 tr/mo (weaker).

## 3. Interactions (bar-level)

- GLSR q80 short, 1h: downtrend (T_ema200_dist<0) net21 +0.136 vs uptrend +0.051; funding>0 +0.152 vs funding<0 +0.036.
  Both filters sharpen the 1h edge meaningfully. On 4h neither adds much (trend/funding splits all within noise).
- TLSRz −1.5 long, 1h: works ONLY with trend (uptrend net21 +0.125 vs downtrend −0.024). On 4h it works in both regimes
  (downtrend even better, +0.411, n=717 bars). Funding sign adds nothing for TLSR.
- Non-overlap check of "GLSR>=4 & funding>0" on 1h 2:1: +0.132/trade at 37 tr/mo, but 2023 still −0.07 — the filter does
  not fix the weak year, it mostly upsamples 2024.

## 4. Candidate rules (all stats = non-overlapping train trades)

RULE 1 — 4h LONG, 2:1, when M_tlsr_acct_z <= −1.5 (top-trader accounts unusually short).
  n=445, wr 42.2%, net +0.241R/trade, 12.4 tr/mo. Per year: 2022 −0.22 (n=34), 2023 +0.36 (n=216), 2024 +0.19 (n=195).
  Positive on 6/6 symbols; insensitive to threshold (−1.0 gives +0.239 at 20 tr/mo); symbol-neutral z-score by design.
  Verdict: promising/robust — the best thing in the family; only blemish is a near-empty negative 2022.

RULE 2 — 4h SHORT, 2:1, when M_glsr >= 4.5 (crowd heavily long).
  n=301, wr 42.9%, net +0.263R/trade, 8.4 tr/mo. Per year: 2022 +0.48, 2023 +0.09, 2024 +0.13 — positive all 3 years,
  and the sweep is cleanly monotone. BUT: BTC/ETH essentially never trade it; DOT is 52% of trades, half the profit is
  2022 DOT/LINK. Verdict: promising but symbol-concentrated — treat as an alt-only rule; re-cut with M_glsr_z (per-symbol
  z) before trusting it as a universal signal.

RULE 3 — 1h SHORT, 2:1, when M_glsr >= 4.0 AND F_rate > 0 (optionally + T_ema200_dist < 0).
  n=1340, wr 39.4%, net +0.132R/trade, 37 tr/mo. Per year: 2022 +0.38, 2023 −0.07, 2024 +0.11.
  Verdict: fragile — 2023 is negative however it is filtered, the 1:1 variant is fee-dead (net ≈ +0.05), and 1h fees
  (0.05R) consume ~a third of the gross edge. Keep only as a volume overlay, not a standalone.

Honest summary: bar-level screens overstated this family ~2-4x (overlapping bars from the same episode). What survives
overlap correction is concentrated on the 4h TF at 2:1 payoff: contrarian long on extreme top-trader shortness (robust),
and contrarian short on extreme global long-crowding (real but alt-concentrated, 2023-weak). M_tvr / M_tlsr_pos screen
buckets (bar expR ≤ ~0.11, below the shrink factor observed here) were not pursued and are not proposed as rules.
