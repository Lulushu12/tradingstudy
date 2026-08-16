# Baseline: 4H volume-spike trend-continuation, 6-symbol portfolio

Rule: close vs EMA200(4H) trend filter; trigger = volume > 1.8x SMA20(volume) with bar
closing in trend direction; entry next 4H open; stop 1.5*ATR14 (Wilder); target 2:1;
one position per symbol (later signals while occupied are dropped); fees 0.08% RT.
Symbols: BTC, ETH, XRP, SOL, LINK, DOT (USDT perp klines, 2020-01 .. 2026-07).
Signals: 4,944 candidates -> 3,043 resolved trades after per-symbol locks.

## Portfolio results at risk_frac = 1% per trade

| Period                | n     | WR    | expR net | tr/mo | mo ret (geo) | max DD  | % pos months |
|-----------------------|-------|-------|----------|-------|--------------|---------|--------------|
| FULL (2020-2026)      | 3,043 | 40.0% | +0.174R  | 39.1  | +6.9%        | -39.8%  | 72%          |
| TRAIN (<2025-01-01)   | 2,229 | 40.1% | +0.178R  | 37.8  | +7.1%        | -31.8%  | 72%          |
| HOLDOUT (>=2025-01-01)| 814   | 39.7% | +0.165R  | 43.0  | +6.4%        | -39.8%  | 68%          |

Holdout expR holds up out-of-sample (+0.165R vs +0.178R train). Note the worst
drawdown of the whole sample occurs inside the holdout period. DD is measured on
daily exit-accounting equity; open-trade MTM between marks could add up to
~n_concurrent * risk_frac more.

## Per-symbol expR (TRAIN) — does the edge generalize?

| Symbol   | n   | WR    | expR net | tr/mo |
|----------|-----|-------|----------|-------|
| BTCUSDT  | 439 | 43.1% | +0.257R  | 7.4   |
| SOLUSDT  | 308 | 42.5% | +0.259R  | 6.1   |
| ETHUSDT  | 406 | 41.1% | +0.206R  | 6.9   |
| LINKUSDT | 348 | 38.8% | +0.146R  | 6.0   |
| DOTUSDT  | 319 | 38.6% | +0.136R  | 6.3   |
| XRPUSDT  | 409 | 36.2% | +0.064R  | 7.0   |

All six positive in train. Holdout per-symbol expR: BTC +0.04, ETH +0.16, XRP +0.19,
SOL +0.22, LINK +0.21, DOT +0.22 — the edge generalizes; BTC is actually the
weakest symbol out-of-sample.

## Sizing sweep (FULL period)

| risk_frac | mo ret (geo) | max DD  |
|-----------|--------------|---------|
| 0.10%     | +0.8%        | -4.9%   |
| 0.15%     | +1.1%        | -7.2%   |
| 0.50%     | +3.6%        | -22.2%  |
| 1.00%     | +6.9%        | -39.8%  |
| 1.50%     | +9.8%        | -53.7%  |
| 2.00%     | +12.4%       | -64.5%  |

Max DD crosses 6% between risk_frac 0.10% and 0.15% (~0.13%/trade). At that sizing
the portfolio earns roughly +1%/month. DD scales almost linearly with risk because
losses cluster: 6 correlated crypto symbols firing on the same volume/trend regime.

## Concurrency (time-weighted share of the sample at k open positions)

| k open | 0    | 1    | 2    | 3    | 4    | 5    | 6    |
|--------|------|------|------|------|------|------|------|
| share  | 14%  | 20%  | 22%  | 18%  | 14%  | 8%   | 4%   |

Median ~2 concurrent positions; >=3 open 42% of the time, all 6 open 4% of the
time. 84% of entries occur while at least one other position is already open —
positions are heavily overlapping and correlated, so pooling 6 symbols multiplies
trade count (~5x BTC alone) but delivers little drawdown diversification: DD grew
from -12.3% (BTC-only at 1%) to -39.8% (portfolio at 1%).

## Verdict

No — the 6-symbol version does not approach 10%/mo at <=6% max DD. It reaches
~10%/mo only at 1.5% risk with -54% max DD; constrained to <=6% max DD it must be
sized down to ~0.13% risk/trade, yielding roughly +1%/month. The edge is real and
generalizes across all six symbols out-of-sample, but cross-symbol correlation
means return/DD efficiency barely improves over BTC alone (~0.17 mo-ret/DD ratio).
More symbols scale trade frequency, not risk-adjusted return.
