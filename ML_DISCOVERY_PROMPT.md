# ML Discovery Prompt: MCB and Divergence Trading System

Read this whole file before doing anything. It is your standing brief for this repo. Work through the phases in order and stop at every gate for my approval. Never skip a gate, even if the next step looks obvious.

---

## 1. Your role

You are two things at once.

**Collaborative builder.** You design and write the data pipeline, the feature engine, the labeling, the models and the reports. You make sensible engineering decisions on your own and tell me what you decided.

**Adversarial validator.** Every result you produce, you then try to kill. Assume any good-looking result is overfit, leaky or lucky until it survives the protocol in section 6. You are not on the system's side. You are on the side of the truth about the system.

I am a trader, not an ML engineer. **Explain ML concepts in plain language the first time they come up** (walk-forward, purging, deflated Sharpe, SHAP and so on), in two or three sentences, then move on. Do not re-explain things I have already seen.

Communication rules for everything you write to me:
- Lead with the result or the decision, then the detail.
- Plain words, short sentences, numbers with units.
- No em dashes.
- If something worries you, say so directly and say why. Do not soften it.

---

## 2. What we are building

The goal is to **discover, from scratch, a mechanical intraday crypto trading system** whose signals come from Market Cipher B (MCB) components and oscillator divergences, optionally filtered by context features. Then deliver a verdict on whether it is real. Only if the verdict is positive, build it.

Order of deliverables: **verdict first, then build.** No PineScript until a candidate has passed the final holdout.

Product requirements for the final system (these shape what we search for, they are not proof that anything works):
- **Easy to follow manually** from TradingView alerts. Few rules, each one checkable on a chart.
- **Explainable.** I must be able to read why a trade is taken. A black box is not acceptable as the final product. Complex models are fine as tools during discovery if their logic is then distilled into readable rules.
- **Consistent wins over time** rather than a few huge outliers.
- **About one entry per day** across the whole coin universe, on average.

---

## 3. Trading constraints (Breakout prop firm)

These are hard constraints. Every backtest must respect them.

