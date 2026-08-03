# How To Combine Price & Volume Using This LEADING Indicator (TSV Trading Strategies)

- video_id: WS3zSvL3H9U
- url: https://www.youtube.com/watch?v=WS3zSvL3H9U
- duration: 12:51
- classification: MULTI-STRATEGY

## Summary

The video teaches Time Segmented Volume (TSV), a volume oscillator that compares intraday volume at specific times against historical averages for the same time period, eliminating market distortions. TSV is a leading indicator showing large-lot vs. small-lot activity. Two main strategies: (1) Divergence trading—detect potential reversals when price and TSV diverge (e.g., higher highs in price but lower highs in TSV indicates distribution); (2) TSV + EMA crossover—identify breakout entries when TSV EMA crosses above centerline (accumulation) at resistance levels. TSV exposes what institutional traders are doing behind price action.

## Instruments and timeframes stated

- markets: stocks, general application [00:00]
- timeframes: examples on 15-minute chart [04:00]; principle applies to all timeframes [02:30]
- sessions/hours: NOT STATED; notes market distortions at open, lunch, close [01:30]

## Indicator: Time Segmented Volume (TSV)

### Calculation and Purpose

"Time Segmented Volume (TSV) is a volume oscillator, and is considered one the best volume oscillators ever written. Its main advantage is the fact it reveals large-lot vs. small-lot activity on the market" [02:30-03:00]

Method: "compares various time segments of both price and volume... segments a stock's price and volume according to specific time intervals... compares the average of only the [specific time] bars over the prior month... to the current [specific time] bar" [03:00-04:00]

"The price and volume data is then compared to uncover periods of accumulation (buying) and distribution (selling)" [03:30]

Zero line: "The baseline represents the zero line" [03:00]

### Advantages over OBV

"Similar to on-balance volume (OBV) because it measures the amount of money flowing in or out of a particular stock. But with a big advantage" [03:00]

"TSV is a leading indicator because its movement is based on both the stock's price and volume" [03:30]

"using time segmented volume will eliminate volume distortions and increase your trading edge" [05:00]

## Strategy 1: TSV Zero-Line Crossover

### Entry trigger (BULLISH)

"When TSV crosses up through the zero line, it signals positive accumulation or buying pressure. This action is considered bullish" [05:30]

### Entry trigger (BEARISH)

"when TSV crosses below the zero line, it indicates distribution or selling pressure, which typically precedes a move down in price" [05:30]

### Claimed performance

Used as a standalone signal: "considered bullish" / "typically precedes" [05:30]

## Strategy 2: TSV Divergence Trading (Price vs. Volume Divergence)

### Negative Divergence (Reversal Down)

Pattern: "price is making successively higher highs while TSV is making successively lower highs, this would constitute a series of negative divergences" [06:00]

Interpretation: "This would be a leading indication of a possible top" [06:00]

Explanation: "the TSV indicator exposes the distribution pattern of the big market players quietly selling the stock even while smaller lot buyers push price up to the final high before the correction" [06:30]

### Positive Divergence (Reversal Up)

Pattern: "price is making successively lower lows while TSV is making successively higher lows, this would constitute a series of positive divergences" [06:30]

Interpretation: "This would be a leading indication of a possible bottom" [06:30]

Explanation: "the TSV indicator reveals the accumulation pattern of the big market players quietly buying the stock even while smaller lot sellers push price down to the final low before the rally up" [06:30-07:00]

Reliability: "Several consecutive divergences increase the reliability factor in trying to pinpoint price reversals" [06:00]

### Entry Logic

Look for: "positive or negative divergences between price and TSV in order to determine potential tops and bottoms" [06:00]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

## Strategy 3: TSV + EMA Crossover (Breakout Entry)

### Indicators and settings

- Time Segmented Volume (TSV) oscillator
- Exponential Moving Average (EMA) applied to TSV
- EMA period: NOT SPECIFIED; speaker notes: "as you increase the value of the moving average, the result is a smoothing effect" [10:00-10:30]

