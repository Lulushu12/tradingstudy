# Explosive Ichimoku Renko Trading Strategy (How To Swing Trade Stocks Like A Samurai)

- video_id: M0flnBqjVzU
- url: https://www.youtube.com/watch?v=M0flnBqjVzU
- duration: 10:53
- classification: STRATEGY

## Summary

This video presents a swing trading strategy combining Renko chart analysis with Ichimoku cloud and lagging span indicators. Renko bricks (set to 100-point increments) filter out time-based noise and price action. Entry signals require three simultaneous conditions: (1) a new colored Renko bar in the trend direction, (2) a wide Kumo cloud of the same color, and (3) lagging span confirmation on the correct side of the cloud. The strategy emphasizes avoiding trading inside the cloud, waiting for price to establish clear trends (staying above/below cloud for extended periods), and requires at least 2-3 brick corrections before re-entering long positions. Choppy markets with lagging span oscillating through the cloud are avoided.

## Instruments and timeframes stated
- markets: verbatim: "Stocks; examples: Tesla"
- timeframes: described as swing trading style [06:30]; NOT STATED exactly; implied intraday to daily based on 100-point Renko bricks
- sessions/hours: NOT STATED

## Strategy 1: Ichimoku + Renko Cloud Trend Following

### Indicators and settings
- Renko chart: brick size: 100 points [01:30]
- Ichimoku indicators used: Kumo cloud (span A and span B), Lagging span [02:00-02:30]
- Ichimoku parameters: NOT STATED (default assumed: span A 9-period, span B 26-period, lagging span plotted 26 periods back)

### Context / bias filter
Identify main trend direction using Kumo cloud and lagging span:

Bullish bias: [04:00-04:30] "When the price enters the Kumo cloud and breaks its upper wall upward, we have a bullish trend"

Bearish bias: [04:00-04:30] "When the price enters the Kumo and breaks its lower wall downward, we have a bearish trend"

Cloud quality assessment: [03:00-03:30]
- "the longer the price stays below/above the Kumo cloud, the stronger the trend is"
- "When the cloud is wide, the expected support or resistance is strong"
- "When the cloud is thin, the expected support/resistance is weak"
- "you should never trade inside the Kumo cloud"

### Entry trigger
Three conditions must be met simultaneously for buy entry [05:00-05:30]:
1. "a new green Renko bar appears above the Kumo cloud"
2. "The Kumo cloud is green and wide" (preferably)
3. "the lagging span is above the Kumo cloud"

Three conditions must be met simultaneously for sell entry [05:00-05:30]:
1. "A new red Renko bar appears below the Kumo cloud"
2. "The Kumo cloud is red and preferably wide"
3. "the lagging span is below the Kumo cloud"

[06:00-06:30] Example entries: "a possible buy around here, another one here, riskier because the market hasn't corrected much, another one here, right about the previous support level, also confirmed by the lagging span, another entry here, after the market found support from the previous breakout level, and another one here after a small pullback."

### Stop loss
[04:00-04:30] "We use the 100 Renko brick to identify key support/resistance levels, to determine the market trends and to place our stop-loss and take-profit targets"

Implied: Stop placed below previous Renko support or above previous Renko resistance based on 100-point brick structure. Exact placement NOT EXPLICITLY STATED.

### Take profit / exit
[04:00-04:30] "and take-profit targets" mentioned but NOT SPECIFIED in mechanical terms.

[07:30-08:00] "I personally like to see a correction of at least 2 or 3 bricks before re-entering." — Suggests take-profit objectives based on 2-3 brick moves.

[08:00-08:30] "from now all you have to do is to manage the trend accordingly" — Exit management is discretionary based on ongoing trend confirmation.

### Invalidation / skip conditions
[03:30-04:00] "when the price trades inside the Kumo, no matter if you anticipate that it will break in one direction, you must stay disciplined and wait for the price to exit the cloud."

[09:00-09:30] "If I see the lagging span that is going up and down though the cloud, I read this as market indecision, and I ignore the setup and search for better entries." — Skip if lagging span oscillates through cloud.

