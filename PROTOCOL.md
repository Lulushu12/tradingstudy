# PROTOCOL

**Status: FROZEN 2026-11-15 (Gate 1 approved by the user).** Any change needs explicit user approval and a logged
reason in the change log at the bottom. Criteria can never be loosened after results exist.

---

## 1. Data and splits
- Source: Binance USDT-M perpetuals, 1m klines (data.binance.vision), all timeframes resampled from 1m. Snapshot 2026-11-15.
- Universe: BTC, ETH, SOL, ADA, XRP, DOGE, SUI, LINK, AVAX.
- **Primary holdout:** 2025-11-15 00:00 UTC to 2026-11-14 23:59 UTC (12 months). Locked.
- **Secondary holdout:** everything before 2022-01-01 (2020-01 to 2021-12; SUI absent). Locked.
- **Development set:** 2022-01-01 to 2025-11-14.
- **Contamination caveat (carried into every verdict):** BTC 2025-01 to 2026-06 was the test set of an earlier systematic
  study that tested WaveTrend signals, and the user traded several of the coins live during the primary holdout period.
  The primary holdout is therefore weaker than a blind holdout on every coin. Holdout verdicts are judged on the
  non-BTC coins; BTC is reported separately.
- **Warm-up (approved):** bars up to 400 days before a split's first evaluated bar may be used to compute indicators and
  structure only. No label, trade or statistic is ever computed on a warm-up bar. For the dev set this uses 2020-11 to
  2021-12 prices from the secondary holdout as warm-up only. Without it, trend regimes are missing for the first ~2
  months of dev and weekly structure has 2 to 8 swings in total.

## 2. Walk-forward validation (development set only)
- Expanding window, 6 test folds: 2023H1, 2023H2, 2024H1, 2024H2, 2025H1, 2025-07-01 to 2025-11-14.
  Fold 1 trains on 2022 only.
- **Purging:** any training trade whose life (signal to exit, at most 1 bar of limit plus 24 h) overlaps the test fold
  is removed. **Embargo:** a 7-day gap between the end of training data and the start of each test fold.
- Every choice (event definition, filters, thresholds, label) is made on the fold's training data only. The
  walk-forward result is the concatenation of the 6 out-of-sample folds.
- The final candidate is the same selection procedure applied to the whole development set. Its rule must be
  (near-)identical to the rule selected in at least 4 of the 6 folds (rule stability).
- No random shuffling across time, ever.

## 3. Execution and account model (always on)
- Signal on a closed execution bar t. **Limit entry at close[t]**, checked on 1m bars from the next minute.
- **Order life:** the limit stays live until (a) it fills, (b) price moves 0.5R in the trade's favour without filling
  (long: 1m high >= limit + 0.5 x stop distance), then it is cancelled, or (c) 24 h pass, then it is cancelled.
  If one 1m bar both trades through the limit and reaches the cancel level, the fill is assumed (the order is exposed).
- **Fill:** only if price trades through the limit by at least one tick. Long: 1m low <= limit - tick.
  Fill price = limit, no slippage.
- **Missed fill:** price touched the limit (long: low <= limit) but never traded through before cancellation or
  expiry. Logged with the outcome the trade would have had if filled at the first touch.
- **Stop:** entry -/+ stop_mult x ATR14 of the execution TF at bar t. Stop-market. Fill = stop price minus slippage.
- **Target:** fixed at entry. Limit order, fills only on trade-through by one tick.
- **Same-minute ambiguity:** if one 1m bar reaches both stop and target, the stop is assumed. In the fill minute only
  the stop is checked.
- **Timeout:** 24 h after the fill, market exit at that minute's close, with slippage.
- **Fees:** 0.04% of notional on every order (entry and exit). Reported in R on every result.
- **Stop slippage per coin** (0.5 x median 1m high-low range, dev period; no order-book data is available):
  BTC 0.03%, ETH 0.04%, XRP 0.05%, ADA 0.06%, DOGE 0.06%, LINK 0.06%, AVAX 0.065%, SOL 0.07%, SUI 0.08%.
  Configurable. Every candidate is also reported at 2x slippage.
- **Tick sizes:** inferred per coin and year from the data (e.g. BTC 0.01 in 2022, 0.1 from 2023; SOL 0.001 to 0.01 in 2025).
- **Risk:** 0.5% of current equity per trade. Size = risk / stop distance.
- **Account rules (Breakout):** daily loss limit 3% of the start-of-day balance, realized P&L only, reset 00:00 UTC.
  Max drawdown 6% static from the starting balance.
- **Risk guards (approved):** at most 1 open position or pending limit per coin; at most 3 open positions
  account-wide (pending limits count toward the 3, so a fill can never create a 4th position); no new entries for the
  rest of the UTC day once realized day P&L reaches -2.0%.

