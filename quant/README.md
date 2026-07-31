# Trading system search — full rundown

Work done 2026-07-30/31 on `claude/btcusdt-trading-system-fcmxyi`.
`FINDINGS.md` is the detailed running log (855 lines, six parts). This file is
the whole story in one read.

---

## 1. What was asked

The brief evolved over the session. In order:

1. Find a system averaging **>=10%/month** under Breakout 1-Step Classic rules,
   ignoring conventional indicator vocabulary, brute-forcing from the data.
2. Then: is buying a prop evaluation a **positive-EV purchase**?
3. Then: build a **regime filter**, and if that fails, go full ML. Hindsight
   explicitly allowed — show retrospectively what *would* have worked.
4. Then: accept **10% every 1-2 months**, or **100% every 2-4 months** on own
   capital with no venue limits.
5. Then: how does any of this become a **business**?
6. Then: try **NASDAQ-100**, and confirm volume was used.

Constraints fixed at the start: 1-Step Classic (10% target, 6% static drawdown
anchored to starting balance, 3% daily loss resetting 00:30 UTC), semi-automatic
execution (one-bar fill delay plus slippage), universe BTC + ETH + majors.

## 2. The answer, in one table

| Target | Best honest (walk-forward) | Best with full hindsight |
|---|---|---|
| 10%/month, Breakout rules | **1.2-1.5%/mo**, failed its holdout | 6.63%/mo |
| 10% per 1-2 months | no config survived at any risk | median +12.7% per 2mo, 58% of windows |
| 100% per 2-4 months, own capital | **ruin at every risk level 1-15%** | doubles ~half the time, at 67-95% drawdown |
| Prop evaluation as a purchase | **+EV at ~2x the fee**, 65% chance of losing it | — |
| NASDAQ-100 cross-sectional | **Sharpe +0.65**, but decayed to negative post-2021 | — |

Nothing reached 10%/month. One thing did come back genuinely positive
out-of-sample: the NASDAQ cross-sectional book.

## 3. What was built

**Data.** 1-minute Binance USD-M perps for BTC/ETH/SOL/XRP/BNB, 2021-01 to
2026-07, 2.93M bars each, pulled fresh from `data.binance.vision`. Zero
duplicates, zero bad OHLC, zero missing minutes on BTC/ETH/BNB. All higher
timeframes resampled from that 1m series, so stops and targets resolve on the
real intrabar path. Later: 97 Nasdaq-100 names daily 1998-2026 (550k rows) and
NQ=F hourly.

**Engine validation, done before trusting any result.** Random entries at 2:1
with zero costs returned a **33.49% win rate and +0.005R** against a theoretical
fair-game null of 33.33% and 0.000R. Stop-wins-ties and delay-monotonicity both
verified. Every number in this repo rests on that check.

**Holdout quarantine.** TRAIN 2021-2024, TEST 2025 to 2026-06, HOLDOUT
2026-06-22 to 2026-07-29 sealed in code (`data.py` refuses to load it without a
literal unlock string). Design done on BTC only; the other four assets held as a
structural out-of-sample check.

## 4. The arithmetic that governed everything

Cost drag per trade = `(2 x commission + 2 x slippage) / stop_distance_%`.

| Setup | Breakeven WR @2:1 | Edge needed over null | Avg hold |
|---|---|---|---|
| 5m, 1xATR | 58.0% | +25.1pp | 0.5h |
| 15m, 2xATR | 39.6% | +6.5pp | 6.4h |
| 30m, 2xATR | 37.5% | +3.7pp | 12.4h |
| 4h, 2xATR | 34.6% | +1.1pp | 95h |

Cheap costs need wide stops, which need long holds, which cap frequency. High
frequency needs tight stops, which makes costs enormous. **Raw win rates sat on
the martingale null at every timeframe from 5m to 1D** (0.49-0.51 at 1:1,
0.32-0.335 at 2:1).

Monte Carlo said the target required **~0.20R net at ~250-300 trades/month**,
i.e. lifting the 2:1 hit rate from 33.7% to ~43.5%.

## 5. What was tested

**Univariate scan.** 71 causal features built on order flow rather than
oscillators — aggressor imbalance (taker-buy volume: who crossed the spread),
trade-size composition, liquidity texture, intrabar path shape from real 1m
data, clock structure. A causality audit recomputed every feature with the
future deleted and found no leakage. Scanned across 13 configurations, each
against a **family-wise permutation null** (same scan on block-shuffled labels).
Result: essentially nothing cleared the null and then held out of sample. Best
cell anywhere went +0.110R train to **-0.106R test**.

