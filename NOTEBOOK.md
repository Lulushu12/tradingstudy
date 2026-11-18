# NOTEBOOK

Resume from this file plus ML_DISCOVERY_PROMPT.md (the standing brief, repo root) and PROTOCOL.md (once it exists).

## Current status
- **Hypothesis H-MV (Macro View gate, Amendment 2) tested: NO candidate (27/27 negative). Waiting for the user's
  decision.** Reports: `reports/phase3/DISCOVERY_REPORT.md`, `reports/phase3/HMV_REPORT.md`. Budget used 417 of 800
  (P3-001..039).
  Holdouts were NOT opened (Phase 4 not reached), so they remain clean for any future hypothesis.
- Earlier status: Phase 2 re-run (Amendment 1 definitions) complete.
  Reports: `reports/phase2/BASELINE_REPORT.md` (v1, P2-001..212) and `reports/phase2/BASELINE_V2_REPORT.md`
  (v2, P2-213..378). PROTOCOL.md FROZEN 2026-11-15 with Amendment 1 (2026-11-16). Budget used: 378 of 800.
  User chose option A (narrow discovery) at Gate 2; the concrete discovery plan still needs approval.
- Phase 0 report: `reports/phase0/QA_REPORT.md`.

## Rebuilding the data (new session)
Data is not in git. The "tradingstudy" cloud environment has a setup script that runs the pipeline at container
build (unproven until the first fresh session; if data/clean is missing, run it manually). Manual rebuild: `uv sync && uv run python -m tradingstudy.data.pipeline` (about 2 GB of downloads,
checksum-verified, roughly 10-15 minutes). Network: needs data.binance.vision (the "tradingstudy" cloud environment
allows it). fapi.binance.com is geo-blocked from the cloud container, so there is no API gap-fill.

## Decisions made (Phase 0)
- Stack: Python 3.13, uv with pinned `uv.lock`. pandas 3.1.1, numpy 2.5.4, pyarrow 26.0.1, pytest 9.2.0.
  Note pandas 3 defaults to microsecond timestamps; code converts explicitly where unit matters.
- Source: data.binance.vision USDT-M perpetual 1m klines (monthly archives, daily archives for the current month and
  for repair) plus monthly funding-rate archives. Raw zips in `data/raw/` untouched.
- All timeframes (6m, 15m, 24m, 30m, 1h, 4h, 1D, 1W) resampled from 1m. Bars labelled by open time (UTC), cover
  [t, t+tf), known only at t+tf. Intraday anchored to UTC midnight, weeks to Monday 00:00 UTC. Matches TradingView.
- Resampled bars carry `n_1m` and `complete`. Gaps are never forward-filled.
- Kline archive defect: some minutes are "frozen" (zero volume, flat OHLC) although trading happened. Fix order:
  (1) daily kline archive overrides monthly (it fixed BTC 2023-11-10, 100 minutes); (2) rebuild from aggTrades,
  validated against that day's normal minutes (OHLC within 0.05% on at least 99% of minutes); (3) minutes with no
  trades at all become gaps. Exchange-wide no-trade windows (2022-05-01, 2022-05-28, 2023-09-12, 2025-08-29) look
  like genuine Binance halts.
- Spikes (big wicks) are listed, not removed. The ones checked are real events (2023-07-13 XRP SEC ruling,
  2025-10-10 liquidation crash, FOMC/CPI prints).
- Holdout guard: `tradingstudy.data.guard` is the only sanctioned loader. Scope "dev" excludes any bar that straddles
  a boundary. Holdout scopes need `holdout_unlock.json` (gitignored, must not exist before Phase 4). Scope "qa" is
  for data-quality counts only.
- Provisional splits (until Gate 1): secondary holdout < 2022-01-01, dev 2022-01-01 to 2025-11-15, primary holdout
  2025-11-15 to 2026-11-14 (download date 2026-11-15).

## User answers so far
- Limit entry price: the signal bar's close. Fill requires trading through by at least one tick.
- Breakout: 6% max drawdown is static (from starting balance). 3% daily is measured from balance without open P&L,
  resets at daily close (assumed 00:00 UTC, unconfirmed).
- Risk: 0.5% of current equity per trade.

