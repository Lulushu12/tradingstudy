# Forward Test Postmortem — MCB Clone Discretionary LTF System

Test window: 2026-08-18 20:30 → 2026-08-25 16:15 (UTC+3), Breakout prop account, $10,000 start.
51 completed trades reconstructed from full order history (`trades_final.csv`).
Universe: AVAX, BTC, DOGE, ETH, LINK, SOL, SUI, XRP. Rules: dual-TF MCB Clone, HTF WT ±53 bias,
MC basic-strategy entries, 5-candle pivot stop (min 0.4%), R:R 1:1, $50 risk. Fees verified from
platform fill: 0.04% per side (0.08% round trip) — 10x the assumed 0.004%.

## Headline

| Metric | Value |
|---|---|
| Gross P&L | +$286.19 |
| Fees | −$273.55 (96% of gross) |
| **Net P&L** | **+$12.64 (+0.13%)** |
| Win rate | 25/51 (49%) |
| Profit factor | 1.01 |
| Peak equity | $10,383 (8/24 11:26), −$370 given back after |
| Longs | +$329 net (22/36 wins, 61%) |
| Shorts | −$317 net (4/15 wins, 27%), Fisher p ≈ 0.026 |
| Standard-size trades only | −$4.70 net |

## Findings

1. **The system never had positive expectancy; the rally masked it.** Breakeven win rate at $50
   risk, 1:1 R:R, ~$5.36 avg fee is **55.4%**. Realized: 49% — during one of the strongest alt
   weeks of the summer (every pair +18–47%, mean pairwise 1h correlation 0.73). The green period
   was long-side regime beta; the "failure" was the rally stalling (8/22–8/25 daily returns flat
   to negative), not a change in the system.

2. **Fees were mis-specified 10x, so every fee-derived rule was miscalibrated.** The 0.4% minimum
   stop was designed to prevent "fee chop" at 0.004%/side. At the real 0.04%/side, a 0.4% stop
   surrenders 20% of risk per trade to fees; the median stop (0.77%) surrenders 10%. Low-timeframe
   trading at 1:1 under this fee schedule requires a sustained 55–60% win rate.

3. **Shorts were the only statistically significant pattern — and the bias behind them does not
   survive a timeframe-robustness check.** The chart timeframe per trade is unknown (unlogged,
   unremembered), so wt2 was computed at every short's entry across the full candidate HTF ladder
   (15m, 30m, 1H, 2H, 4H, OKX feed). Result: 1 of 15 shorts had wt2 < −53 on ANY of the five
   timeframes (n33, LINK 8/23, 1H). The 8/23 cluster (n34-37) sits at −45..−48 on 1H/2H —
   borderline; a different feed or reading wt1 could flip those to compliant. Every short before
   8/22 was unambiguous: no candidate timeframe anywhere near −53 during the rally leg. During the
   test week only 6.3% of all 15m/30m bars across all pairs printed below −53, so even a
   deliberate LTF hunt rarely found a bearish reading. Trader confirms probable signal-shopping;
   because the timeframe was never logged, the bias rule is unauditable even by its author — a
   rule that cannot be checked after the fact cannot constrain behavior before it.

4. **The give-back was regime + tilt, concentrated in 16 hours.** From the 8/24 peak: two
   counter-trend shorts (AVAX, XRP) lost overnight; two longs (ETH, BTC) stopped on the week's
   first ~1% pullback; then a double-size SUI long (−$105) on the day's weakest coin, then another
   SUI long (−$27). Six straight losses, −$365 net. One-third of the give-back was the single
   oversized trade.

5. **Execution discipline was otherwise decent.** Stop-out losses cluster $41–54 (consistent $50
   risk); 21/23 stops respected the 0.4% minimum. Flagged: 5 emotional double-size trades
   (n16, 36, 37, 38, 50 — net +$17, positive only by luck), 1 misclick (n10: 0.24 BTC vs usual
   0.06–0.15, 0.14% stop, stopped same minute), and churn clusters (5 LINK trades in 4h on 8/23,
   3 positions in 5 minutes at 15:55–16:00).

## Verdict

The forward test did not "go bad at some point." Net of real fees it was breakeven the whole way:
a coin flip paying 10% rake, riding a rally tailwind on the long side, bleeding on counter-trend
shorts, with the residual noise (streaks) read as signal. At standard size the honest result is
−$4.70 over 51 trades. The 4%-then-give-back shape was: tailwind on, tailwind off.

## What would have to change before another test

1. Fee-aware economics: with 0.08% RT, either much wider stops (higher TF) so fees are <3% of
   risk, or R:R above 1:1, or both. Recompute breakeven WR before trading, not after.
2. Shorts require a mechanical <−53 HTF bias check. This week 0/15 would have qualified.
3. Kill the timeframe freedom: pre-commit chart TF per session; log setup screenshot at entry.
4. Size lock at $50 and a stop-trading rule after 3 consecutive losses.
5. Sample honesty: even the long side (+$329, 61%) is one week, one regime, statistically
   unproven. A future test needs pre-committed sample size and kill thresholds.
