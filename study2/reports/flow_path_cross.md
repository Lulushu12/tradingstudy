# Flow / Path / Cross-Asset Screen (TRAIN only: 2020-01-01 .. 2024-12-31)

Data: matrix_1h (250,530 rows) & matrix_4h (62,634 rows), 6 perps pooled. Net R = (rr if y==1 else -1) - feeR.
Baselines (netR/trade): 1h long 1:1 -0.070, long 2:1 -0.071, short 1:1 -0.033, short 2:1 -0.030.
4h: long 1:1 -0.048, long 2:1 -0.010, short 1:1 +0.001, short 2:1 -0.052.

## 1. Order flow

**O_flow_div** (= z(4-bar price ret) - z(4-bar net flow); positive = price up without flow).
Decile tables are near-flat. 1h top decile improves short 1:1 from -0.033 to -0.006 (n=25k) but never goes
positive; fdiv>2 short 2:1 is -0.08/-0.11 (1h/4h). On 4h, fdiv>2 LONG 2:1 is +0.05 — the opposite of the
divergence-fade hypothesis. **Verdict: no tradeable edge; "price up + flow down -> short" rejected net of fees.**

**O_cvd_24h x T_ret_24h quadrants** — the disagreement quadrant cvd+ & ret24- (net taker buying into a
falling price, i.e. absorption/accumulation) is the only positive one:
- 1h long 2:1: +0.086 (n=8,910); top-quintile cvd & ret-: +0.113 (n=6,591). 4h long 2:1: +0.071 (n=2,206).
- Per-year (1h, 2:1): 2020 +0.35, 2021 -0.02, 2022 +0.05, 2023 -0.10, 2024 +0.05. All 6 symbols positive at 2:1.
- Mirror quadrant cvd- & ret+ mildly favors shorts (1h -0.009 vs -0.033 base) but never positive.
**Verdict: real but front-loaded in 2020; only the 2:1 long side survives; 2 of 5 years negative.**

**Whale bars** (O_whale = ats_z>2 & vol_z>1): follow-through is directional, not contrarian.
- 4h whale & up-bar -> long 2:1: **+0.126** (n=989); years: +0.28/+0.10/-0.19/+0.16/+0.29; BTC +0.31, ETH +0.31,
  DOT -0.19. Whale & down-bar -> short is ~flat (+0.03 at 1:1, negative at 2:1). 1h version weak (+0.025).
- Shorting whale bars is consistently bad (-0.10 to -0.18 at 2:1). ats_z>2 alone (no volume filter): no edge.
**Verdict: 4h whale prints in an up bar = bullish continuation; usable, one bad year (2022).**

## 2. Stop-hunt / sweeps

- **P_sweep_low==1 -> long (reclaim): REJECTED.** 1h long 1:1 -0.096, 2:1 -0.104 (n=9,930) — *worse* than
  baseline; 4h -0.049/-0.014. Trend filter doesn't help (uptrend -0.095, downtrend -0.097 at 1h).
  Breadth conditioning makes it worse (sweepL & breadth>=0.5: -0.20 to -0.24). A swept 24h low mostly keeps going.
- **P_sweep_high==1 -> short:** only works against trend. sweepH & ema200_dist<=0: 4h short 1:1 +0.049
  (n=2,701; years +0.02/+0.02/+0.18/+0.03/-0.10; all 6 syms >=0), 1h +0.006. With-trend (above EMA200) it loses.
**Verdict: liquidity-grab-reclaim long is a myth in this data; sweep-high fade is a modest, 2022-heavy
downtrend-only edge — borderline.**

## 3. Cross-asset lead-lag (alts only, sym != BTCUSDT)

**X_btc_lead1 threshold sweep (long 2:1 netR, 1h):** >0.3%: -0.025 | >0.5%: +0.020 | >1.0%: +0.046 | >1.5%: **+0.133**.
Monotone in threshold — BTC's last-bar move spills over to alts as *continuation*, and the edge is long-only:
after big BTC down bars, alt shorts still lose (lead<-1.5% short 2:1: -0.106) while alt longs are ~+0.07
(bounce). 4h confirms: lead>1.5% long 2:1 +0.110 (n=4,573).
- Best rule 1h lead>1.5% long 2:1 (n=4,204): years +0.10/+0.18/+0.07/-0.01/+0.20; **all 5 alts positive**
  (DOT +0.14, ETH +0.16, LINK +0.09, SOL +0.15, XRP +0.13). Most stable finding in the study.

**X_breadth extremes:** no edge either way. breadth==1 alt short 2:1 -0.004 (1h) / +0.018 4h 1:1; breadth==0
long is negative. Full-universe agreement predicts neither continuation nor reversal net of fees.

**X_rs_btc_z extremes — lagging alts catch up:** rs_z<-2 long 2:1: 1h +0.059, **4h +0.169** (n=1,092;
years +0.52/+0.22/-0.18/+0.14/+0.38). Sharper conditioned version rs_z<-1.5 & BTC24h>+2% long 2:1:
4h +0.184 (n=821), 1h +0.089 — but per-symbol is split (XRP/ETH great, DOT/SOL negative).
Shorting the laggard ("keeps lagging") is the worst cell in the study: -0.13 to -0.21 at 2:1.
Shorting extended alts (rs_z>2) also loses. **Verdict: catch-up long, not momentum-lag short; 2022 is the
exception year (laggards kept bleeding in the bear).**

## 4. Non-overlapping re-check (1 concurrent trade/symbol, occupied until barrier resolution from klines)

| Rule | TF | trades | tr/mo | netR/trade | totalR | med hold |
|---|---|---|---|---|---|---|
| **A: alt long 2:1 when X_btc_lead1>+1.5%** | 1h | 2,436 | 40.6 | **+0.109** | +266 | 11h |
| **B: long 2:1 on O_whale==1 & up bar** | 4h | 684 | 11.4 | **+0.099** | +68 | 24h |
| (alt B') rs_z<-2 catch-up long 2:1 | 4h | 446 | 7.4 | +0.085 | +38 | 32h |
| (alt B'') rs_z<-1.5 & BTC24h>2% long 2:1 | 4h | 318 | 5.3 | +0.121 | +38 | 32h |

Rule A per-year after de-overlap: 2020 +0.10, 2021 +0.19, 2022 +0.05, 2023 -0.10, 2024 +0.16; all 5 alts
positive. Rule B: 2020 +0.39, 2021 -0.02, 2022 -0.14, 2023 +0.13, 2024 +0.19; DOT is the weak symbol.

## Verdicts

1. **BEST: BTC-lead momentum long on alts** (1h, X_btc_lead1>+0.015, long 2:1). +0.11R/trade de-overlapped,
   ~41 trades/mo, positive 4/5 years and 5/5 symbols. Continuation, not mean reversion; long-side only.
2. **SECOND: 4h whale up-bar long 2:1** (+0.10R de-overlapped, ~11 tr/mo) — genuine but 2021-22 flat/negative.
3. Supporting: cvd+/price-down accumulation long (2:1) and lagging-alt catch-up long are real but choppier
   (both fail in 2022-23 stretches); consider as filters rather than standalone rules.
4. Rejected: O_flow_div fades, sweep-low reclaim longs, breadth-extreme trades, and *all* short-side variants
   of the above (short edge never exceeded fees).
5. Caveats: thresholds picked on train (mild selection bias); 2020's outsized vol inflates several means;
   fee/slippage beyond feeR untested; label ties at 1:1/2:1 resolved by the matrix builder, not re-verified.