## 4. Labels (triple barrier, Breakout-compatible)
- Stops: {1.5, 2.0} x ATR14. The 1.0 x ATR stop is dropped (median fee 0.14R on 15m, 0.23R on 6m).
  On 6m only the 2.0 x ATR stop is used.
- Targets, R family: {1R, 1.5R, 2R, 3R}.
- Targets, level family (exploratory): 1.272 and 1.618 extension of the most recent confirmed leg in the trade
  direction on the execution TF (long: last up-leg A -> B, target A + e(B - A)); next opposing level (nearest held S/R,
  active range boundary or last broken range boundary beyond entry, from the execution TF and higher structure TFs).
  Trades whose level target is under 1R (or on the wrong side of entry) are skipped.
- Timeout 24 h. Entry variants A (confirmed) and B (front-run) per event definition.

## 5. Event definitions (frozen with this protocol)
- **WaveTrend:** brief 5.1 formulas, validated against real MCB exports (100% cross-dot agreement).
- **Money Flow:** MCB_Clone_v1 formula on Heikin-Ashi candles, no outer EMA:
  SMA((HA close - HA open) / stdev(HA close, 7) x 150, 60) - 2.5. Best match to real MCB (corr 0.99, 95% same sign).
- **WT dot divergence:** dot level = wt2 at the cross bar; price = extreme wick of the dot's wave (since the previous
  opposite dot); compared with up to `lookback_dots` earlier same-colour dots within `max_dist` bars; level filter on the
  current dot (regular), none on hidden. Front-run: first bar in the wave where wt1 turns toward wt2 with the conditions
  already met, using wt2 at that bar as the provisional level.
- **MF divergence:** pivot with `piv` bars each side, known `piv` bars after the pivot; price = extreme over the pivot
  window; compared with earlier pivots within `lookback` bars. Front-run: left-side-only pivot candidate plus a turn.
- **Baseline 1, divergence stack:** WT regular dot divergence + MF regular divergence, same direction, the later within
  11 bars of the earlier. Variant A both confirmed; Variant B one confirmed and the other front-run. Event = later bar.
- **Baseline 2, plain range flip:** execution-TF ranges and flips with the fixed parameters in section 6, k = 3.
  Variant A = rejection bar; Variant B = first touch of the retest zone.
- **HTF layer variant (separate):** Baseline 1 filtered by (i) HTF (10 x TF) WaveTrend near-cross in the trade direction,
  or (ii) HTF Money Flow rising for longs / falling for shorts. Each filter tested on its own.
- **Trend regimes (approved, may be revisited at a gate):** R1 = price vs 4h EMA200 and its 1-day slope (direction); R2 = 4h ADX(14) >= 25 with DI
  direction (trend strength). R3 (1D SMA50) is computed but not used for the regime breakdown.

## 6. Fixed parameters (not searched unless approved at a gate)
- Swings: ATR(14) zigzag of each structure TF; k searched in {2, 3, 4}.
- Ranges: highs within 1.0 ATR, lows within 1.0 ATR, height 2 to 12 ATR, at least 10 bars; breakdown close beyond
  0.25 ATR; retest zone 0.25 ATR; invalidation close 0.5 ATR back inside; expiry 200 bars.
- Held S/R: hold tolerance 0.5 ATR; break close beyond 0.25 ATR; strength half-life 30 days; 12 nearest levels per TF.
- FRVP: range start to breakdown bar, 1m volume, bins 0.1 x ATR of the range TF; value area 70%; LVN = local minimum
  below 25% of POC volume. Previous-UTC-day profile with bins 0.05 x 1D ATR.
- Fibonacci: execution TF 0.618 only (zone 0.618 to 0.65); higher TFs 0.382, 0.5, 0.618, 0.786; last 3 legs.
- Confluence (approved): levels from the execution TF and all higher structure TFs within 0.25 x execution ATR,
  plus a count of distinct level types (Fib, held S/R, range boundary, profile).
- HTF layer: multiplier 10, near-cross threshold 2.

## 7. Search grids (bounded, pre-declared)
- Zigzag k: {2, 3, 4}.
- WT dot divergence: lookback dots {3, 5, 8}; max distance {150, 300} bars; level filter {45, 53, 60}.
- MF divergence: pivot {2, 3, 5}; lookback {50, 100}; min delta {0, 1.5}; min price delta {0, 0.25 ATR}.
- Stack window: {6, 11, 20} bars.
- Execution TFs: 6m, 15m, 24m, 1h.
- Filters: any feature from brief section 5, through readable rules only (decision trees of depth <= 3, or rule lists
  of <= 3 conditions). Thresholds are learned inside each fold's training data.
- Grids are not fully crossed. Each evaluated grid point counts against the budget.

