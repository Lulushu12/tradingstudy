# Outside-the-Box Feature Study — Findings

Request: stop mining chart patterns everyone can see (and arbitrage away); hunt
features that are NOT already priced in. Universe expanded to 6 perps:
BTC, ETH, XRP, SOL, LINK, DOT. Full ML allowed. Original targets back on the
table: 60% @1:1, 50% @2:1, 10%/mo @ <=6% max DD.

Data: Binance UM-futures archive (data.binance.vision), 2020-01 -> 2026-07:
klines 5m/15m/1h/4h **with taker-buy volume and trade counts** (order flow
TradingView never shows), funding rates, premium index (perp basis), and — from
2022-01 — open interest + top-trader/global long-short ratios at 5-min
resolution. All features strictly causal; labels are triple-barrier
(stop 1.5xATR14, target 1:1 or 2:1, entry next bar open, 5m-path collision
resolution, loss on ambiguity); fees 0.08% RT included in every number.
Protocol: everything developed on pre-2025; 2025-01+ is a locked holdout,
looked at ONCE per pre-registered candidate.

## Verdict on the original targets

| Target | Achievable? | Best found |
|---|---|---|
| 60% winrate @ 1:1 | **No** | Nothing OOS-stable clears the ~52-54% fee-adjusted breakeven wall at scale |
| 50% winrate @ 2:1 | **No** | Best robust 2:1 books run 39-42% (breakeven ~34-35%) |
| 10%/mo @ <=6% max DD | **No** | Best honest combo: ~1.5%/mo at -6% DD holdout (see below) |

The wall is structural: at 2:1 with 4h ATR stops, breakeven is ~34.5%; the best
genuine signals buy 5-8 points of winrate above that, not 15.

## What is NOT priced in (holdout survivors)

Six rule candidates were frozen on train data and each given ONE look at the
2025+ holdout, plus walk-forward ML models with the threshold frozen on
validation. Survivors:

**1. Crowd-fade short (`glsr_short`) — the discovery of the study.**
When the Binance global long/short account ratio z-score (30d) >= 1.75 —
retail crowded long — short at 2:1 (4h, stop 1.5xATR).
- Train 2022-24: +0.235R/trade, 483 trades. Holdout 2025+: **+0.215R/trade,
  42% WR @2:1, ~15 trades/mo** (t≈2.6). Positive on ALL 6 symbols and 6 of 7
  holdout quarters. Non-overlapping trades, fees in.
- This is positioning data — invisible on a chart, published by the exchange,
  and evidently still not arbitraged flat.

**2. ML 4h short 2:1 (`ml4h_s21`).** LightGBM over all ~70 features,
walk-forward validated, threshold frozen pre-holdout: holdout +0.14R/trade
non-overlapping (~30 trades/mo; +0.21R at bar level). Survives removing all
calendar features (+0.208R bar-level), so it is NOT the day-of-month artifact;
top drivers are positioning + flow + vol-regime interactions. The matching
LONG models are weak OOS (+0.02R non-overlapping) and partly calendar-driven —
distrusted and excluded.

**3. Whale-bar continuation long (`whale_long`).** 4h bar with avg trade size
z>2 AND volume z>1 closing up -> long 2:1. Train +0.110R; holdout **+0.125R,
~9 trades/mo**. Big prints get continuation, not reversal (t≈1.2 — weaker
evidence, but sign-stable train->holdout).

**4. BTC-lead alt momentum (`btclead_alt`).** BTC 1h bar >= +1.5% -> long the
alts 2:1. Train +0.107R; holdout +0.052R at ~23 trades/mo. Halved OOS but
still positive — the lead-lag exists and it is CONTINUATION, not reversion.
1h fees eat much of it.

**Baseline for scale**: the prior study's 4H volume-spike trend rule extends
from BTC to all 6 symbols: +0.165R holdout, positive expectancy on every
symbol (BTC is the WEAKEST in 2025+). ~39 trades/mo pooled.

## Killed by the holdout (reported, not hidden)

- `tlsr_long` (fade top-trader-account shorts): train +0.241R -> holdout
  **-0.061R**. The most "promising" train rule died OOS.
- `rslag_long` (laggard-alt catch-up): +0.071 -> -0.123R.
- `squeeze_long` (negative funding + rising price): +0.221 -> -0.325R (n=26).
- 1h ML: all four targets — no net edge after 1h fee drag (holdout ~0.00R).

## Feature families judged on train alone

- **Calendar**: day-of-month/turn-of-month effects are 2020-23 regime
  artifacts, dead or inverted by 2024. No hour/session/weekend edge clears
  fees. Post-funding-payment bounce after extreme funding is real (+19bps,
  t=5.2) but fee-sized and untradeable in this framework.
- **Funding/basis**: contrarian shorting of extreme positive funding — the
  textbook trade — is DEAD on train (it's a bull-regime proxy). Every fragile
  survivor was long-side around negative funding; none survived the holdout.
- **Sweep/SFP patterns**: "liquidity grab reclaim" longs are NEGATIVE (-0.10R)
  — the retail favorite loses. Price-up-without-flow divergence fades: flat.
- **Overlap honesty**: bar-level screens overstate edges 2-4x; every number
  above marked non-overlapping is one-position-per-symbol sequential.

## Combined portfolio vs the 10%/mo @ 6% DD target

Books are complementary (train monthly-R correlation: glsr_short vs
whale_long -0.49, vs volspike +0.05). Risk weights chosen on train under a
5% train-DD cap, then ONE holdout evaluation:

<!-- FINAL_COMBO -->

## Honest caveats

1. Positioning metrics exist only from 2022 — the star rule has 3 years of
   train, 1.6 of holdout. No 2021-style mania in its training set.
2. The holdout was reused across ~10 pre-registered looks (6 rules + 4 ML
   targets). Mild selection pressure remains; the survivors' margins (t≈2.6
   for glsr_short) tolerate it, the weak ones (btclead, whale) less so.
3. Long/short-ratio data is exchange-published and could change format or be
   discontinued; the edge depends on data Binance chooses to publish.
4. Live L/S ratios must be sampled in real time (the archive is end-of-window);
   assume some slippage vs backtest.
5. All entries are next-bar-open market orders with 0.08% RT fees; no slippage
   beyond fees is modeled (consistent with the prior study).
6. DD is measured on daily exit-accounting equity; intramonth open-trade MTM
   can add transient drawdown (~sum of concurrent open risk).

## Reproduce

`study2/`: fetch.py (Binance archive), build_data.py (parquet), features.py
(causal features), core.py (labels/fees), build_matrix.py, screen.py,
ml.py (walk-forward LightGBM), validate_rules.py (pre-registered holdout),
portfolio.py + combine.py (books, weights, sim). Family deep-dives in
`study2/reports/`.