- FROZEN_SPEC.md and CLAUDE_CODE_PROMPT.md are SUPERSEDED by ML_DISCOVERY_PROMPT.md (user, Gate 0).
- No FROZEN_SPEC system baseline (user declined).
- Holdout verdict judged on the 8 non-BTC coins; BTC reported separately (user agreed).
- User traded some of the other coins live in the last 12 months, so the primary holdout is weaker on all coins,
  not only BTC. BTC remains worst (old systematic study tested WT signals on 2025-01..2026-06). Caveat goes in PROTOCOL.md.
- Canonical clone source: Lulushu12/Trading-training `indicators/MCB_Clone_v1.pine`. It does NOT match the brief's
  section 5.2 baseline (pine uses 5-bar fractal divergences with -65/-40/+45/+15 filters and stdev-based MF; the brief
  describes dot divergences, 5 dots, 300 bars, MF lookback 100). User confirmed no other indicator file exists, so the
  brief's dot-divergence baseline is implemented from the brief's text.
- Money Flow: choose the variant that best matches the TradingView exports (indicator matching, no P&L, no budget
  cost) and carry only that one into discovery (user agreed). User does not remember whether the exports are real
  MCB or the clone; the validation will tell (column names suggest real MCB).

## Phase 1 results (summary)
- WaveTrend validated vs real MCB (100% cross-dot agreement). Money Flow = MCB_Clone_v1 formula on Heikin-Ashi
  candles, no outer EMA (corr 0.99, 95% sign agreement). Brief's HTF formula ~86%, fixed 3H rejected.
- Feature code: src/tradingstudy/features (mcb, divergence, htf, context, build), src/tradingstudy/structure
  (swings, ranges, levels, profile, build). 60 tests incl. end-to-end real-data look-ahead test + mutation test.
- Census: divergence stack ~12/day across coins at 15m (needs filtering to reach ~1/day); range flip 0.6/day at 15m k=3.
- Known weaknesses flagged at Gate 1: contaminated holdout on all coins, small range-flip sample, level density makes
  confluence weak, several divergence details are Claude's definitions.

## Phase 2 results (summary)
- All 212 baseline configurations have negative net expectancy except 2 tiny-sample ones (best +0.05R, 94 trades,
  DSR 0.18). None meets any of S1, S2, S4, S5, S7. Deflated Sharpe ~0 everywhere.
- Gross R (before fees) is about zero: the divergence stack and the range flip behave like coin flips at the entry;
  fees (0.14R on 6m, 0.10R on 15m, 0.05R on 1h) make them losers. 6m is negative even before fees.
- Hints (all still negative or small samples): higher TF is better (1h best); with-trend (R1) beats counter-trend in
  Baseline 1 at every TF; HTF near-cross filter improves Baseline 1 on every TF; BTC is the worst coin almost everywhere.
- Missed fills are rare (2-3% of orders, about half would have won): limit at close nearly always fills.
- Code: src/tradingstudy/backtest (engine, portfolio, stats, signals, costs, cache), src/tradingstudy/phase2.
  Trades per config: data/results/phase2/trades.parquet (not in git; rebuild with python -m tradingstudy.phase2.baselines).

## Phase 2 re-run results (v2, Amendment 1)
- All 166 negative except 3 tiny-sample cases; best: stack v2 1h confirmed + HTF near-cross, 2R, +0.037R over 290
  trades, 3/6 folds, 5/9 coins, DSR 0.00. None meets S1, S2, S5 or S7.
- Corrected definitions did not help: stack v2 gross R -0.09 (15m) to -0.04 (1h); range flip with respect rule gross
  -0.03 to -0.15; higher-TF ranges are rare (36-156 trades in 3 years across 9 coins) and negative.
- Consistent hints across v1 and v2: 1h best; with-trend beats counter-trend for the divergence stack on every TF;
  HTF near-cross helps on 1h/24m; BTC worst coin. Longs and shorts both negative (no sign bug).

## Phase 3 results (summary)
- 12 walk-forward rule-search procedures (stack v2 and pooled range flips x 15m/24m/1h x A/B): all negative out of
  sample (-0.085R to -0.360R net), DSR 0.00, every one fails S1, S2, S3, S4, S5, S7, S9.
- Classic overfitting signature: rules picked on training data showed +0.15R to +0.28R, then lost in the next fold.
- Most stable rule: 24m stack front-run, "with 4h trend AND HTF near-cross" (picked 4/6 folds): gross +0.018R,
  net -0.085R. Not a candidate.