**Template-free predictability — the most informative test.** At 15m, 92 of 497
feature-horizon pairs had |IC| > 0.03 and **95% held their sign out-of-sample**
(coin flip = 50%). Predictability is real. But purged, embargoed walk-forward
ridge gave **negative OOS R-squared at every timeframe and horizon**, and the
decile spreads explain why:

| TF / horizon | Predictable drift | In R | Cost drag | Net |
|---|---|---|---|---|
| 15m / 24 bars | +0.125 ATR | 0.06R | 0.187R | **-0.13R** |
| 30m / 96 bars | +0.147 ATR | 0.07R | 0.124R | **-0.05R** |

**The drift is real and 2-3x smaller than the cost of harvesting it.** That one
sentence explains every dead crypto result.

**Cross-sectional crypto.** Sharpe 0.07 after correcting a weighting bug.

**The one surviving rule.** `vol_spike_cont` (4h bar with trade count >1.8x its
96-bar average, closing with the 96-bar displacement) was positive in-sample,
out-of-sample in time, and on all four assets never used to select it. Pooled
**+0.1426R, 95% CI [+0.040, +0.249]**, n=3391. But every per-year CI contains
zero, and 2023 was +0.008.

**Holdout: FAIL.** Frozen spec, pre-registered criterion, opened once.
Expected +0.143R, got **-0.6135R** with a 9.6% win rate, breaching static
drawdown on 2026-07-17. Diagnosis: BTC moved **+0.04% net across 5.5 weeks**,
path-efficiency 0.000. A trend-continuation rule with no regime filter, in a
market with zero trend.

**Machine learning.** Deep model: +175%/mo in-sample, +0.29%/mo walk-forward.
Then the decisive test — a **shallow** model (8 leaves, depth 3, min_data 2000,
L2=50) that *cannot* memorise individual bars: still **+16.7%/mo IS vs -3.1%/mo
WF**. So the overfitting was never memorisation, it was **regime encoding** —
the model learning which year rewarded what. Trained only on the past it
anti-predicts the future.

**Feature importance predicted the outcome before the walk-forward did.** Crypto
models ranked `since_lo480`, `since_hi480`, `pos480` first — position-in-history,
a calendar. Equity models ranked `vol63`, `amihud21`, `mom126` first — risk-premium
proxies. The first kind cannot transfer; the second partly does.

**NASDAQ-100.** Cross-sectional risk-parity long/short gave **WF Sharpe +0.65
(1d) and +0.68 (5d)**, market-neutral, net of 5bps — the only genuinely positive
out-of-sample result in the study. Volume-only features reached **Sharpe 0.55 at
24.4% maxDD** versus price-only 0.54 at 29.5%, so volume carried as much signal
as price with a smoother ride. But: first half +10.7%/yr, second half +3.2%/yr,
five of the last six years negative; dies above ~22bps cost; Calmar 0.18, so any
leverage reaching 2%/month implies a 100% drawdown.

## 6. Bugs found in my own work

Each initially produced a spectacular and false result. Listed because the
corrections are most of the value here.

1. **Equal-dollar cross-sectional weighting** implicitly shorted the high-vol
   assets (SOL, XRP). Produced Sharpe -2 where the truth was ~0.
2. **Portfolio double-counting** — unioning rules summed R over overlapping
   masks, counting the same trade up to 8 times. Fake "369%/month".
3. **Divide-by-zero ratio** — rules with no drawdown scored 9.2e9.
4. **Coverage** — the "best" rule traded in 14 of 66 months. A system that sits
   out 79% of the calendar cannot deliver a monthly return.
5. **An invalid daily-loss proof.** I capped entries per day at k and sized
   3%/k, claiming a breach was impossible. Wrong: the limit applies to *exits*,
   and trades entered on different days exit on the same one.
6. **NQ path resolution on hourly closes**, ignoring bar highs and lows.
   Undetected stop-outs made the unconditional long side score **+0.1942R**.
   Corrected to true high/low: **-0.0010R**. The entire apparent edge was the bug.

## 7. Why 10%/month is unreachable here

Three independent walls, any one sufficient:

1. **Signal-to-cost.** Genuine predictability exists but the drift is 2-3x
   smaller than the round-trip cost of capturing it. Subtraction, not search.
2. **Return-to-drawdown geometry.** 10%/month against a 6% floor is a Calmar
   near 20-35. The account Monte Carlo shows the mechanism: mean monthly return
   is **flat at 1.2-1.5% across every risk setting** while bust probability
   climbs to 76%. Leverage buys dead accounts, not returns.
3. **The 3% daily loss rule.** With hindsight, the same signal returns +76%/month
   at higher risk — and breaches on day 11. Signals cluster across correlated
   assets, so a bad day closes several losers at once. No risk setting delivers
   both compounding and survival.

