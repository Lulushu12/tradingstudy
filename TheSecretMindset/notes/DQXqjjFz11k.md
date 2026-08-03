# Best Indicator To Trade Multiple Time Frame Divergences | Ultimate Oscillator Forex & Stock Strategy

- video_id: DQXqjjFz11k
- url: https://www.youtube.com/watch?v=DQXqjjFz11k
- duration: 11:47
- classification: STRATEGY

## Summary

This video teaches a trading strategy based on the Ultimate Oscillator, a multi-timeframe momentum indicator designed by Larry Williams to reduce false divergences. The strategy uses a three-step method: identify a bullish divergence (price makes lower low while indicator makes higher low) from oversold territory (below 30), then enter when the oscillator breaks above the divergence high. An alternative, more aggressive entry uses the 50-level crossover. Sell signals follow the inverse logic with bearish divergences from overbought territory (above 70). The oscillator uses default settings of 7-period, 14-period, and 28-period lookbacks, which can be adjusted for different market volatility.

## Instruments and timeframes stated

- markets: Forex and stocks mentioned (example security not named) [title]
- timeframes: "Intraday, daily, weekly or even monthly charts" [09:30]; timeframe-specific parameter adjustments: (4,8,16) for more sensitivity on shorter timeframes [10:00], (7,14,28) default [01:00]
- sessions/hours: NOT STATED

## Strategy 1: Ultimate Oscillator Divergence Trading

### Indicators and settings

**Ultimate Oscillator:**
- Parameters: 7 (short-term), 14 (intermediate-term), 28 (long-term) [01:00-01:30]
- Range: 0 to 100 [03:00-03:30]
- Overbought: above 70 [03:00-03:30]
- Oversold: below 30 [03:00-03:30]

**Formula [00:30-01:30]:**
1. Calculates buying pressure: "subtracting the close from the low or the prior close, whichever of the two is the lowest" [02:00]
2. Measures buying pressure relative to true range [01:00-01:30]
3. Creates averages based on three timeframes (7, 14, 28) [01:00-01:30]
4. Creates weighted average of the three averages [01:00-01:30]
5. "The short-term period is weighted more heavily in the ultimate oscillator equation" [01:30]

### Context / bias filter

No specific context filter stated. Strategy can be applied on "intraday, daily, weekly or even monthly charts" [09:30].

### Entry trigger

#### Buy Signal - Three-Step Method [04:30-07:00]:

**Step 1: Bullish Divergence Must Form [04:30-05:00]**
"Price makes a lower low but the indicator is at a higher low" [04:30-05:00]. The higher low in the oscillator shows less downside momentum [06:00].

**Step 2: First Low Below 30 [04:30-05:00]**
"The first low in the divergence (the lower one) must have been below 30. This means the divergence started from oversold territory and is more likely to result in an upside price reversal" [04:30-05:00].

**Step 3: Indicator Rises Above Divergence High [05:00]**
"The ultimate oscillator must rise above the divergence high. The divergence high is the high point between the two lows of the divergence" [05:00-05:30].

**Example [06:00-06:30]:**
"We have the bullish divergence forming between the indicator and security price. This means the ultimate oscillator formed a higher low as price recorded a lower low...The low of the bullish divergence was below 30...The oscillator rose above the high of the bullish divergence" [06:00-06:30].

**Alternative Entry (More Aggressive) [06:30-07:00]:**
"An alternative entry I often use is a move above 50 level" [06:30-07:00]. "I try to skip this step, and enter earlier in my trades" [08:30-09:00].

#### Sell Signal - Three-Step Method [05:00-08:30]:

**Step 1: Bearish Divergence Must Form [05:00-05:30]**
"Price makes a higher high but the indicator is at a lower high" [05:00-05:30]. The lower high in the oscillator shows less upside momentum [07:30].

**Step 2: First High Above 70 [05:00-05:30]**
"The first high in the divergence (the higher one) must be above 70. This means the divergence started from overbought territory and is more likely to result in a downside price reversal" [05:00-05:30].

**Step 3: Indicator Drops Below Divergence Low [05:30]**
"The ultimate oscillator must drop below the divergence low. The divergence low is the low point between the two highs of the divergence" [05:30].

**Example [07:30-08:00]**
"The ultimate oscillator forms a lower high as price posted a higher high...The high of the bearish divergence is above 70...The oscillator falls below the low of the bearish divergence to confirm a reversal" [07:30-08:00].

**Alternative Entry (More Aggressive) [07:30-08:00]**
"If you want an earlier entry, pull the trigger when the ultimate oscillators moves below its 50 level" [07:30-08:00].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

1. **Unconfirmed Divergence:** If the indicator does not break the divergence high (bullish) or divergence low (bearish), the signal is not confirmed [08:00-08:30]. "An entry based on the 50 level would have brought a loss, because the price reversed and continued its uptrend" [08:30-09:00].

2. **False Divergence (Reversal Does Not Occur):** "A divergence is not present at all price reversal points. The market can reverse without any divergence. Also, a reversal won't always occur from overbought or oversold territory" [10:30-11:00].