## 8. Experiment budget
- **800 evaluated configurations in total**, Phases 2 and 3 combined. One configuration = one complete specification
  (event definition + parameters + filters + label + variant + TF) whose out-of-sample results are looked at.
  Breakdowns of one configuration (by regime, coin, session) do not count extra; choosing a subset to build a rule does.
- Phase 2 estimate: Baseline 1 98, Baseline 2 98, HTF layer 16 (reference label only) = 212. Discovery: up to 588.
- The deflated Sharpe uses the ledger count at the time of evaluation.

## 9. Success criteria (walk-forward, development set, all must hold)
- S1 net expectancy >= +0.10R per trade after fees, slippage and missed fills.
- S2 profit factor >= 1.20.
- S3 >= 300 out-of-sample trades, >= 25 per fold; average frequency 0.3 to 3 entries per day across the universe.
- S4 positive expectancy in >= 4 of 6 folds.
- S5 positive expectancy on >= 6 of 9 coins and >= 5 of the 8 non-BTC coins; no coin > 35% of total net R.
- S6 every one-step neighbour of each searched parameter keeps expectancy > 0 and >= 50% of the candidate's.
- S7 deflated Sharpe probability >= 0.95.
- S8 prop Monte Carlo (10,000 paths, block bootstrap by day, 0.5% risk, section 3 account rules): probability of
  breaching the 6% max drawdown within 90 trading days <= 10%, and the 3% daily limit within 90 days <= 5%.
  30- and 60-day figures reported too.
- S9 >= 55% of calendar months positive out of sample.
- S10 rule stability (section 2).
- Still positive (S1 relaxed to > 0) at 2x slippage.

## 10. Holdout verdict (Phase 4, each holdout opened exactly once)
- Primary, 8 non-BTC coins: PASS needs net expectancy > 0, >= 100 trades, PF >= 1.05 and one-sided bootstrap
  P(expectancy <= 0) < 0.10.
- Secondary, 7 non-BTC coins (SUI absent): same, with >= 80 trades.
- Verdict: PASS if both pass. FAIL if net expectancy <= 0 on either. INCONCLUSIVE otherwise.
- BTC and the prop Monte Carlo on holdout trades are reported alongside, not used in the verdict.

## 11. Kill criteria
- A candidate failing any of S1 to S10 is not eligible for the holdout.
- If the budget is spent without an eligible candidate, the verdict is "no system found". No budget extension
  without explicit user approval, logged as a protocol change.
- After results exist, criteria cannot be loosened. A criterion believed wrong is logged; the verdict still uses it.

## Amendment 1 (Gate 2, 2026-11-16, approved by the user). Overrides sections 4, 5 and 7 where they conflict.
Reason: after the Phase 2 baselines (all negative, gross R about zero), the user corrected definitions that were
Claude's interpretations, before any discovery run. The 212 Phase 2 results stay in the ledger unchanged.

- **Execution TFs:** 15m, 24m, 1h. 6m is dropped from discovery (negative even before fees in every baseline).
- **WT dot divergence (regular):** the level filter applies to the ANCHOR (earlier) dot: bullish anchor wt2 <= -53,
  bearish anchor >= +53. The signal (new) dot can be anywhere. Everything else as section 5.
- **MF divergence (old FROZEN_SPEC / MCB_Clone_v1.pine f_findDivs logic):** pivot = 5-bar fractal on MF (MF at bar p
  strictly lower than the 2 bars before and the 2 bars after; mirrored for highs), known at p + 2. A pivot counts only
  if MF <= -2.5 (bearish >= +2.5). Each counting pivot is compared with the previous counting pivot only.
  Price at a pivot = lowest low (highest high) over bars p-2..p. Regular bullish: price lower AND MF higher.
  Hidden mirrored (feature only). The Money Flow formula stays the MCB-matched Heikin-Ashi version (section 5).
- **Divergence stack, Variant A:** WT regular dot divergence + MF regular divergence, same direction, within 11 bars
  between their confirmation bars; entry on the later confirmation.
- **Divergence stack, Variant B (old FROZEN_SPEC front-run):** leg 1 = either oscillator's regular divergence, fully
  confirmed. Leg 2 = the other oscillator, at the first bar t where ALL hold: (a) its reference (previous counting MF
  pivot, or previous green/red dot beyond -53/+53) is no older than 50 bars; (b) price has gone beyond the reference
  extreme (lowest low of the last 3 bars below the reference's swing low; MF reference swing low = lowest low of the
  5 bars ending at the reference pivot; WT reference = its wave low); (c) the oscillator is still on the divergent side
  of the reference (MF: mf[t-1] above the reference MF; WT: the lowest wt1 of the current wave above the anchor dot
  level); (d) the oscillator ticked once in the reversal direction (MF: mf[t] > mf[t-1]; WT: wt1[t] > wt1[t-1] while
  wt1 is still below wt2, i.e. before the dot). Level filter on the reference only. Leg 1's pivot (MF pivot bar or WT
  dot bar) is at most 11 bars before t; same bar allowed. One entry per leg-1 event.
  (Adaptation stated for review: the old spec used fractal WT divergences on wt2; with dot divergences the WT
  front-run tick is taken on wt1 before the cross.)
