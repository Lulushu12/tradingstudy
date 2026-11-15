# Gate 1 Report

Phase 1 is complete: every feature in brief section 5 is implemented, tested for look-ahead, and the MCB clone is
validated. The proposals are in `PROTOCOL.md` (draft). Nothing is frozen until approval.

## 1. Feature validation

**WaveTrend: validated.** Against the real MCB exports (BTC 5m, 15m, 1h, 4h, 1D, 1W, dev rows only), mean absolute
error <= 0.0001 to 0.007 and correlation 1.0000; cross dots match 100% (same count, same bars, same colour) on every
timeframe. One data trap found and fixed: TradingView recomputes indicators from the start of each exported chunk,
so the first rows of every export file carry warm-up error. Those rows are excluded.

**Money Flow: real MCB is best matched by your clone's formula computed on Heikin-Ashi candles, without the outer EMA.**

| Formula | Corr with real MCB | Same sign | Same direction bar to bar |
|---|---|---|---|
| Clone formula on Heikin-Ashi, no outer EMA (chosen) | 0.989 to 0.995 | 94 to 96% | 92 to 94% |
| MCB_Clone_v1.pine as coded | 0.96 to 0.97 | 88 to 90% | 84 to 85% |
| Brief's reverse-engineered HTF version (3x TF, developing candle) | 0.89 to 0.91 | 85 to 87% | 71 to 78% |
| Brief's "clone formula" (high - low denominator) | 0.82 to 0.86 | 79 to 83% | 65 to 67% |
| Fixed 3H HTF hypothesis | 0.27 to 0.69 | 59 to 74% | |

Fitted on BTC 15m 2022-2023 only; the chosen formula holds on 2024-2025 and on every other timeframe. The XRP
"HA SHA MFI" export turned out to come from your clone, not MCB (reproduced exactly), so it validates the port only.
Remaining gap to MCB: about 5% of bars disagree on sign, almost all near zero. Divergence pivots will occasionally
differ from what you saw on MCB.

**Look-ahead: tested three ways.**
1. Every feature is recomputed with the future cut off and with the future replaced by a different random walk;
   past values must not change.
2. End-to-end on real BTC data: all ~155 feature columns and all range-flip events are rebuilt with every timeframe
   truncated to bars closed by a cut time; every earlier value is identical.
3. Mutation test: a deliberate one-bar leak planted in WaveTrend, and separately in the zigzag, makes the test fail.
   So the test can actually catch leaks.

60 automated tests pass.

## 2. Census (dev, counts only, no outcomes)

Events per day across all 9 coins:

| Event | 6m | 15m | 24m | 1h |
|---|---|---|---|---|
| WT buy/sell signal (dots beyond +/-53) | 103 | 41 | 25 | 10 |
| Divergence stack, confirmed, 11-bar window | 31 | 12.4 | 7.6 | 3.3 |
| Divergence stack, front-run, 11-bar window | 26 | 10.5 | 6.4 | 2.8 |
| Range flip, confirmed, k = 3 | 1.5 | 0.6 | 0.4 | 0.15 |
| Range flip, confirmed, k = 2 | 6.6 | 2.7 | 1.7 | 0.7 |

Your target is about 1 per day. The divergence stack needs strong filtering to get there, which is what discovery is
for. The range flip at 15m is near target on its own.

Fee per trade in R (median across coins): at 1.5 x ATR stop, 6m 0.15R, 15m 0.09R, 24m 0.07R, 1h 0.04R.
At 1.0 x ATR, 6m 0.23R and 15m 0.14R, which is why I propose dropping the 1.0 x ATR stop.

Trend regime shares (15m, mean across coins): R1 up 43% / down 53% / mixed 4%; R2 trending up 22% / down 29% /
no trend 49%; R3 up 37% / down 43% / mixed 20%.

## 3. Concepts used in the protocol (plain language)

- **Walk-forward validation:** train on the past, test on the next block of time you have not touched, then roll
  forward and repeat. Only the test blocks count as evidence. It mimics how you would actually have used the rules.
- **Purging and embargo:** a trade lasts up to a day, so a training trade near the edge of a test block can "see" the
  same price action as the first test trades. Purging deletes those overlapping training trades; the embargo adds a
  7-day buffer so nothing leaks across the boundary.
- **Deflated Sharpe ratio:** if you try 800 configurations, the best one looks good by luck alone. The deflated
  Sharpe asks how likely the winner's result is to be real once you account for how many things were tried. 0.95 means
  roughly a 95% probability that the true edge is above zero after that correction.
- **Block bootstrap Monte Carlo:** reshuffle the out-of-sample trades in whole-day blocks (keeping same-day clustering)
  thousands of times to see the range of equity paths, and how often each path breaches the 3% daily or 6% max limit.

## 4. What worries me (said directly)

1. **The holdout is contaminated on every coin**, not just BTC, because you traded several of them during it. A pass
   is weaker evidence than it would normally be. I cannot fix this; I can only make sure the verdict says so.
2. **The range flip is a small sample.** At k = 3 there are about 0.6 confirmed events a day across all coins on 15m,
   roughly 850 in the whole dev period before any filter or label. Split across 6 folds and then filtered, the
   statistics will be thin. k = 2 gives 4x more events but noisier ranges.
3. **Levels are everywhere.** With 7 timeframes x (4 Fib ratios x 3 legs + 12 S/R + range bounds + profiles), the
   median bar has 4 levels within 0.5 ATR and a Fib level within 0.11 ATR. "Price is at a level" is almost always true,
   so as defined it carries little information. This is the mechanical version of the hindsight problem in drawing
   levels by hand. I propose a tighter band and counting distinct level TYPES; expect confluence to disappoint anyway.
4. **Several divergence details are my definitions, not your words** (dot level = wt2 at the cross; price = the wave's
   extreme wick; front-run uses wt2 at the turn bar as the provisional level). WT front-run fires less often than
   confirmed because wt2 is still sinking at the turn. If you trade it differently, tell me now; after Gate 1 these freeze.
5. **800 configurations is a lot.** The deflated Sharpe will demand roughly +0.10R per trade with ~1,000 trades to clear.
   That is deliberately hard. A smaller budget makes the bar only a little lower (it grows with the log of the count).

## 5. Decisions needed (details in PROTOCOL.md)

1. Approve the splits and the contamination caveat.
2. Approve warm-up (pre-2022 prices for indicator warm-up only, never for labels or statistics).
3. Approve the walk-forward scheme (6 folds, purge, 7-day embargo, rule-stability requirement).
4. Approve the execution model: limit at close live 1 bar, trade-through fills, stop-wins-ties, slippage per coin.
5. Risk guards: max 1 position per coin, max 3 account-wide, stop new entries for the day at -2% realized. Yes or no?
6. Daily reset at 00:00 UTC?
7. Labels: drop the 1.0 x ATR stop; 6m only at 2.0 x ATR.
8. Trend regimes: R1 (4h EMA200 direction) and R2 (4h ADX strength).
9. Range parameters: tolerance 1.0 ATR, height 2 to 12 ATR (chosen on event counts, not outcomes).
10. Confluence: band 0.25 x execution ATR plus distinct-type count.
11. Search grids, budget of 800, success criteria S1 to S10, holdout and kill criteria.
