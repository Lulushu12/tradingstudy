# GATE 0 REPORT

Date: 2026-07-08. Auditor: skeptical quantitative audit per CLAUDE_CODE_PROMPT.md.
System under audit: FROZEN_SPEC.md v1 (Variant B primary, Variant A comparison).
Canonical indicator source: MCB_Clone_v1.pine (committed to repo this session).

Status: GATE 0 COMPLETE EXCEPT PORT VALIDATION, WHICH IS BLOCKED ON A FRESH
EXPORT FROM THE TRADER. STOPPED. No backtest has been run. No P&L has been
computed anywhere. Phase 1 requires (a) resolution of the open items below and
(b) the trader's explicit written go.

## 1. Port and validation status

The indicator was ported line by line from MCB_Clone_v1.pine to
audit/mcb_port.py: WaveTrend (WT), MFI clone, 5-bar fractals with 2-bar
confirmation lag, regular divergences with level filters on both the primary
(45 / -65) and secondary (15 / -40) WT chains and the MFI chain (2.5 / -2.5),
and the pre-div raw conditions. RSI, StochRSI, gold dots, and buy/sell dots
are excluded per spec section 2. Spec overrides applied at the system layer:
stack window 11 (not the Pine default 30), preDivMaxAge 50 (not 100).

Validation state, reported honestly:

- The 15m TradingView exports in the repo carry indicator columns. Per the
  trader's instruction those columns are treated as noise and all indicators
  are computed from OHLCV only. For the record, before that instruction the
  port's wt1/wt2 matched those columns within 1e-6 relative on 99.4% of
  187,700 compared bars, with every mismatch traceable to TradingView export
  cold-start artifacts at chunk boundaries (proven by two TV exports of the
  same bars disagreeing with each other by the same decaying magnitudes).
  The exported money-flow column does NOT match the canonical f_mfi formula
  and appears to come from an older indicator version; it was abandoned as a
  reference rather than reverse-engineered.
- Therefore, formally: THE PORT IS NOT YET VALIDATED. Required from the
  trader: a TradingView export of MCB Clone v1 itself (current version, deep
  history loaded before exporting) over any studied-data span of a few
  thousand bars, containing wt2, mfi, and the divergence dot columns
  (WT Bear/Bull Div, WT 2nd Bear/Bull Div, MFI Bear/Bull Div) and ideally the
  stack diamonds. Until the port reproduces those within floating-point
  tolerance, all census numbers below are PROVISIONAL and no backtest runs.

## 2. Data integrity

- Studied set: 33 TradingView export chunks (15/ and "New export/15m/"),
  BINANCE BTCUSDT perpetual, 15m. Merged: 191,170 unique bars from
  2021-01-07 07:00 UTC to 2026-06-21 16:45 UTC (bar-open times, all UTC,
  all timestamps exactly on 900s boundaries).
- Continuity: 3 gaps totaling 6 missing bars (2021-03-02, 2022-05-01,
  2022-05-28), consistent with Binance maintenance/outages. Nothing else.
- Quality: zero OHLC-inconsistent bars, zero NaNs, zero non-positive prices,
  zero zero-range bars, zero zero-volume bars.
- Duplicates: 146,098 duplicated-timestamp rows across overlapping exports;
  OHLC identical everywhere except two partial-bar export artifacts at the
  newest edge, both fixed against the Binance archive: bar 2026-06-21 16:15
  (kept the completed row) and final bar 16:45 (patched with the completed
  archive bar; the TV export had caught it mid-formation at 5% of its final
  volume).
- Feed check: completed TV-exported bars match the Binance USDT-M futures
  archive to the decimal. The studied data IS Binance perp data.
- Live-execution risk, flagged not hidden: Breakout sources liquidity from
  OKX, Bybit, and Binance. Live fills and live indicator values on Breakout's
  feed will not be identical to this Binance series. Backtest results carry
  that additional feed-mismatch risk on top of everything else.
- 2025 coverage hole: the studied set has NO data for 2025-03-01 through
  2025-06-30 (no export covers it). Phase 1 windowing must treat 2025 as
  partial. If the trader has this span, exporting it would close the hole.

## 3. Costs (verified 2026-07-08)

- Commission: Breakout publishes 0.04% per side taker/maker, so the spec's
  0.08% round trip is CONFIRMED, not conservative padding.
- Swap fee, NOT in the spec: 0.033% per open position per day. On the
  Breakout terminal it accrues as ~0.0055% at each 4h mark; on the DX
  terminal it is charged daily at 00:00 UTC snapshot. A 15m system holds
  through 4h marks routinely, so this is a real cost and will be modeled.
  OPEN QUESTION for the trader: which terminal do you trade on?