### Context / bias filter

- Price approaching important resistance or support level [10:00]
- Market in accumulation phase (EMA above centerline) for upside breakouts [09:30-10:00]
- Market in distribution phase (EMA below centerline) for downside breakouts [09:30]

### Entry trigger (Upside Breakout)

"If you see a period of accumulation, meaning the moving average above centerline, and you see a new high in the time segmented volume, at an important area of resistance, that's a high probability signal that the breakout could be valid and a future upside move could follow" [09:30-10:00]

Entry: Enter at breakout above resistance with TSV EMA above centerline and rising

### Entry trigger (Downside Breakout)

Inverse of upside: EMA below centerline (distribution) + new low in TSV at support

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Claimed performance

"a high probability signal that the breakout could be valid and a future upside move could follow" [10:00]

"If you've tried some of the conventional ways of day trading breakouts and they aren't working for you, the Time Segmented Volume will serve you better" [10:30]

## Key Insight: Price/Volume Harmony vs. Divergence

"reading price action and volume action on the same exact bars, using time segmented volume to give you the true volume information you need... if price and volume are in harmony or if they are divergent" [04:30-05:00]

Examples of interpretation:
- Large price bar + strong volume = confirmed move (harmony)
- Large price bar + weak volume = caution; move suspect (divergence)
- Strong volume bar = possible end of move or reversal incoming (divergence interpretation)

## Vagueness log

1. UNDEFINED-RULE: "Successively higher/lower highs/lows" — exactly how many swings constitute a series? [06:00]
2. UNDEFINED-PARAM: EMA period for TSV — speaker mentions smoothing tradeoff but no specific value [10:00-10:30]
3. UNDEFINED-RULE: "Important area of resistance/support" — what defines "important"? [10:00]
4. UNDEFINED-RULE: "New high in TSV" — compared to what baseline? Recent period? [10:00]
5. UNDEFINED-PARAM: Time segment definition — 15 minutes used in example, but general use unclear [04:00]
6. UNDEFINED-PARAM: Stop loss NOT specified for any strategy
7. UNDEFINED-PARAM: Profit target NOT specified
8. UNDEFINED-RULE: "Period of accumulation/distribution" — how long? Minimum duration? [09:30]
9. SUBJECTIVE: "High probability signal" — no quantified criteria [10:00]
10. UNDEFINED-RULE: Divergence identification — exact rules for detection not mechanically clear

## Mechanizability

PARTIAL

TSV calculation (compare same-time-period volume averages) can be mechanized given historical data. EMA on TSV is standard. Zero-line crossover is computable. However, gaps prevent full automation: (1) divergence patterns ("successively higher/lower") require defining pattern length; (2) "important resistance/support" lacks objective definition; (3) "new high in TSV" needs a reference baseline; (4) EMA period is not specified; (5) stop and profit targets entirely missing; (6) reversal signal strength is subjective. TSV indicator framework is mechanizable, but trading signals require manual interpretation.

## Notable claims and caveats

- "Many traders ignore volume" [00:00]
- "volume oscillators... provide far more valuable information about what is going on with the stock price before price actually moves" [00:00-00:30]
- "This gives traders a leading indicator that shows the direction of price, breakout moves, momentum runs, and bottoms or tops ahead of price action" [00:00-00:30]
- "Volume has inherent distortions" due to open/lunch/close [01:30]
- "every instrument has considerably different levels of volume" [02:00]
- "The key to getting past these challenges is to use the time segmented volume" [02:30]
- "TSV is a leading indicator" [03:30]
- "the big problem with most technical traders is that they rely too heavily on price and time indicators and don't evaluate volume indicators sufficiently" [07:00-07:30]
- "Price no longer is the most important indicator. A combination of Price, Volume, and Time indicators offer the most reliable, consistent, and leading indication" [07:30]
- "the indicator will have a greater tendency to lag price" as EMA length increases [10:30]
- No specific win rate or Sharpe ratio provided
- No discussion of commissions, spreads, slippage, or transaction costs