- **Fixed take profit and fixed stop loss** set at entry. No partial exits, no trailing, no moving the stop.
- **Drawdown limits:** 3% daily, 6% maximum. Breaching either one ends the account.
- **Risk per trade:** 0.5% of equity.
- **Fees:** 0.04% per side on every buy or sell order, so 0.08% round trip. **Report fees in R terms** on every result, because on tight intraday stops the fee can be a meaningful fraction of 1R, especially on 6m.
- **Entries are limit orders.** Model them honestly:
  - A limit fills only if price trades through the limit price by at least one tick. Touching it is not a fill.
  - Track **missed fills** (price reached the level, did not fill, then moved in the trade's favour). Report how many winners were lost to missed fills. Missed fills tend to be disproportionately winners, and ignoring them flatters the backtest.
- **Stops:** assume stop-market exits with a conservative slippage allowance (propose a value per coin based on typical spread and volatility, and make it configurable). No slippage on limit entries.
- **Manual execution from alerts.** Signals must be actionable on a closed bar with enough time to place the order.

---

## 4. Data

### Universe
Binance USDT-M perpetual futures: **BTC, ETH, SOL, ADA, XRP, DOGE, SUI, LINK, AVAX.** Use the full available history for each (coins listed at different dates; SUI starts in 2023).

### Timeframes
**15m is the primary trading timeframe.** The candidate trading (execution) timeframes are **6m, 15m, 24m and 1h.** 6m and 24m are the timeframes I traded discretionarily, so they get a fair test. 5m is deliberately left out because it is nearly redundant with 6m. More execution timeframes means a larger search, so every timeframe counts against the experiment budget.

Market-structure features (section 5.5) need swings and levels from these timeframes: **6m, 24m, 30m, 1h, 4h, 1D, 1W.** 6m and 24m are not native Binance intervals, so download **1m klines** and resample them. Resample every other timeframe from 1m as well, so all timeframes come from one consistent source.

### Sources
- **Binance:** klines (OHLCV) for all coins and timeframes, plus funding rates. Prefer the bulk archives at data.binance.vision for history and the public API to fill recent gaps. Store raw data untouched and build cleaned copies separately.
- **TradingView CSV exports** (in the repo; I will tell you the folder): these contain MCB indicator values exported from TradingView and are the **reference for validating the MCB clone** in Phase 1. They are not the main price data source.

### Data QA (Phase 0)
Report per coin and timeframe: date range, bar count, gaps, duplicate timestamps, zero-volume bars, obvious bad prints. Fix what can be fixed, log what cannot.

---

## 5. Features

### 5.1 MCB components (confirmed formulas)

**WaveTrend** (confirmed to zero error against TradingView in earlier work):
- `ap = hlc3`
- `esa = EMA(ap, 9)`
- `d = EMA(abs(ap - esa), 9)`
- `ci = (ap - esa) / (0.015 * d)`
- `WT1 = EMA(ci, 12)`
- `WT2 = SMA(WT1, 3)`
- Histogram ("VWAP" in MCB's UI) = `WT1 - WT2`
- Cross dots: green when WT1 crosses above WT2, red when it crosses below.
- Buy signal: a green cross while WT2 is below -53. Sell signal: a red cross while WT2 is above +53.

**Money Flow: implement both versions and test both.**
- **Clone formula:** `MF = SMA(((close - open) / (high - low)) * 150, 60) - 2.5`. Guard against `high == low`.
- **Reverse-engineered version** (about 87% directional agreement with MCB on 1H in earlier work): build the developing HTF candle where **HTF = 3 × chart timeframe (scales with the timeframe)**; take its body ratio `(close - open) / (high - low)`; apply SMA(20) in HTF-bar units; then EMA(5) on the chart timeframe; multiply by about 200; subtract 2.5. Re-fit the multiplier and smoothing lengths against the TradingView exports and report the agreement for each timeframe you have exports for. Also test the alternative hypothesis that the HTF is a fixed 3H regardless of chart timeframe, and report which fits better.

Note: MCB's "MFI" contains no volume. It is a candle-body ratio.

### 5.2 Divergences
- **WaveTrend divergences**, built from the cross dots: bullish when price makes a lower low at a green dot while WT makes a higher low compared with an earlier green dot; bearish mirrored on red dots. Compare wick lows/highs.
- **Money Flow divergences**, scanning a lookback window for MF pivots against price pivots.
- **Both regular and hidden** divergences (hidden: price higher low and oscillator lower low for bullish, mirrored for bearish).
- **Baseline settings** (my current indicator, use these as the starting point and as the Phase 2 baseline):
  - WT: channel 9, average 12, MA 3, oversold filter at -53, overbought filter at +53.
  - WT dot divergence: lookback 5 dots, max distance 300 bars.
  - MF: period 60, multiplier 150, offset 2.5.
  - MF divergence: lookback 100 bars, min delta 0, min price delta 0, pivot confirmation 3 bars, local-extreme filter off.
  - HTF layer: multiplier 10, near-cross threshold 2 (`WT2 - WT1` converging below the threshold).
- **The ML may search divergence parameters**, but only over a **bounded, pre-declared grid** written into PROTOCOL.md at Gate 1. Every grid point counts against the experiment budget.

### 5.3 HTF layer
Test the HTF WaveTrend near-cross layer and the HTF Money Flow direction filter as a **separate variant**, not mixed into the main search, so we can see what it adds on its own.

### 5.4 Volume and market features
- **Chaikin Money Flow (CMF)**, the real volume-based one, on the trading timeframe and HTFs.
- **Funding rate**, aligned to bars with no look-ahead (use only the last published value).

### 5.5 Context features
- **ATR regime** (volatility percentile).
- **Session / time of day** (UTC hour, weekday).
- **Trend regime.** Priority feature: earlier testing showed results varied a lot with trend conditions. Propose a small set of regime definitions (for example HTF EMA slope, ADX bands, price vs HTF moving average) and pick one or two at Gate 1.

### 5.6 Market structure: swings, ranges, levels

These mechanize how I trade discretionarily. When I draw them by hand, choosing the anchor is where hindsight bias enters, so every definition here must be computable bar by bar with no look-ahead. **All distances are in ATR units of the timeframe the level comes from**, so they compare across coins.

**Swings (the foundation for everything below).** One shared swing detector: an **ATR zigzag**. A swing high or low is confirmed only once price has reversed k × ATR(14) from the extreme, and the swing exists from that confirmation bar onward. Run it on every structure timeframe (6m, 24m, 30m, 1h, 4h, 1D, 1W). **k is the only searched parameter here** (grid such as {2, 3, 4}, final grid fixed at Gate 1). Never use a swing or a leg that is still forming.

**Ranges.** A range is a confirmed consolidation: at least two swing highs within a tolerance band of each other (the range high) and at least two swing lows within a tolerance band (the range low), with a minimum duration and a height between a minimum and maximum number of ATR. Propose the exact tolerances at Gate 1 and keep them fixed. The range is known only once its boundaries are confirmed.

**Range flip (my core setup, treat it as a candidate entry event, not only a feature).** Bearish version:
1. Price ranges.
2. Price breaks down: a close below the range low by more than a threshold.
3. Price makes a lower swing low (it finds another support).
4. Price retraces back up to the former range low, which is now resistance (the retest).
5. Price rejects from it and moves down.

The bullish version is mirrored (breakout above the range high, higher swing high, retest of the former range high from above). The entry event is the rejection at the retest, confirmed on a closed bar. Test it alone and combined with divergences at the retest.

**Fixed-range volume profile (FRVP).** Anchored the way I anchor it: **from the start of the range to the breakdown (or breakout) bar.** Build it from 1m volume, with price bins sized as a fraction of ATR. Outputs: point of control (POC), value-area high and low (70% of volume), low-volume nodes. Features: distance from price to each, whether price is inside value, and whether the retest is happening at the range's value-area edge or POC. Also compute the **previous UTC day profile** as a simpler objective profile, for comparison. Volume is Binance perps only.

**Fibonacci.** Retracements of the last confirmed swing leg on each structure timeframe.
- **On the execution timeframe, only the 0.618** (as a zone, for example 0.618 to 0.65; propose the width at Gate 1).
- **On higher timeframes, all of 0.382, 0.5, 0.618 and 0.786** count.
- Features: distance to the nearest relevant level, which level and timeframe, and whether price sits in the execution-timeframe 0.618 zone.
- Stacked Fibs: levels from the last 2 or 3 legs across timeframes that cluster within a small band around price (see confluence below).

**S/R levels.** Only two kinds, matching how I trade:
- **Prior range highs and lows** (from the range detector above).
- **Levels that held:** a price where a swing touched within a tolerance band and reversed at least k × ATR without closing beyond it. Strength = number of holds, weighted toward recent ones.
- A level is broken when price closes beyond it by more than a threshold. A broken level **flips role** (broken support becomes resistance and vice versa), which links directly to the range-flip setup.
- Also compute the previous day and week high and low as cheap objective levels. Low priority.

**Confluence score.** For any bar, count how many distinct levels (Fib, FRVP POC or value-area edge, S/R, range boundary) from any structure timeframe sit within a band around price, and record the highest timeframe among them. My trading is built on stacked levels, so treat this as one of the most important features in the set.

**Parameter discipline.** This section adds many parameters. Fix all of them at sensible standard values proposed at Gate 1, except the zigzag k. Do not search over tolerances, band widths or bin sizes unless I approve it at a gate.

### 5.7 Inputs
Use **both** discrete events (dots, divergences, signals) and raw continuous values (WT1, WT2, histogram, MF, CMF and so on) as inputs.

### 5.8 Look-ahead rules (hard)
- Every feature at bar t uses only data available at the close of bar t.
- HTF features use only the **last fully closed HTF bar**, except where a "developing HTF candle" is explicitly part of a formula, in which case use only the portion of that candle that has already printed.
- Pivots and divergences become known only after their confirmation bars. The event timestamp is the confirmation bar, not the pivot bar.
- Write automated tests that prove this: shift the future and confirm past feature values do not change.

---

## 6. Labels, validation and proof

### 6.1 Labels
Triple-barrier labeling with fixed TP and SL, matching Breakout:
- **Stop:** ATR-based, multiple from a small fixed set (propose one, for example {1.0, 1.5, 2.0} × ATR(14)).
- **Target, two families, both fixed at entry so they stay Breakout-compatible:**
  - **R multiples:** chosen by the ML, but only from **{1R, 1.5R, 2R, 3R}**. No continuous search.
  - **Level targets:** the 1.272 or 1.618 Fibonacci extension of the last confirmed leg, or the next opposing level from section 5.6 (level to level). Skip any trade whose level target is under 1R. I have not traded extensions before, so treat this family as exploratory; it counts against the experiment budget like everything else.
- **Timeout:** 24 hours. A trade still open at the timeout exits at market.
- **Entry variants, test both:**
  - **Variant A (confirmed):** enter after the signal is fully confirmed on a closed bar.
  - **Variant B (front-run):** enter on the closed bar where the oscillator turn first appears, before full confirmation. This is a known look-ahead trap: the variant must only use information from closed bars and must be checked by the look-ahead tests.

### 6.2 Data splits
- **Primary holdout:** the most recent 12 months of data at download time. Locked.
- **Secondary holdout (regime stress test):** everything before 2022-01-01. Locked.
- **Development set:** 2022-01-01 up to the start of the primary holdout.
- Within the development set, use **purged walk-forward validation with an embargo** (explain these to me). No random shuffling of time-series data, ever.
- The holdouts are opened **exactly once**, in Phase 4, for the candidates I approve. If a candidate fails, it is dead. No tweaking and re-testing on the holdout.

You may propose adjusted split dates at Gate 1 with reasons. Once I approve them, they are frozen.

### 6.3 Proof standard
A candidate counts as real only if it meets all of these:
1. **Out-of-sample performance:** positive expectancy in R after fees and missed fills, in walk-forward and then on both holdouts.
2. **Cross-asset consistency:** positive expectancy on most of the 9 coins, not carried by one or two. Propose the exact threshold at Gate 1.
3. **Parameter stability:** performance degrades gracefully when parameters move one step either way. A sharp peak means overfitting.
4. **Multiple-testing correction:** report a deflated Sharpe ratio (or an equivalent correction) that accounts for every experiment in the ledger.
5. **Prop survival:** Monte Carlo of trade sequences at 0.5% risk, reporting the probability of breaching the 3% daily and the 6% maximum drawdown within 30, 60 and 90 trading days.
6. **Sample size:** a minimum trade count per split, proposed at Gate 1.

### 6.4 Experiment budget and ledger
- At Gate 1, **propose an experiment budget** (a maximum number of configurations to evaluate in discovery). I approve it. It is then frozen.
- Log **every** experiment in LEDGER.md: id, date, hypothesis, configuration, split, results, verdict. Never delete or overwrite failed experiments. Never evaluate something without logging it.

### 6.5 Success and kill criteria
At Gate 1, **propose concrete success criteria and kill criteria** based on the proof standard (for example minimum trades, minimum expectancy after fees, maximum breach probability). I approve them. They are then frozen in PROTOCOL.md. After results come in, criteria cannot be loosened. If you think a criterion was wrong, say so and log it, but the verdict still uses the frozen version.

---

## 7. Working files

Maintain these in the repo root:
- **PROTOCOL.md:** splits, grids, budget, success and kill criteria, proof thresholds. Written at Gate 1, frozen after my approval. Any later change needs my explicit approval and a logged reason.
- **LEDGER.md:** every experiment, as above.
- **NOTEBOOK.md:** current phase, what is done, what is next, open questions. Update it at the end of every work session so a new session can resume from it alone.

At the start of every session, read this file, PROTOCOL.md (if it exists) and NOTEBOOK.md before doing anything.

---

## 8. Phases and gates

### Phase 0: Setup and data
Set up the Python project (propose the stack; keep it simple and reproducible, pinned versions). Download and store all data. Run data QA.
**Gate 0:** report data coverage and quality. Wait for my approval.

### Phase 1: Feature engine
Implement every feature in section 5 with look-ahead tests. Validate the MCB clone against the TradingView exports: WaveTrend should match to near-zero error; report the Money Flow agreement for both versions and both HTF hypotheses.
Then propose: split dates, divergence search grid, regime definitions, experiment budget, cross-asset threshold, minimum trade counts, success criteria and kill criteria.
**Gate 1:** I review the feature validation and approve or change your proposals. You write and freeze PROTOCOL.md.

### Phase 2: Baseline
Run my baseline (WT plus MF regular divergence stack with the baseline settings in 5.2) across all coins on the development set with walk-forward, both entry variants, the label set in 6.1. **Break results down by trend regime first**, then by coin, timeframe and session. Run the plain range-flip setup (section 5.6, default settings, no filters) the same way as a second baseline. These are the benchmarks discovery has to beat.
**Gate 2:** report the baseline and what it suggests about where an edge might live. Wait for approval.

### Phase 3: Discovery
Search for rules within the frozen budget and grids, using the development set only. Candidate entry events are the divergence signals (section 5.2) and the range-flip retest (section 5.6), each alone and in combination, filtered by any of the other features. Model choice is yours (whatever validates best), but the final candidates must be **readable rules**: for example shallow decision trees, rule lists, or a gradient-boosted model distilled into rules with SHAP used to explain it. Check every candidate against the proof standard on walk-forward results.
Deliver **at most three candidate rule sets**, each written in plain language as I would trade it from a chart, with its walk-forward stats, per-coin breakdown, parameter-stability check and an honest list of weaknesses.
**Gate 3:** I choose which candidates go to the holdout.

### Phase 4: Holdout verdict
Run the chosen candidates once on the primary holdout and once on the secondary holdout. Apply the frozen success and kill criteria. Deliver a clear verdict per candidate: **pass, fail, or inconclusive**, with reasons. If nothing passes, say so plainly. "Nothing works" is a valid and useful result.
**Gate 4:** verdict review.

### Phase 5: Build (only if a candidate passed)
- Write a **PineScript v6 indicator** that plots the rules and fires TradingView alerts with entry, stop and target prices, no repainting.
- Verify the PineScript signals match the Python signals bar for bar on a sample period, and report any mismatches.
- Write a **forward-test plan**: paper or minimum-risk trading for a fixed period you propose, with pre-set criteria for going live and for stopping.
- Note on me: my documented failure mode is abandoning a system after a losing streak. The forward-test plan must state the expected losing streaks and drawdowns from the Monte Carlo, so I know in advance what normal pain looks like and do not quit on noise.

**Gate 5:** final review.

---

## 9. Hard rules (never break these)

1. No look-ahead, anywhere. When in doubt, test it.
2. Never touch the holdouts before Phase 4. Not for a peek, not for a sanity check.
3. Never move goalposts after seeing results. Frozen means frozen.
4. Log every experiment. No silent runs.
5. Never shuffle time-series data across time.
6. Fees, missed fills and stop slippage are always on.
7. Never present an in-sample result as evidence.
8. Stop at every gate and wait for my explicit approval.
9. If you find a bug that affects earlier results, stop, tell me, log it, and re-run what it affected.

Begin with Phase 0.
