# I Stopped Overcomplicating SMC, Now I Only Use This Trading Strategy

- video_id: z3TBWjnHRqg
- url: https://www.youtube.com/watch?v=z3TBWjnHRqg
- duration: 24:43
- classification: STRATEGY

## Summary

This video teaches a Smart Money Order Block trading system based on four confluent conditions: supply/demand zones that cause a break of structure, fair value gaps, pivot point alignment, and liquidity runs. The trader demonstrates how to identify high-probability entries on both short and higher timeframes (5-min to H4) by layering these filters together, with emphasis on using "fresh" zones created recently rather than old institutional order blocks. The strategy aims to achieve precise entries with minimal stop losses and substantial risk-reward ratios.

## Instruments and timeframes stated

- markets: S&P, USD CAD, NAS100, Apple (AAPL), USDJPY, EURJPY (specific examples; general markets NOT STATED)
- timeframes: 5-min, H4 (4-hour mentioned in examples; NOT STATED as fixed requirement)
- sessions/hours: NOT STATED

## Strategy 1: Smart Money Order Block Trading System

### Indicators and settings

- Supply/Demand zones: visual identification based on "compact consolidation areas situated between strong and sudden price movements" [04:00-04:30]
- Fair Value Gap (FVG): "sequence of three candles showing significant buying or selling, ideally in the same direction" with "gap emerges between the wick of the first candle and the wick of the last candle" [05:30-06:00]
- Pivot Points: "calculated as an average of prices from the performance of a market in the prior trading period" [07:30]; specific period for calculation NOT STATED
- Break of Structure (BOS): "break above a previous higher high in an uptrend, or a break below a lower low in a downtrend" [04:30-05:00]
- Liquidity run: visual observation of price spikes; measurement method NOT STATED [09:00-09:30]

### Context / bias filter

Four conditions must be met for a valid setup [03:00-03:30]:
1. Supply/demand zone must cause a break of structure or change of character [03:00]
2. Fair Value Gap must exist right after the supply or demand area [05:00-05:30]
3. Pivot point must offer additional confluence (pivot, S1, R1, etc.) at or near the zone [07:00-07:30]
4. Liquidity run must trap traders on the opposite side of your trade (optional but increases probability) [08:30-09:00]

Zone freshness is critical: "strongest entry points occur when price retracts to a supply or demand zone for the first time after its creation" [19:30-20:00]. Older zones are unreliable because "why would banks wait months to finish trades" [20:30-22:00].

### Entry trigger

For a buy trade: "You place a limit order or enter directly at the top of the demand level" when all four conditions are met [12:00-12:30]. Entry can also be refined using lower timeframe confirmation like "a change of character to the downside, maybe you find another fair value gap to initiate a short position" [23:30-24:00].

For a sell trade: "You sell at the bottom of the supply level" when conditions are met [12:30-13:00].

### Stop loss

- Buy trades: "slightly below the zone" [12:00]
- Sell trades: "slightly above the zone" [12:30]
- "On the 5-min time frame, so the stop loss shouldn't be too wide, and in most cases, you'll get a decent risk to reward ratio on your trades" [12:00-12:30]

Exact distance from zone boundary NOT STATED.

### Take profit / exit

- Buy targets: "next major supply level or at a recent swing high, or even at a pivot point" [12:00-12:30]
- Sell targets: "next major demand level or at a recent swing low, or at a pivot point" [12:30-13:00]

For higher timeframes like H4, targets can shift based on multi-day structure: "at the next major demand level on its way down, or at a recent low, or a pivot point" [15:30-16:00].

### Invalidation / skip conditions

- If you "don't see a liquidity run, trapping buyers, so this isn't an A+ setup" but the trade can still be taken as weaker [23:00-23:30]
- Zone is invalidated if it is older and banks have "already moved on, took their profits" [22:00-22:30]
- If you "placed the sell order at the bottom of the supply zone, and the stop loss above it, you would have probably lost the trade" when conditions shift [23:30-24:00]
- Specific age threshold for "too old" NOT STATED

### Claimed performance

"If you follow this approach you will achieve remarkably precise entries, with minimal stop losses while targeting substantial rewards" [00:00]. "These consolidations often precede strong price movements" [00:30]. No win rate, R multiple, or profit percentage stated. Example trades shown but no backtested statistics provided.

### Vagueness log

1. Supply/demand zone identification is VISUAL-ONLY: defined only as "compact consolidation areas situated between strong and sudden price movements" [04:00-04:30], not computable from OHLCV alone
2. Fair Value Gap wick-to-wick gap threshold is UNDEFINED-PARAM: "gap emerges between wick of first candle and wick of last candle" but minimum gap size NOT STATED [05:30-06:00]
3. "Slightly below/above the zone" for stop placement is UNDEFINED-PARAM: no specific distance or number of pips/points given
4. "Change of character" is UNDEFINED-RULE: mentioned as alternative to BOS but not objectively defined [04:30]
5. Pivot point calculation period is UNDEFINED-PARAM: "prior trading period" could mean daily, weekly, or other; context-dependent
6. Liquidity run identification is VISUAL-ONLY: described as price spike but no objective threshold or volume confirmation method stated [09:00-09:30]
7. Zone "freshness" time threshold is UNDEFINED-PARAM: "newer is better" but no guidance on how recent (hours? days? weeks?) [19:30-22:00]
8. "Minor break of structure" versus significant BOS distinction is SUBJECTIVE [18:00, 18:30]

### Mechanizability

PARTIAL - The overall structure is mechanizable: identify consolidation patterns, verify BOS occurred, detect 3-candle gap sequences, check pivot alignment. However, multiple core gaps prevent full automation: (1) identifying valid supply/demand consolidations requires distinguishing them from random price action; (2) liquidity runs are defined by visual spikes with no volume or magnitude threshold; (3) "change of character" is subjective; (4) zone freshness impact on probability is stated qualitatively but not quantified; (5) exact stop placement distance from zone edge requires judgment. A partial implementation could code BOS and gap detection but would fail on visual pattern recognition.

## Notable claims and caveats

The speaker emphasizes that "you will encounter losing trades even when all 4 conditions are met" [19:00-19:30], making clear this is not a guaranteed system. He critiques "traditional retail trading methods, like relying on trend lines and chart patterns" as "less effective" [09:30-10:00] because institutions exploit clustered stop losses. He recommends moving to lower timeframes for additional confirmation to "avoid losing trades" [23:30-24:00] but acknowledges this adds complexity.

The speaker never mentions trading costs, spreads, slippage, or commissions. Risk management is mentioned only in general terms ("if your risk management is on point, there's nothing to worry about in the long term" [24:00-24:30]) without specific position sizing guidance.
