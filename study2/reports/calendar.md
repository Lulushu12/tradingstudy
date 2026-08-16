# Calendar / Time-Effect Study (TRAIN ONLY: dt < 2025-01-01)

Data: matrix_1h (250,530 rows) / matrix_4h (62,634 rows), 6 symbols, 2020-01-01..2024-12-31.
Edge = wr - breakeven_wr; breakeven = (1+median feeR)/(rr+1). Median feeR: 1h 0.0443 (be 1:1 = 0.522), 4h 0.0212.
Net R = (rr if y=1 else -1) - feeR. Pooled rows are cross-sym correlated, so quoted z's are optimistic; per-year stability is the real filter.

## 1. Day-of-month: dom 7-10 short / dom 25-28 long (2:1)

**dom 7-10 SHORT 2:1** — pooled edge +2.5% (1h, z=9.7), +4.2% (4h, z=7.9) vs -1.3%/-2.5% rest-of-month.
Per-year (1h edge): 2020 +0.9 | 2021 +1.4 | 2022 **+5.5** | 2023 **+4.2** | 2024 **-0.1**. 4h: 2024 = -6.1.
Per-symbol (1h): BTC -0.4, LINK +1.1, others +2.4..+5.5. Raw fwd-24h return dom 7-10: -8 bps pooled, but per-year
-5 / +28 / -93 / -21 / **+50** bps — sign flips; 2022 alone contributes most of the pooled effect.
**Verdict: NOT stable — driven by 2022-23 bear/chop; dead in 2024 and in BTC. Treat as regime artifact, not a rule.**

**dom 25-28 LONG 2:1** — pooled edge +1.7% (1h, z=6.4), +6.7% (4h, z=12.8) vs -2.7%/-1.3% rest.
Per-year absolute edge (1h): 2020 +5.2 | 2021 +0.5 | 2022 +0.5 | 2023 +3.9 | 2024 **-1.2**. 4h: +10.4/+15.5/+2.9/+5.4/-0.2.
Relative edge (in minus out) positive **5/5 years on 1h** (+4.7/+1.5/+6.2/+7.9/+1.7 pp) and 4/5 on 4h.
Sanity check, raw fwd-24h return dom 26-28: **positive all 5 years** (+85/+74/+10/+47/+60 bps) vs +18 bps unconditional.
Per-symbol edge positive 6/6 on 4h, 5/6 on 1h (XRP -0.5).
**Verdict: the only dom effect with cross-check support. As an absolute long edge it failed 2024 net of fees;
as a *relative* tilt (late-month drift, "avoid shorts / prefer longs dom 25-28") it held every year. Candidate — weak, filter-grade only.**

Full dom-decile fwd-24h (bps): 1-3 +34, 4-6 +59, 7-10 -8, 11-13 +46, 14-16 +30, 17-19 -17, 20-22 -4, 23-25 +33, 26-28 +54, 29-31 +67.

## 2. Hour-of-day / day-of-week (1h, 1:1)

Full 24-hour table computed (long & short edge + per-year sign counts). Headline: **every one of the 48 hour×side cells
has negative pooled edge**. Best cells: short @ h23 (-0.001), short @ h11 (-0.006); best per-year consistency is 3/5
(short h13). Long is negative at all 24 hours, 0-1 years positive out of 5. No hour block clears breakeven in even 4/5 years.
Sessions (1:1 edge, long/short): US -2.7/-1.7, Asia -3.1/-1.3, EU/other -3.6/-1.0. Weekend -3.1/-2.0 vs weekday -3.2/-1.1.
DOW: only Thu short is pooled-positive (+0.5 pp, z=1.9) but 2/5 years — exactly what one lucky cell out of 28 looks like.
**Verdict: NO time-of-day, session, weekend or DOW effect survives 1h fees (median 0.044R ~= 8 bps of price). Dead.**

## 3. Funding-time effects (1h, C_funding_slot==0 close = bar right after payment)

Label edges at slot0 vs other slots: essentially identical (long -2.8 vs -3.2 pp; short -1.6 vs -1.3 pp). No slot0 effect per se.
Extreme funding at slot0: extPOS (F_rate>0.0005, n=2410) and extNEG (<-0.0002, n=1077) — 1:1 label edges still negative
both sides (best: extPOS long -0.7 pp, extNEG short -0.8 pp); per-year label edges flip sign. No tradeable label rule.

