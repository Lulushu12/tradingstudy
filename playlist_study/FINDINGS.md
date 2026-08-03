# Findings: backtesting the TradingLab "Day Trading" playlist

Scope as agreed: quick and dirty first pass. No commission, no slippage, no
walk-forward, single asset. What stops that being misleading is the
`breakeven_bps` column, the round trip cost that would take the average trade to
zero. Binance USD-M perp taker fees are about 8bps round trip, so anything below
roughly 10bps is already dead no matter how good its frictionless curve looks.

Data: BINANCE BTCUSDT.P from this repo's exports, 2021-01 to 2026-06.
Full numbers in `results/summary.csv`, reproduce with
`PYTHONPATH=playlist_study/src python3 playlist_study/src/run.py`.

## Headline

Seven of 25 tested configurations clear 8bps, but they represent only three
distinct strategies: S1 (Fibonacci ABCD), S5 (EMA meter + SMI) and S6 (Impulse
MACD). Everything else fails to cover the cost of trading.

The single most useful result is about the playlist rather than any one system.
The liquidity-sweep-into-fair-value-gap idea, which 21 of the 159 videos teach in
one form or another and which is the channel's signature content, is the worst
performer tested. Every variant loses money before costs, in one case at a
breakeven of -19bps. Removing components does not rescue it: dropping the sweep
requirement, dropping the break of structure, entering at the gap midpoint, and
targeting opposing liquidity were all tried, and the best of them lands at +1bps,
which is still short of the 8bps needed to trade it.

## Results

| Strategy | TF | Stop | n | Win% | Avg R | PF | MaxDD | Breakeven bps | Survives 8bps |
|---|---|---|---|---|---|---|---|---|---|
| S5 EMA meter + SMI | 4h | nbar | 164 | 39.0 | 0.16 | 1.23 | -45% | 72.4 | yes |
| S5 EMA meter + SMI | 4h | swing | 171 | 39.8 | 0.19 | 1.17 | -59% | 51.3 | yes |
| S6 Impulse MACD | 4h | nbar | 593 | 31.4 | 0.18 | 1.16 | -58% | 25.1 | yes |
| S6 Impulse MACD | 4h | swing | 594 | 30.1 | 0.15 | 1.15 | -58% | 23.0 | yes |
| S5 EMA meter + SMI | 4h | atr | 372 | 38.2 | 0.14 | 1.14 | -34% | 23.0 | yes |
| S6 Impulse MACD | 4h | atr | 602 | 28.9 | 0.23 | 1.14 | -57% | 21.2 | yes |
| S1 Fib ABCD 0.88 | 30m | stated | 513 | 17.9 | 0.49 | 1.56 | **-12%** | 14.3 | yes |
| S7 Smoothed HA (flip exit) | 1h | swing | 2059 | 31.9 | 0.10 | 1.09 | -56% | 7.1 | no |
| S2 Donchian+LWTI+vol | 5m | stated | 2302 | 35.3 | 0.06 | 1.04 | -66% | 3.6 | no |
| S3 Raschke 3/10 | 1h | swing | 1013 | 34.2 | 0.01 | 1.03 | -87% | 3.4 | no |
| S9 SMC (no sweep) | 15m | stated | 665 | 32.9 | -0.01 | 1.01 | -72% | 1.0 | no |
| S8 ABC + RSI | 4h | stated | 58 | 41.4 | 0.05 | 1.00 | -47% | -1.3 | no |
| S4 RSI 80/20 + VWAP | 15m | swing | 1139 | 44.6 | 0.00 | 0.96 | -66% | -2.6 | no |
| S9 SMC (as taught) | 15m | stated | 1307 | 29.0 | -0.13 | 0.85 | -96% | -18.7 | no |
| S9 SMC (target liquidity) | 15m | stated | 3065 | 49.6 | -0.17 | 0.70 | -99.8% | -19.2 | no |

Worst rows omitted; see the CSV.

## The claims, checked

Video 010 claims 62% win rate and 1,040% profit over 77 trades for the Fib ABCD
setup. The actual win rate over 513 trades on BTC 30m is **17.9%**, nowhere near
62%. The strategy is nonetheless the most interesting one in the playlist,
because it is still profitable: entering at the 0.88 retracement with the target
at the leg extreme pays 7.33R on a winner, so a 17.9% hit rate produces +0.49R
per trade and a profit factor of 1.56. The video's number is wrong and its logic
is sound, which is an unusual combination and the opposite of the failure mode
you would expect.

S1 also carries by far the lowest drawdown of anything tested, -12% against -34%
to -99% for everything else. That is a direct consequence of the tiny stop: risk
is 12% of the leg while reward is 88% of it.