- Label grid and stability neighbours deliberately not run: the declared plan allows "at most 3"; with no procedure
  positive out of sample, tuning targets would be fishing.

## H-MV results (summary)
- Macro View replica: user's indicator from Trading-training branch claude/practical-galileo-wyubia (f_macro_core),
  exact timing, user's lean rule. Code: src/tradingstudy/features/macro.py, phase3/hmv.py.
- 27 configurations (stack A, stack B, WT divergence alone x lean/any/strong x 15m/24m/1h): all negative, -0.05R to
  -0.25R net, DSR 0.00. Gated results are about the same as ungated (15m -0.16..-0.24 vs -0.20..-0.23; 1h
  -0.05..-0.12 vs -0.10..-0.13). Best: 1h stack with strong Macro View bias, -0.053R, gross +0.002R.
- Follow-up (target grid, stability) not run: declared to run only if a configuration is positive out of sample.

## Exit diagnostic (E003)
- Favourable vs adverse excursion after entry is symmetric for every entry set (46-51% favourable-first; random control
  48-50%; median MFE = median MAE). No exit rule (partials, trailing, breakeven) can extract an edge from these entries.

## Diagnostics E004 / E005 (2026-11-18)
- E004 range edges: ranges short-lived (median life 4 h on 15m to 72 h on 4h), price inside a confirmed range ~7% of
  the time; edges hold 2-4 points WORSE than a random walk. Range fading closed.
- E005 HTF entries + 15m structure stop: 1h signals random; 4h signals show a small early favourable reaction
  (53-55% at 0.5-1R vs control ~49-51%) that fades by 2R. Did not meet the declared rule. Implied net ~+0.03-0.05R
  at 1R, below the bar. Report: reports/phase3/RANGE_HTF_DIAGNOSTICS.md.

## Open questions for the user
1. Which coins were traded live in the last 12 months, and roughly how often?
2. Final decision after Phase 3: stop with the verdict "no system found", or declare a new hypothesis (new plan,
   counted against the remaining 410 configurations).

## Issues to carry into Phase 1 / Gate 1
- Fee in R is large on low timeframes (BTC dev medians: 6m-proxy 0.48R at 1x ATR stop, 15m 0.25R, 1h 0.12R).
  Likely proposal: 6m only with 2.0x ATR stop; drop 1.0x ATR stop everywhere.
- Indicator warm-up: features at the start of dev need bars from before 2022-01-01 (secondary holdout). Proposal for
  Gate 1: allow pre-dev bars as indicator warm-up only, never for labels or evaluation.
- Bars containing a halt are flagged incomplete (e.g. 5 BTC weeks). Phase 1 needs a usability rule (e.g. n_1m >= 95%).
- Funding archives end 2026-10-31 (no November monthly file yet). Inside the holdout, so irrelevant until Phase 4.
- BTC perps listed 2019-09 but archives start 2020-01. Inside secondary holdout.
- MCB clone validation must use only TradingView export rows before 2025-11-15.
- TradingView exports with MCB columns: BTC 5m, 15m, 1h, 4h, 1D, 1W (Lt Blue Wave = WT1, Blue Wave = WT2, VWAP,
  Mny Flow). XRP 15m has Mny Flow only. No exports for 6m or 24m. The 1m export has no MCB columns.

## Incident log
- 2026-11-15, Phase 0: a file-format probe printed 2 rows (2 minutes) of raw BTC 1m prices from 2026-10, inside the
  provisional primary holdout. No strategy, indicator or outcome information. Breaks the letter of hard rule 2.
  Disclosed to the user. All later probes used pre-holdout files and the guard enforces this in code.
- 2026-11-15, Phase 2 pre-run: (1) BUG found before any baseline run: ranges.py defaults were still the draft
  values (tol 0.5 ATR, h_min 3 ATR) instead of the frozen 1.0 / 2.0. Fixed; feature cache rebuilt. No results had
  been produced with the wrong values. (2) A "mechanical" sanity check printed stop/target/timeout exit counts for 6
  ETH 15m configurations (B1 A and B2 A, 1.5 ATR stop, targets 2R / fib1.272 / next_level), which reveal win counts.
  These configurations belong to the frozen baseline set, so no choice was made on them. Disclosed to the user.