## 8. The business model

The per-account return is unattractive; that is the wrong unit. A prop fee is
not capital deployed, it is the price of an option on someone else's balance
sheet.

| True expR | EV per $800 account | ROI on fee | P(lose fee) |
|---|---|---|---|
| -0.015 (no skill) | -$133 | -0.17 | 87% |
| **+0.024 (posterior)** | **+$1,546** | **+1.93** | 65% |
| +0.143 (studied) | +$17,443 | +21.80 | 4% |

The honest edge estimate, blending studied data (+0.1426R, n=3391) with the
failed holdout (-0.6135R, n=52) by inverse variance, is **+0.0238R, 95% CI
[-0.072, +0.119]** — it straddles zero.

Three structural findings:
- **Never run accounts in parallel.** Cross-asset correlation is rho=0.30, so 5
  assets give 2.27 effective independent streams and twenty simultaneous
  accounts are worth three. Twenty sequential accounts are worth twenty.
- **Undersize.** 0.25% risk yields 11x the EV of 1% risk. Busts are absorbing.
- **Bank early.** Withdraw at +2% beats +20% at every edge level tested, because
  the static floor never trails, so holding profit is a bet on surviving long
  enough to build a cushion.

**Kelly is unforgiving.** Half-Kelly at the studied edge (f=3.9%) gives
+23%/month if right — and **-1.3%/month if the truth is +0.024R**, with a 49%
chance of losing half the account. f = 1% is the only sizing positive across the
whole plausible range.

**The number that governs the decision:** distinguishing +0.1426R from +0.024R
needs **1,074 trades, about 21 months**. You cannot know which world you are in
for two years, and the right action differs enormously between them.

**Implied model.** Run prop evaluations *sequentially*, 0.25% risk, 2% heat,
bankroll of 10 fees ($8,000, P(broke) 1.4%). Own capital out, or at f=1%. The
accumulating trade record IS the experiment, and it pays for itself while
running. After ~1,074 trades the edge is measured rather than assumed, and only
then does levering own capital become a decision rather than a coin flip.

## 9. What I would do next

- **Regime filter on fresh quarantined data.** The holdout failure mode is now
  precisely identified (trend-continuation in zero-efficiency chop). Building
  the filter after seeing the holdout would fit to it, so that work needs data
  that does not exist yet.
- **More instruments, cheaper execution.** The only lever that genuinely moved
  the needle was breadth plus cost. That points at Russell 1000 rather than
  Nasdaq-100, and institutional cost structure rather than retail.
- **Resolve the survivorship question** on the equity result with a
  point-in-time universe. The current result cannot separate "bias" from
  "arbitraged away", and they imply different actions.

## 10. Reproduce

```
src/fetch.py        1m crypto data          src/scan.py        univariate + permutation null
src/data.py         loading + holdout lock  src/ic.py          template-free predictability
src/engine.py       1m-path + account rules src/xsec2.py       cross-sectional (risk parity)
src/sanity.py       ENGINE VALIDATION       src/candidate.py   pre-registered rules
src/costmap.py      cost drag by timeframe  src/account.py     account Monte Carlo
src/requirement.py  what 10%/mo demands     src/holdout.py     final holdout (run once)
src/features.py     71 features + audit     src/ml.py          deep model IS vs WF
src/labels.py       per-bar outcomes        src/hifreq2.py     high-frequency + real sim
src/regime.py       regime filter           src/ruleopt2.py    compact rule optimiser
src/payout.py       prop economics          src/business.py    correlation, EV, Kelly
src/kellyrisk.py    edge-mismatch risk      src/eqml.py        NDX cross-sectional ML
src/eqstress.py     survivorship/cost tests src/nqml.py        NQ futures intraday
```

Run `python3 src/sanity.py` first — if the engine validation does not reproduce
33.49% / +0.005R, nothing downstream is meaningful.

Bulk data (`data/raw1m`, `data/labels`, `data/sets`, `data/equity`) is
gitignored; `src/fetch.py` and `src/eqfetch.py` regenerate it.

## 11. Honest closing

Across crypto and equities, spot and futures, cross-sectional and time-series,
univariate scans and gradient boosting, in-sample fits produced 20-80%/month and
walk-forward produced 0-7%/year. The gap was hindsight every time.

The genuine products of this work are: a validated backtest engine, a measured
edge of +0.024R with an honest confidence interval that includes zero, one
positive out-of-sample equity result that has since decayed, a precise diagnosis
of why 10%/month is unreachable under these rules, and a business structure
where being wrong does not end the ability to keep playing.

Past performance is not the issue. The issue is that the edge available here,
measured carefully, is smaller than the cost of collecting it — and no amount of
searching changes a subtraction.