3. **Poor Entry Timing:** "Waiting for the oscillator to move above the divergence high (bullish divergence) or below the divergence low (bearish divergence) could mean poor entry point as the price may have already run significantly in the reversal direction" [10:30-11:00].

### Claimed performance

No specific win rate, R-multiple, or profit claims stated. General claim: "The multiple timeframe objective seeks to avoid the pitfalls of other oscillators. Many momentum oscillators surge at the beginning of a strong advance, only to form a bearish divergence as the advance continues" [00:00-00:30]. "By using the weighted average of three different timeframes the indicator has less volatility and fewer trade signals compared to other oscillators that rely on a single timeframe" [02:30-03:00].

### Vagueness log

1. "Bullish divergence": UNDEFINED-RULE (how many candles/bars between the two lows? how many must separate them?)
2. "Bearish divergence": UNDEFINED-RULE (same as above for highs)
3. "Divergence high": UNDEFINED-RULE (the exact high between the two lows—is it the close of the bar? the wick? exact price?)
4. "Divergence low": UNDEFINED-RULE (same clarification)
5. "Rises above" / "drops below": UNDEFINED-RULE (market order? limit order? at close? at any price?)
6. "Oscillator moved to oversold levels": VISUAL-ONLY (below 30 is quantified, but the visual identification of where to draw divergence levels requires chart inspection)
7. Stop loss: NOT STATED
8. Take profit: NOT STATED
9. Position sizing: NOT STATED
10. Confirmation on which timeframe: UNDEFINED-RULE (indicator is on one timeframe, but multiple timeframes mentioned; which timeframe for entry decision?)

### Mechanizability

FULL for divergence detection and oscillator calculation if specific parameters are defined. The Ultimate Oscillator calculation is standard and can be computed from OHLCV data using the stated formula. Divergence detection (lower low in price with higher low in indicator, or vice versa) is mechanically computable. However, the entry mechanics (market order vs. limit, exact entry price) and stop/target placement are not specified, making the strategy incomplete for backtesting without additional assumptions.

---

## Timeframe Parameter Adjustments [09:30-10:30]

"It is sometimes necessary to adjust its settings to generate overbought or oversold readings, which are part of the buy and sell signals" [09:30].

**For Higher Sensitivity (Shorter Timeframes/Lower Volatility):**
"If you plot the oscillator and there are no overbought or oversold readings, you could try shortening the timeframe to (4,8,16) to increase sensitivity" [10:00].

**For Lower Sensitivity (Longer Timeframes/Higher Volatility):**
"The opposite is true for securities and stocks with high volatility. It is sometimes necessary to lengthen the timeframes to reduce sensitivity and the number of signals" [10:00-10:30].

---

## Divergence Interpretation [02:30-03:00]

"The ultimate oscillator measures momentum for three distinct timeframes. The second timeframe is double compared to the first, and the third timeframe is double compared to the second. Even though the shortest timeframe carries the most weight, the longest timeframe is not ignored, which should reduce the number of false divergences" [02:30-03:00].

---

## Notable claims and caveats

- "The ultimate oscillator is designed to capture momentum across three different timeframes...attempts to correct [the] fault [of single-timeframe oscillators] by incorporating longer timeframes" [00:00-00:30].
- "By combining three separate time periods...the ultimate oscillator tends to peak when price peaks" [01:30].
- "Also, I prefer this indicator because the ultimately oscillator generates fewer divergence signals than other oscillators due to its multi-timeframe construction, so the market noise is greatly reduced" [03:00].
- "Williams developed the ultimate oscillator to incorporate multiple timeframes to smooth out the indicator's movements and provide a more reliable indicator of momentum, with fewer false divergences" [03:30-04:00].
- **Important limitation:** "The multiple timeframe trading method for the indicator may help eliminate some poor trades, it also eliminates many good ones" [10:30].
- "A divergence is not present at all price reversal points. The market can reverse without any divergence" [10:30].
- "A reversal won't always occur from overbought or oversold territory" [10:30-11:00].
- "Waiting for the oscillator to move above the divergence high (bullish divergence) or below the divergence low (bearish divergence) could mean poor entry point as the price may have already run significantly in the reversal direction" [10:30-11:00].
- "The ultimate oscillator, like all indicators, has its own limitations" [10:30].
- "The ultimate oscillator shouldn't be used in isolation, but rather as part of a complete trading plan. And such a plan must include other forms of analysis such as price action, other technical indicators, and even fundamental analysis" [11:00-11:30].
- No mention of costs, spread, slippage, or commission.
- No mention of drawdown, losing streaks, or risk management specifics.

## Video Classification Note

This is a complete STRATEGY with a clear, mechanizable core (Ultimate Oscillator divergence detection on specified parameters). The strategy can be coded with the stated parameters (7, 14, 28) and overbought/oversold levels (70/30), and divergence detection is computable. However, entry mechanics (order type, exact entry price, confirmation timeframe) and stop/target placement are not specified, requiring trader discretion or additional assumptions for backtesting.