- **Range flip rejection ("respect" rule):** Variant A: a bar that touched the retest zone, whose OPEN and CLOSE are
  both on the correct side of the old level (bearish: open <= level and close < level; wick beyond is allowed), with a
  body in the trade direction. Variant B: the first touch bar whose open and close are both on the correct side (any
  colour).
- **Higher-timeframe ranges:** in addition to same-TF ranges, ranges/breakdown/lower low detected on a range TF
  (1h or 4h) with the retest and rejection timed on a lower execution TF. Pairs: 1h>15m, 4h>15m, 1h>24m, 4h>24m,
  4h>1h. Zone tolerance and invalidation use the range TF's ATR at the breakdown; expiry = 200 range-TF bars.
- **Stops: structure-based, replacing the ATR stops.** Divergence trades: beyond the current swing (long: lowest low
  since the previous red dot, and over the last 13 bars, whichever is lower) plus 0.1 x ATR(exec). Range flips: beyond
  the retest extreme (bearish: highest high from the first touch to the entry bar) plus 0.1 x ATR(exec). A trade whose
  stop is closer than 0.5 x ATR(exec) is skipped. R targets and the 0.5R cancel use this structure R.
- **Labels:** structure stop x {1R, 1.5R, 2R, 3R, fib 1.272, fib 1.618, next level}.
- **Re-run before discovery (counts against the budget):** stack v2 42, same-TF flip v2 42, HTF-range flip 70,
  HTF layer on stack v2 12 = 166. Ledger total 378 of 800; 422 remain for discovery. The deflated Sharpe uses N = 378.

## Phase 3 discovery plan (approved by the user 2026-11-16, declared before any discovery run)
- **Event families:** (1) divergence stack v2; (2) range flips pooled per execution TF (same-TF ranges plus 1h and 4h
  ranges with the retest on the execution TF; one signal per bar, conflicting directions skipped).
  Execution TFs 15m, 24m, 1h; Variants A and B. 2 x 3 x 2 = 12 search procedures.
- **Selection label:** structure stop, 2R target (reference). Rule selection uses each signal's own simulated outcome
  (net R of filled trades, portfolio rules not applied); out-of-sample evaluation uses the full engine and portfolio.
- **Features (fixed list, direction-relative where marked):** r1_rel, r2_rel (trend direction/strength relative to the
  trade); htf_near_cross_rel; htf_mf_rel (HTF MF rising for longs / not rising for shorts); atr_pctile_30d; session;
  funding_z_rel (funding z x direction); cmf_rel (exec CMF x direction); cmf4h_rel (4h CMF x direction);
  confluence_types; fib_exec_in_0618_zone; sr_dist (absolute distance to the nearest execution-TF S/R level, ATR).
- **Conditions:** numeric features: x <= q33, x <= q67, x > q33, x > q67 with q = tertile cut points of the fold's
  training signals; categorical and binary features: x == value. **Rules:** no filter, any single condition, or any
  pair of conditions on two different features.
- **Fold training data:** all dev signals whose signal time is at least 7 days before the fold start (embargo) and
  whose trade or order ended before that point (purge). The rule with the highest training expectancy among rules with
  at least 100 training trades is applied unchanged to the fold's signals.
- **Final rule:** the same procedure trained on all dev data before 2025-11-15 (with the same purge). S10 requires
  the same rule (same features and directions of conditions) to be selected in at least 4 of the 6 folds.
- **Budget accounting:** each procedure counts as 1 configuration (12). Then for at most the 3 best procedures by
  out-of-sample expectancy: the 7-target label grid (up to 21) and parameter-stability neighbours (up to ~30).
  Stated caveat: the many rules tried inside each fold are not counted in N for the deflated Sharpe, which flatters
  the result; the high bar of S1-S10 is the protection.

## Change log
- 2026-11-15: initial freeze at Gate 1. User decisions: splits, warm-up and walk-forward approved after explanation;
  limit order life changed from 1 bar to "until 0.5R favourable move or 24 h" (user); risk guards, 00:00 UTC reset,
  labels, regimes R1/R2, range parameters, confluence, grids, budget 800 and criteria S1-S10 approved as proposed.
  Interpretation added by Claude and stated here for review: pending limits count toward the 3-position cap.
- 2026-11-16: Amendment 1 at Gate 2 (see above). User decisions: WT anchor filter, frozen-spec MF divergence and
  front-run, structure stops, respect rule, higher-TF ranges, 6m dropped. Success and kill criteria unchanged.
- 2026-11-16: Phase 3 discovery plan declared and approved (section above). No criteria changed.
