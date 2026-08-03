# RSI vs MFI Trading Strategies (How to Trade with Money Flow Index)

- video_id: bAT6F7x9K8M
- url: https://www.youtube.com/watch?v=bAT6F7x9K8M
- duration: 11:20
- classification: MULTI-STRATEGY

## Summary
This video introduces the Money Flow Index (MFI), a volume-weighted momentum indicator similar to RSI, and presents four distinct trading strategies using it. The video compares MFI to RSI, explains how to interpret MFI signals (overbought/oversold and divergences), and demonstrates progressively refined trading approaches that combine MFI with trend filters and price action confirmation.

## Instruments and timeframes stated
- markets: Stocks (AT&T, Netflix examples [07:00-08:30]), and general application to all markets
- timeframes: NOT STATED for standard strategies; "different timeframes" mentioned for backtesting [10:30]
- sessions/hours: NOT STATED

## Strategy 1: MFI Overbought/Oversold Trading

### Indicators and settings
- MFI: 14-period (default setting) [01:00]
- Overbought levels: above 80 (general), above 90 (more reliable/rare) [02:00, 04:00]
- Oversold levels: below 20 (general), below 10 (more reliable/rare) [02:00, 04:00]

### Context / bias filter
No specific trend filter required for basic approach, but important caveat: "During periods of strong upward trends of downward trends, markets can and will remain in the overbought or oversold areas for weeks or even months." [04:30]

### Entry trigger
"When the MFI is above 90, the price is considered overbought and a reversal or pullback could potentially occur. When the MFI is below 10, the price is considered oversold and a reversal or pullback might be recorded on the market." [04:00]

### Stop loss
NOT STATED (in basic strategy)

### Take profit / exit
NOT STATED (in basic strategy)

### Invalidation / skip conditions
Should not enter blindly on overbought/oversold alone: "you shouldn't blindly enter counter trend positions. You need to pay attention to price action, to recent market swing, to key support and resistance levels and if you spot some sort of confluence, then you should consider entering into a trade." [04:30]

### Claimed performance
NONE CLAIMED

### Vagueness log
1. "Reversal or pullback could potentially occur": NOT DEFINED precisely (UNDEFINED-RULE)
2. Stop loss placement: NOT STATED
3. Take profit target: NOT STATED
4. Position sizing: NOT STATED
5. "Confluence" definition: NOT SPECIFIED (SUBJECTIVE)

### Mechanizability
DISCRETIONARY - While overbought/oversold levels can be mechanically detected, the requirement for additional price action confirmation makes actual entry discretionary.

## Strategy 2: MFI Divergence Trading

### Indicators and settings
- MFI: 14-period (default)
- Detection of price/MFI divergence

### Context / bias filter
Price is making new highs or new lows