The other claims are not checkable in the same way. "$10k to $1.1M in 12 months"
(053) and "$9,100 to $82M" (060) are attributed to third parties trading other
instruments, so a BTC backtest cannot confirm or refute them, only show that the
mechanics do not transfer to this market. S2, the Donchian + LWTI system behind
the first claim, produces a breakeven of 3.6bps on 2,302 trades: not a disaster,
but less than half the cost of trading it.

## Year by year, and why the headline table oversells

Pooled statistics hide regime dependence. Average trade return per calendar year
for the three survivors:

| Year | S1 Fib ABCD | S5 EMA+SMI | S6 Impulse MACD |
|---|---|---|---|
| 2021 | +0.218% | +1.142% | -0.132% |
| 2022 | +0.138% | +1.001% | +0.862% |
| 2023 | +0.002% | +0.920% | +0.611% |
| 2024 | +0.106% | +0.625% | +0.377% |
| 2025 | +0.273% | -0.531% | -0.173% |
| 2026 | -0.012% | +1.317% | -0.067% |

This reorders them. S6 has the second best headline breakeven but is positive in
only three of six years; its entire edge comes from 2022 to 2024, and it has lost
money in the most recent two. S5 has the best headline number of all but only 164
trades in five and a half years, about 27 a year, which is too few to say much,
and it had a losing 2025. S1 is the most consistent of the three, positive in
five of six years and never badly negative.

So the ranking by headline breakeven (S5, S6, S1) roughly inverts once stability
is considered (S1, then S5, then S6).

## How much the interpretations mattered

Testing all three readings of "stop below the recent low" was worth doing,
because the choice changes the verdict rather than nudging it:

- S5 ranges from 72.4bps (N-bar low) to 23.0bps (ATR multiple). All survive, but
  the best reading looks three times better than the worst.
- S3 ranges from +3.4bps (swing pivot) to -11.7bps (ATR). One reading is
  marginally alive, another is clearly dead.
- S7 ranges from +6.0bps to -11.5bps depending on stop and exit.

No video in the playlist defines this. A viewer implementing any of these
strategies is choosing, unknowingly, between materially different systems.

## What is not in these numbers

- **One asset, one period.** BTCUSDT only, 2021-2026. Crypto has few distinct
  macro regimes in that window, so surviving here means "not yet falsified",
  not "works".
- **In sample by construction.** I chose the timeframes, the expiry window, the
  minimum leg size and the pivot definition. None came from the videos.
- **Multiple testing.** 25 configurations were run. Finding seven that clear a
  threshold is partly what happens when you test 27 of anything.
- **No costs applied.** Breakeven headroom is reported instead, which answers
  the same question more directly for a first pass.
- **Drawdowns are unacceptable as they stand.** S5 and S6 both draw down 45 to
  58%. A real deployment would need position sizing well below 1x, which changes
  the compounding maths the total-return column implies.
- **Instrument mismatch.** TradingLab teaches stocks and forex. Anything keyed to
  a market open, a pre-market gap or a cash session has no clean crypto analogue,
  and those rules were tested against a UTC-midnight session convention.

## Not tested, and why

| Strategy | Videos | Blocker |
|---|---|---|
| Hedge fund order block indicator | 016, 018 | closed source, calculation never disclosed |
| Green/red arrow indicator | 052 | closed source, no rules given |
| The Next Pivot + SSL Hybrid | 064 | SSL Hybrid was rebuilt, but the "Next Pivot" projection that generates the entry is proprietary |
| UT Bot + regression candles | 063 | UT Bot was rebuilt, but the stop references an undefined "black line" and no exit rule is given |
| On-chain reversal zones | 090 | needs ChainExposed unrealised profit/loss data |
| Kullamaggie momentum breakout | 060 | needs a cross-sectional universe of stocks that moved 30-100% in a month |

060 is the one worth returning to. It is a well documented equities momentum
method and probably the most credible strategy in the playlist, and it is
precisely the one a single crypto series cannot evaluate. Testing it needs daily
data for a few hundred US equities. Yahoo Finance is hard rate-limited from this
environment and Stooq sits behind a proof-of-work challenge, so it needs either
an API key or a different data route.

## Reproducing

```
PYTHONPATH=playlist_study/src python3 playlist_study/src/run.py          # everything
PYTHONPATH=playlist_study/src python3 playlist_study/src/run.py S1       # one strategy
```

Sources: `src/data.py` loading and gap handling, `src/indicators.py` including
the rebuilt indicators, `src/conventions.py` for the house rulings on the
ambiguities, `src/strategies.py` for the nine systems with every assumption
marked, `src/backtest.py` for the engine.