[09:30-10:00] "I want to see consistent red, or consisted green. I don't want to see the cloud changing its color often." — Skip if Kumo changes color frequently.

[10:00-10:30] "Look how choppy the market seems. First the Renko bars are unable to record higher highs or higher lows, or lower lows and lower highs, the ultimate definition of a trend. But they also cut though the cloud easily." — Skip if Renko bars are choppy and cloud is penetrated repeatedly without conviction.

### Claimed performance
NONE EXPLICITLY CLAIMED. Implied positive results ("a great one" [07:30]; "it was a losing trade, or a breakeven trade at most" [07:00-07:30] for a counterexample).

### Vagueness log
1. UNDEFINED-RULE: "new green Renko bar appears above the Kumo" — unclear if entry is on close of the bar or immediately upon formation [05:00-05:30].
2. UNDEFINED-RULE: "Kumo cloud is green and wide" — width threshold NOT SPECIFIED; no quantification [05:00-05:30].
3. UNDEFINED-RULE: "wide" cloud vs "thin" cloud — no specific measurement given [03:00-03:30].
4. UNDEFINED-RULE: "longer the price stays below/above the Kumo" — no timeframe or brick count specified [03:00-03:30].
5. UNDEFINED-PARAM: Stop loss placement: "key support/resistance levels" from Renko NOT mechanically defined; exact brick count or points NOT STATED [04:00-04:30].
6. UNDEFINED-PARAM: Take profit target: NOT SPECIFIED beyond general "2 or 3 brick correction" [07:30-08:00]; no concrete profit target.
7. UNDEFINED-RULE: "Renko bars are unable to record higher highs or lower lows" — what threshold defines "unable"? [10:00-10:30]
8. SUBJECTIVE: "manage the trend accordingly" [08:00-08:30] is discretionary; no mechanical exit rules.
9. UNDEFINED-RULE: Lagging span "going up and down though the cloud" — how many crosses trigger indecision? [09:00-09:30]

### Mechanizability
PARTIAL. Renko chart brick creation (100-point increments) is mechanizable if OHLCV data is available. Ichimoku cloud calculation is mechanizable (parameters needed for span A and B). Lagging span is mechanizable. However:
- "Green" vs "Red" cloud requires Ichimoku spanning line comparison (mechanizable)
- Cloud "width" assessment lacks quantification
- Entry bar detection (new bar above/below cloud) is mechanizable
- "Lagging span oscillation" detection requires defining oscillation criteria (number of crosses)
- Stop and take profit placement lack specific mechanical rules
- Skip conditions depend on subjective trend quality assessment

A skeleton can be coded (STC crosses cloud, lagging span confirms), but full mechanization requires specification of cloud width thresholds and oscillation detection rules.

## Notable claims and caveats

- [00:00-00:30] "those 2 techniques combined will give you some decent entries and will filter a lot of market noise"
- [00:30-01:00] "Renko charts eliminate the time component of trading and only focus on the price itself. Potentially, Renko charts can filter out a lot of the market noise and display the price in a much more organized way that is simpler to interpret."
- [01:30] "For this strategy, we'll use 100 points for one brick, because i want to eliminate the noise as much as possible."
- [06:30] "Remember that these are 100 point bricks, so this is similar to a swing trading style."
- [07:00-07:30] Example of losing trade: "Yes, it was a losing trade, or a breakeven trade at most, because the market formed another green brick and reversed."
- [08:30-09:00] "In real time, we have contradicting signals. So the price broke through the cloud, which is still red, and the lagging span also made its way on the other side of the cloud. So, at the time being, no short here for now."
- [09:00-09:30] "If I see the lagging span that is going up and down though the cloud, I read this as market indecision"
- [10:30] Emphasis on filtering: "So, pay attention to these filters because they can make the difference between a bad trade and a good one."

No mention of transaction costs, spread, slippage, or commission. No explicit drawdown or losing streak warnings, though examples of losing/breakeven trades are mentioned. The strategy requires patience and discipline to wait for clean setups and avoid trading inside the cloud.
