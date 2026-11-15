# NOTEBOOK

Resume from this file plus ML_DISCOVERY_PROMPT.md (the standing brief, repo root) and PROTOCOL.md (once it exists).

## Current status
- **Phase 0 complete. Waiting for Gate 0 approval.** Do not start Phase 1 until the user says go.
- Report: `reports/phase0/QA_REPORT.md`.

## Rebuilding the data (new session)
Data is not in git. Rebuild with `uv sync && uv run python -m tradingstudy.data.pipeline` (about 2 GB of downloads,
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

## Open questions for the user
1. Does ML_DISCOVERY_PROMPT.md officially supersede FROZEN_SPEC.md and CLAUDE_CODE_PROMPT.md? (Not answered.)
2. Run the FROZEN_SPEC system unchanged as a third Phase 2 baseline? (Proposed, not answered.)
3. Holdout verdict judged on the 8 non-BTC coins, BTC reported separately (BTC 2025-01..2026-06 was the old study's
   test set and was traded live)? (Proposed, not answered.)
4. Were any of the other 8 coins traded live in the last 12 months? (Not answered.)
5. MCB Clone v1 PineScript is referenced in old prompts but not in the repo. Add it, or treat brief formulas as canonical?
6. Limit order lifetime (proposal: cancel after 1 bar). Daily reset time (assumed 00:00 UTC).

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