- Slippage proposal (for pre-commitment in AUDIT_COMMITMENTS.md):
  0.02% (2 bps) per fill, all fills market orders per spec, so 4 bps per
  round trip on top of commission. Justification: BTC perp top-of-book
  spread is typically well under 1 bp, but entries fire at 15m closes which
  cluster with volatility, stops are stop-markets filled in fast tape, and
  Breakout's aggregated feed adds basis noise vs Binance. 2 bps per fill is
  deliberately on the harsh side of typical for this size; Phase 1 will also
  sweep slippage upward until expectancy crosses zero and report the
  headroom.
- Venue drawdown limits (verified via Breakout program rules): max daily
  loss 3% (1-Step) or 5% (2-Step); max drawdown 3% (Turbo), 5% (Pro),
  6% (Classic), trailing on 2-Step; limits apply to EQUITY INCLUDING OPEN
  POSITIONS and a single touch forfeits the account. At the spec's 1% risk
  per trade, six consecutive full losses breach a Classic account. A 15m
  divergence system will produce 6-loss streaks routinely. This constraint
  is carried into the draft kill thresholds below.
  OPEN QUESTION for the trader: which account model/size is the target?

## 4. Holdout (quarantined)

- Span: all BTCUSDT perp data with bar opens at or after
  2026-06-21 17:00:00 UTC (unix 1782061200), any timeframe, any source.
- Fetched by script from the Binance USDT-M public archive to
  holdout/holdout_15m.csv: 1,468 bars through 2026-07-06 23:45 UTC bar open,
  zero gaps. Not one row was printed, plotted, or described. The file will
  be extended forward by the same script as time passes; extending is
  allowed, reading is not. Recorded in HOLDOUT_DO_NOT_TOUCH.md; the data
  loader refuses quarantined paths.
- Honest assessment: this holdout is currently ~15 days and grows only as
  real time passes. It is SHORT, and it is CONTAMINATED: the trader traded
  and replay-practiced this market recently, and the studied span itself
  ends 17 days ago. A pass on this holdout will be weak evidence; a fail is
  still a fail. REQUIRED FROM THE TRADER at sign-off: state how much of the
  span after 2026-06-21 you actively traded or replayed, so the
  contamination is on record before anyone looks at results.

## 5. Signal census (PROVISIONAL pending port validation; counts, no P&L)

Raw divergence events (confirmation bars, studied data; 2021 and 2026
partial years, 2025 missing Mar-Jun):

  year   WT bull  WT bear  MFI bull  MFI bear
  2021       310      354       358       322
  2022       289      345       363       294
  2023       265      337       362       316
  2024       305      375       323       324
  2025       345      383       360       346
  2026       157      174       190       130
  total     1671     1968      1956      1732

Variant A (WT div + MFI div, confirmation gap <= 11, gap 0 valid), counted
as leg pairs, signal at the later confirmation bar:

  year   bull  bear      total pairs: 1520
  2021    121   149      unique signal bars: 1414
  2022    119   126
  2023    125   123
  2024    135   148
  2025    153   165
  2026     81    75

Variant B (leg 1 confirmed div either oscillator, leg 2 front-run on the
other: pre-div raw condition + one-bar tick, leg 1 confirmed by the turn
bar, turn bar within 11 of leg 1's pivot; first completion consumes the
leg pair):

  year   bull  bear      total: 1333 (leg1=WT 673, leg1=MFI 660)
  2021    111   143      unique signal bars: 1294
  2022    110    81
  2023     93    98
  2024    114   139
  2025    163   171
  2026     63    47

Sample-size verdict (Gate 0 item 5): Variant B produces roughly 270 signals
per year. That is ENOUGH for inference. No small-sample kill at census
stage. Reminder per operating principles: these are in-sample counts on
studied data; they can falsify, never confirm.

## 6. Shared-leg statistics and dedup rule proposal

On Variant A pairs: 15.3% of WT legs (199 of 1,302) and 13.1% of MFI legs
(175 of 1,339) participate in more than one pair; worst single leg feeds 4
pairs. Collapsing same-direction signal bars closer than 12 bars into one
cluster gives 544 bull / 592 bear clusters for A, 519 / 541 for B.

PROPOSED DEDUP RULE (for approval, then frozen): when a signal fires, BOTH
of its legs are consumed for that variant and direction. A later pair that
re-uses a consumed leg is not a new trade. First completion wins. This is
causal (decidable at the signal bar), it mirrors the spec's own
"the front-run consumes the signal" principle, and it prevents pyramiding
one anchor into multiple 1% positions.

RELATED SPEC SILENCE, needs the trader's ruling now, before any results
exist: a fresh same-direction signal (all-new legs) while a same-direction
position is already open. Options: (a) open an independent additional
position, symmetric with the spec's opposite-signal rule; (b) skip while a
same-direction position is open. This choice changes trade counts and
correlated risk. It must be decided here, blind, not after Phase 1 numbers.

## 7. Draft Phase 1 kill thresholds (for approval, then frozen in AUDIT_COMMITMENTS.md)