### Entry trigger
Bearish divergence: "If the price is making new highs and the MFI fails to make new highs, or falls. This is a bearish divergence and can be used as a sell signal." [05:00]
Bullish divergence: "If the price makes new lows but the MFI fails to set new lows, or rises, this would be a bullish divergence." [05:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
"Could be a leading indication of an upcoming change in the direction of the market" [05:00]
Also: "Since the MFI integrates volume data into it, a divergence between the direction of the indicator and price could be a leading signal." [05:30]

### Vagueness log
1. Definition of "new highs/lows": NOT STATED (recent swing, all-time, recent period) (UNDEFINED-RULE)
2. How much MFI "failure" constitutes a divergence: NOT SPECIFIED (UNDEFINED-PARAM)
3. Stop loss placement: NOT STATED
4. Take profit target: NOT STATED
5. Entry timing after divergence detected: NOT STATED

### Mechanizability
PARTIAL - Divergence detection can be coded (comparing price and MFI extremes), but the criteria for significant divergence are not defined.

## Strategy 3: Combined Overbought/Oversold + Divergence + Trend Line Breakout

### Indicators and settings
- MFI: 7-period (reduced from default 14 for increased sensitivity) [06:00]
- 200-period exponential moving average (trend filter) [06:30]
- Trend lines or channel support/resistance

### Context / bias filter
1. Trend established by 200 EMA direction [06:30]
2. MFI must reach overbought/oversold at least once in recent period [06:00]
3. Divergence between MFI and price must occur [06:30]

### Entry trigger
"First, the money flow index must reach an overbought or oversold area at least once on the chart in the recent trading period. The second step: a divergence between the money flow index and the price must occur during the recent period. I prefer to identify the main trend with a 200-period exponential moving average and I only take signals in the direction of the 200 EMA. Then I search for entries once the price breaks through a recent support or resistance level, a trend line or channel." [06:00-07:00]

Specific rules:
- If price below 200 EMA: take only short signals [06:30]
- If price above 200 EMA: take only long signals [06:30]
- Entry on breakout of trend line/channel [07:00]

### Stop loss
"Your stops should be placed below the recent market swing." [07:30]

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Entry only in direction of 200 EMA trend [06:30]

### Claimed performance
Examples shown on AT&T and Netflix [07:00-08:30] with "several valid entries"

### Vagueness log
1. "Recent trading period" timeframe: NOT DEFINED (UNDEFINED-PARAM)
2. "Recent support or resistance level": SUBJECTIVE
3. Trend line drawing: SUBJECTIVE (requires manual drawing)
4. Take profit target: NOT STATED
5. "Recent market swing" exact definition for stop placement: UNDEFINED-RULE

### Mechanizability
PARTIAL - MFI levels and divergences are computable, 200 EMA is computable, but trend line identification and entry confirmation on breakout require subjective judgment.

## Strategy 4: MFI 50-Level Crossover

### Indicators and settings
- MFI: 50-period (increased from default 14 for decreased sensitivity) [10:00]
- 200-period exponential moving average (trend filter) [10:00]

### Context / bias filter
Trend direction identified by 200 EMA [10:00]

### Entry trigger
"When money flow index crosses above 50 level, this signals buying pressure coming into the market. When money flow index crosses below 50 level, this signals selling pressure." [09:00]
Filter: Only take signals in direction of 200 EMA trend [10:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Only take signals aligned with 200 EMA trend [10:00]

### Claimed performance
"Will offer some good entries, but it also will generate many bad trades" with default 14-period [09:30]
Improvement with 50-period: reduces noise [10:00]

### Vagueness log
1. MFI period optimization: Speaker recommends backtesting: "Play with the periods of the MFI and even the period of the EMA and back test yourself on different timeframes, to find the best settings suited for your trading style." [10:30]
2. Stop loss placement: NOT STATED
3. Take profit target: NOT STATED
4. Position sizing: NOT STATED

### Mechanizability
FULL - MFI 50-level crossovers and 200 EMA direction are both mechanically computable with stated parameters.

## Notable claims and caveats

- MFI is "the volume-weighted RSI" [00:30] - incorporates volume while RSI does not [01:00]
- Typical default calculation uses 14 periods [01:00]
- MFI readings above 80 are overbought, below 20 are oversold, but 90/10 are more reliable [02:00-02:30]
- "Overbought and oversold doesn't necessarily mean the price will reverse, only that the price is near the high or low of its recent price range" [02:00]
- Markets can remain overbought/oversold for "weeks or even months" during strong trends [04:30]
- "MFI should never be used on its own as a trade signal, and must be used in conjunction with other tools of analysis" [05:00]
- Volume is considered a leading indicator by some traders, so MFI may provide signals more timely than RSI [03:00]
- 7-period MFI recommended for increased sensitivity in Strategy 3 [06:00]
- 50-period MFI recommended for decreased sensitivity and noise reduction in Strategy 4 [10:00]
- Speaker recommends backtesting different MFI and EMA periods for individual trading styles [10:30]
- No discussion of transaction costs, spreads, slippage, or commissions
