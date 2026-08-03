# CATEGORICAL FADE v1 - FROZEN SPEC

Status: FROZEN before Phase 1 execution. No changes except by explicit logged amendment.
If the code and this spec disagree, this spec wins.

Derived from the categorical-trading framework in VIDEO_EXTRACT.md, mechanised as the
configuration that survived Gate 0 (GATE0_VERDICT.md, GATE0_STABILITY.md). This is NOT the
system in the source video. The video teaches 20-to-40-second scalping at 1:1 on NQ. This is a
4H swing system at 0.47 R:R on BTC. It inherits the framework's classifier and its two trade
templates and nothing else. That difference is stated here so it cannot be quietly forgotten.

## 1. Instrument and timeframe
- BINANCE BTCUSDT.P, 4H bars only.
- 15m and below are excluded: Gate 0 showed the gross edge is timeframe-invariant while cost per
  R is not, and everything below 1h is consumed by friction.
- 1h is excluded on data grounds: the parquet has a 520-day hole covering all of 2023.

## 2. Classifier
- Kaufman Efficiency Ratio on close, lookback 20 bars.
  `ER(t) = |C_t - C_{t-20}| / sum_{i=t-19}^{t} |C_i - C_{i-1}|`
- **Threshold is CAUSAL.** A bar qualifies as consolidation when `ER(t) <= P10(t)`, where `P10(t)`
  is the 10th percentile of all ER values observed strictly before bar t.
- Warmup: no signals until 2,000 ER observations exist. Signals before that are discarded, not
  counted as skipped.
- This is a deliberate tightening from Gate 0, which used pooled full-sample decile edges. A live
  system cannot know future quantiles. If the result degrades under causal thresholding, that
  degradation is the honest number.

## 3. Range and direction
- Range at bar t: `R_hi = max(high, t-19..t)`, `R_lo = min(low, t-19..t)`, `mid = (R_hi + R_lo)/2`.
- Displacement sign `s = sign(C_t - C_{t-20})`. If `s = 0`, no trade.
- The trade FADES the displacement. `s > 0` means price rose into the upper range, so the trade is
  SHORT. `s < 0` means LONG. Fully symmetric.

## 4. Entry
- Market order at the OPEN of bar t+1. Never at bar t close.
- Everything in sections 2 and 3 is evaluated on closed bar t only. No intrabar evaluation.

## 5. Exits
- Target: the range midpoint `mid` as computed at bar t. Fixed at entry, never moved.
- Stop: the Donchian extreme in the displacement direction plus one ATR of buffer.
  - Short: `R_hi + 1.0 x ATR14(t)`. Long: `R_lo - 1.0 x ATR14(t)`.
  - ATR14 is Wilder (RMA) smoothed, computed on closed bars up to t.
- Fixed at entry. No trailing, no partials, no break-even moves, no discretionary exit.
- Maximum hold 200 bars. On the 200th bar the position exits at that bar's close.
- **Both-touched resolution: the STOP is assumed hit first.** OHLC cannot resolve intrabar path,
  so the ambiguous case always resolves against the system. Gate 0 excluded these bars; Phase 1
  is stricter and counts them as full losses.

## 6. Trade validity filters
A signal is discarded unless all hold at bar t:
- reward distance `|mid - entry| > 0.5 x ATR14(t)`
- risk distance `|entry - stop| > 0.5 x ATR14(t)`
- reward/risk ratio `< 20`

These exist to remove degenerate geometry (entry sitting on the midpoint), not to improve results.

## 7. Position management
- One position at a time. A signal arriving while a position is open is SKIPPED and logged as
  skipped. Gate 0 measured mean concurrent overlap at 0.33 positions, so this discards few signals
  and is the conservative choice.
- No pyramiding, no averaging, no hedging.

## 8. Sizing
- 1% of CURRENT account equity at risk per trade, matching the convention in the repo's other
  FROZEN_SPEC.
- `size = (0.01 x equity) / risk_distance`.
- Starting equity 10,000. No leverage cap modelled, no margin call modelled, no funding modelled.
  Funding on a perpetual over multi-day holds is a real omission and is recorded in section 10.

## 9. Costs
- Commission 0.04% per side, 0.08% round trip. This is the repo's standing assumption and remains
  UNVERIFIED against a venue schedule.
- Slippage 0.02% per fill, applied to entry and exit alike, always against the position.
- All-in base case: 0.12% round trip.
- Costs are applied to every fill including max-hold exits.

## 10. Known honesty flags
1. Costs are assumed, not verified.
2. Perpetual funding is not modelled. Median hold is short (1 bar median, 12 bars at p90) so the
   exposure is limited, but it is a real unmodelled cost that is always a drag on one side.
3. One asset, one venue, ~5.5 years, 2,190 bars per year. Crypto has few distinct macro regimes.
4. No holdout. Every bar in this test is data the repo already contained during Gate 0. This can
   falsify, never confirm.
5. Kill thresholds in AUDIT_COMMITMENTS_CATEGORICAL.md were written AFTER Gate 0 results existed.
   They are therefore informed, not blind. This is stated plainly rather than hidden.
6. The 4H bar close is a UTC-aligned convention from the data export. Bar alignment is a free
   parameter nobody has tested.