All evaluated per variant on studied data, net of 0.08% RT commission,
2 bps/fill slippage, and the swap fee model, at 1% risk sizing per spec.
Walk-forward scheme: 10 consecutive calendar half-year windows 2021H1
through 2026H1 (2025 windows partial per the coverage hole). No parameter
is fit anywhere in Phase 1, so windows are evaluation segments, and every
result is in-sample by construction.

- K1 Expectancy: pooled net expectancy per trade <= 0 R after costs: KILL.
- K2 Consistency: more than half of the windows with negative net
  expectancy: KILL.
- K3 Cost headroom: breakeven slippage under 4 bps/fill (2x assumption):
  KILL.
- K4 Concentration: pooled net expectancy <= 0 after removing the single
  best window: KILL (an edge living in one window is a regime bet wearing
  a system costume).
- K5 Venue survivability: bootstrap the observed trade sequence; if the
  probability of touching the target account's max-drawdown limit within
  one year of trading at spec sizing exceeds 50%, the system AS SPECIFIED
  is untradeable at Breakout even if K1-K4 pass. Sizing is frozen; changing
  it to pass K5 would be a spec amendment for the trader to decide, made
  blind, not tuned against results.

A kill by K1-K4 on both variants means the system is dead, and optimization
is not a resurrection tool.

## 8. Open items blocking Phase 1 (trader input required)

1. Fresh MCB Clone v1 export for port validation (section 1). BLOCKING.
2. Which Breakout terminal (swap fee model) and which account model/size
   (K5 limit). BLOCKING for cost model freeze.
3. Ruling on same-direction concurrency (section 6). BLOCKING.
4. Confirm the pre-div current-turn zero-line filter interpretation: the
   coded default requires wt2 < 0 for a bull front-run turn (mfi < 0
   respectively; mirrored for bear). The spec's "the current front-run turn
   is unrestricted" was read as "no pivot-level filter on the turn", which
   is consistent with the code. Confirm or correct. BLOCKING.
5. Confirm Variant B timing interpretation: the front-run completes only at
   a bar t where leg 1 is already fractal-confirmed (t >= leg 1
   confirmation bar), so gap 0 means leg 1 confirms on the same bar close
   as leg 2's turn. BLOCKING.
6. Contamination statement for the holdout span (section 4). BLOCKING for
   the final holdout test, not for Phase 1.
7. Optional: export covering 2025-03-01 to 2025-06-30 to close the studied
   data hole.
8. Approve or amend: slippage 2 bps/fill, dedup rule, kill thresholds K1-K5,
   walk-forward scheme. Once approved they are written to
   AUDIT_COMMITMENTS.md and become immutable.

Per the operating rules: STOPPED here. No Phase 1 work will start without
the trader's explicit written go after the blocking items are resolved.

## 9. Trader rulings received 2026-07-08 (logged verbatim intent, blind, pre-results)

- Item 2 (terminal): Breakout terminal. Swap modeled as 0.0055% charged at
  each 4h boundary crossed while a position is open. Account size $10k.
  Account model: 1-Step Classic (3% max daily loss, 6% static max
  drawdown on $10k). RESOLVED.
- Item 3 (same-direction concurrency): independent additional position.
  Each signal trades independently at the per-trade risk fraction.
- Item 4 (pre-div zero-line filter): consistent with the code. Bull
  front-run turn requires the oscillator below 0, bear above 0, on the
  current bar. CONFIRMED.
- Item 5 (Variant B timing): front-run completes only at or after leg 1's
  confirmation bar. CONFIRMED.
- Item 7 (dedup): leg-consumption rule CONFIRMED.
- SPEC AMENDMENT 1 (blind, agreed in conversation before any P&L existed):
  risk per trade changed from 1% to 0.5% of current equity. Motivated by
  Breakout equity-limit survivability (K5), decided without reference to
  any backtest result. FROZEN_SPEC.md section 5 sizing is superseded by
  this amendment; the spec file itself is not edited.
- Item 7 slippage: trader proposed zero slippage on the argument that
  market-at-close fills are symmetric around the backtest price. Auditor
  REFUSED zero as baseline: symmetry covers drift between signal close and
  fill, but not (a) taker fills crossing the spread, which is paid on every
  fill by construction, and (b) stop-market exits filling in adverse fast
  tape, where ATR stops sit exactly where liquidation cascades run. Both
  are systematic, not zero-mean. Counter-proposal pending trader response:
  1 bp per fill baseline (small because $10k positions have negligible
  impact in BTC perp), Phase 1 still sweeps slippage upward, K3 kill
  requires positive expectancy at 3 bps per fill.
- Item 1 (port validation): trader asked why self-computed values do not
  suffice. Auditor position: the port computes values, but validation
  checks the TRANSLATION of Pine semantics against TradingView's own
  execution (ema seeding, population vs sample stdev, valuewhen chains,
  fractal edge cases). The WT path is incidentally validated via the old
  export columns; the canonical MFI formula and all divergence event logic
  have zero independent checks. A fresh MCB Clone v1 export remains
  BLOCKING for any backtest.
