# Holdout quarantine

Declared 2026-07-30, before any signal search was run.

## Locked spans

| Block | Span (UTC) | Use |
|---|---|---|
| TRAIN | 2021-01-01 .. 2024-12-31 | Search. Anything goes here. |
| TEST | 2025-01-01 .. 2026-06-21 | Out-of-sample validation. Read only after a candidate is frozen from TRAIN. |
| HOLDOUT | 2026-06-22 .. 2026-07-29 | **QUARANTINED.** Never read, plotted, described, or fed to any statistic until the final system is frozen in writing. |

## Cross-asset quarantine

Design and parameter selection happen on **BTCUSDT only**.
ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT are held as a structural out-of-sample check:
a rule fitted to BTC that survives unchanged on four other assets is much harder
to have curve-fit than one that only survives a time-split. Their data may not be
used to choose rules, parameters, or thresholds.

## Enforcement

`quant/src/data.py::load()` takes an explicit `block` argument and refuses to
return rows outside it. There is no code path that loads HOLDOUT without the
literal string `I_AM_RUNNING_THE_FINAL_HOLDOUT_TEST`.

## Honest limits of this holdout

- HOLDOUT is ~5.5 weeks, roughly one month. It can falsify a system. It cannot
  confirm one. A single month is one sample from a distribution.
- The repo's own prior study already looked at data through 2026-06-21, so TEST
  is partially contaminated by that earlier exploration. TEST is therefore a weak
  out-of-sample, and the cross-asset check carries more weight than the time split.
- The data is Binance USD-M perpetual. Breakout fills on Kraken-sourced prices.
  Basis and spread differ. This is a live-execution risk, not something the
  backtest can measure.