Event study, raw forward returns from next-bar-open entry (bps), vs normal-funding slot0 (fwd1/4/8 = 0/+1/+7):
- after **extPOS** payment: fwd1 **+18.8** (t=5.2 vs normal), fwd4 +5.5, fwd8 +21.2. Per-year fwd1: +14/+19/na/0/+34 —
  positive in every year with n>100 (2022 had zero extPOS events; 2023 n=34). Direction is a **bounce UP** (short-squeeze /
  relief after longs pay), i.e. *contrarian* to the naive "crowded-long -> short" read.
- after **extNEG** payment: fwd8 +33 bps (t=1.9, ns); per-year +63/+237/-13/+51/+101 but n=73 and n=22 in 2021/2024.
**Verdict: the extPOS 1h bounce is the most statistically consistent raw effect found (+15-30 bps, 3-4/4 usable years),
but it is ~2-4x round-trip taker fees, event count is bursty (63% of events in 2021), and it does NOT survive the
ATR-stop label framework. Interesting microstructure note; not a rule. extNEG: underpowered, no call.**

## 4. Turn-of-month (dom in {28..31,1,2})

Pooled looks seductive: 4h long 2:1 TOM edge +5.3 pp (z=11.9) vs -1.4 rest; shorts badly negative at TOM (-6.8 pp).
Per-year long TOM (1h, 2:1 edge): 2020 **+6.7** | 2021 **+10.0** | 2022 -3.7 | 2023 -1.0 | 2024 **-6.8** — monotone decay;
1:1 identical pattern (+4.2/+6.1/-2.1/-2.2/-6.9). Raw fwd-24h dom 29-31 per-year: +143/+249/+24/-1/-69 bps — same decay.
**Verdict: pure 2020-21 bull-market artifact that has inverted by 2024. Reject despite huge pooled z. (Note the contrast
with dom 25-28, which held in relative terms every year — the "1,2,28-31" window is the part that died.)**

## 5. Multiple-testing accounting

Tests run: ~48 hour cells + 14 DOW + 10 sessions/weekend + 10 dom buckets + ~40 per-year/per-symbol dom cells +
~20 funding cells + 8 TOM = **~150 comparisons**. At |z|>2 we'd expect **~7-8 false positives by chance alone**;
at |z|>3, ~0.4. Additionally pooled z's are inflated ~sqrt(2-4)x by cross-symbol correlation of the 6 perps.
Rule applied: nothing is called real unless the sign holds in >=4/5 years AND in the raw-return cross-check.
Only dom 25-28 relative tilt and the extPOS-funding 1h bounce clear that bar; neither clears fees as a standalone system.

## Rule candidates & verdicts

| # | Rule (exact condition) | Pooled | Per-year | Verdict |
|---|---|---|---|---|
| R1 | SHORT 2:1 when C_dom in [7,10] (4h) | +4.2 pp, z=7.9 | +/-: -1.7,+2.7,+16.1,+8.2,**-6.1** | **REJECT** — 2022-23 regime fluke, dead 2024, absent in BTC |
| R2 | LONG 2:1 when C_dom in [25,28] (4h) | +6.7 pp, z=12.8 | +10.4,+15.5,+2.9,+5.4,-0.2 | **WEAK KEEP as filter only** (never standalone): relative tilt 5/5 yrs, raw fwd24 +10..+85 bps 5/5 yrs; absolute edge ~0 in 2024 |
| R3 | Any hour-of-day / DOW / session / weekend rule (1h 1:1) | all edges < 0 | best 3/5 yrs | **REJECT** — nothing beats fees |
| R4 | LONG 1 bar after funding payment when F_rate > 0.0005 (raw, not labeled) | +19 bps fwd1, t=5.2 | +14/+19/na/0/+34 | **NOTE, don't trade** — real-looking but ~fee-sized, bursty event supply, fails label framework |
| R5 | TOM long, C_dom in {28..31,1,2} | +5.3 pp, z=11.9 (4h) | +6.7,+10.0,-3.7,-1.0,-6.8 | **REJECT** — bull-era artifact, inverted by 2024 |

Bottom line: calendar/time effects in this universe are almost entirely regime artifacts amplified by pooling.
The only survivors are a mild late-month (25-28) long tilt usable as a confluence filter, and a contrarian post-extreme-funding
bounce too small to trade. Expected-false-positive budget (~7-8) comfortably explains everything else flagged by the screen.
