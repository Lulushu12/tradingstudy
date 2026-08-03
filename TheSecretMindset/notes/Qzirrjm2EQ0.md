# I Discovered The "IDEAL ENTRY LEVEL" For Day Trading (Strategies REVEALED)

- video_id: Qzirrjm2EQ0
- url: https://www.youtube.com/watch?v=Qzirrjm2EQ0
- duration: 13:45
- classification: MULTI-STRATEGY

## Summary
The video teaches day trading strategies centered on using the daily open price as a key support/resistance reference level. Three distinct strategies are presented: (1) Pin bar rejection at the daily open level in trending contexts, (2) EMA high-low channel strategy combined with daily open bounces, and (3) Heiken Ashi color change strategy combined with daily open price level. All strategies use daily open as a bias filter and confluence point for entries.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: Day trading focus (intraday); daily open, high, low used for day context [00:00-00:30]
- sessions/hours: Mentions "active market" and price reaction throughout the trading day; NOT STATED which sessions

## Strategy 1: Pin Bar Rejection at Daily Open Price

### Indicators and settings
- Daily open price indicator/line (from TradingView or manual marking)
- Pin bar pattern: NOT STATED specific parameters for tail-to-body ratio

### Context / bias filter
- Only trade in trending markets [06:00]
- If current day's open is higher than previous day's open: only consider long entries [04:00-04:30]
- If current day's open is lower than previous day's open: only consider short entries [04:00-04:30]
- Daily open distance between consecutive days must be large enough to indicate trending: "separation between lines, which means we have a short-term trend" [05:30]
- Avoid markets where daily open lines are very close: "short distance one from another indicate a possible range" [04:30]

### Entry trigger
- "A bullish pin bar that formed in the context of an uptrending market right at the opening price line" [06:30-07:00]
- For uptrend: bullish pin bar with long lower wick (rejection of lower prices) at daily open level [06:30-07:00]
- For downtrend: bearish pin bar with long upper wick (rejection of higher prices) at daily open level
- Double pin bar (two consecutive rejections at daily open) provides more confirmation [07:00-07:30]

### Stop loss
- NOT STATED (no specific stop loss location or distance mentioned)

### Take profit / exit
- NOT STATED (no specific profit target or exit rule stated)

### Invalidation / skip conditions
- Skip trading if daily open lines are very close together (indicating range-bound market) [04:30-05:00]
- Skip if price is range-bound rather than trending [05:00]
- Do not trade pin bars counter-trend except at "key chart levels of support or resistance" (like daily open) [06:30]

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: Pin bar definition - what tail-to-body ratio qualifies as "long lower tail" or "long upper tail"?
2. UNDEFINED-PARAM: Daily open distance threshold - what distance between consecutive opens qualifies as "large" for trending vs "narrow" for ranging?
3. UNDEFINED-RULE: Trend determination - how many days of higher open prices constitute an established uptrend?
4. UNDEFINED-PARAM: Confirmation requirement - is one pin bar enough or is double pin bar preferred? [07:00-07:30]
5. SUBJECTIVE: "Key chart level of support or resistance" identification beyond daily open

### Mechanizability
PARTIAL
Pin bar identification from OHLCV is possible with defined tail/body thresholds, and daily open level is mechanically available. However, the key gaps are: pin bar ratio definition (not specified), trend confirmation (how many higher opens = trend?), and daily open proximity threshold (how close to the open for "right at the opening price line"?). Without these parameters, automation requires guessing.

---

## Strategy 2: EMA High-Low Channel with Daily Open Price

### Indicators and settings
- 200 Exponential Moving Average (EMA) applied to high prices: channel upper band
- 200 Exponential Moving Average (EMA) applied to low prices: channel lower band
- Daily open price line

### Context / bias filter
- Price must be in a clear trend (price stays mostly on one side of daily open) [05:30]
- When moving average channel is trending upwards: look for buy signals [10:30]
- When moving average channel is trending downwards: look for sell signals [10:30]
- Prefer confluence with daily open line and channel touching at same price [09:30-10:00]

### Entry trigger
- "When the price retreats to the moving average channel. In this case, the 200 exponential moving average and reacts with a bounce" [09:30-10:00]
- "When the moving average channel is trending upwards, you should consider buying when the price bounces off the channel and the opening price" [10:30]
- Reverse for downtrends: sell when price rallies to channel and gets rejected [10:30]
- Additional confirmation: "If you find a pin bar, that's even a better signal" [10:30]
- Even better: "If you have a previous market swing around the area offering another layer of confluence" [10:30]

### Stop loss
- NOT STATED (no specific stop loss location or distance mentioned)

### Take profit / exit
- NOT STATED (no specific profit target or exit rule stated)

### Invalidation / skip conditions
- Avoid when channel is flat/not trending - look for "an area of value from which you can take your trades" [09:30]
- Skip entries if price simply touches the moving average briefly without strong rejection [09:00]
- Avoid when daily open lines are too close together (range-bound environment) [04:30-05:00]

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: 200 EMA period is stated but no other parameters (smoothing type, etc.) specified
2. UNDEFINED-RULE: What constitutes "trending upwards" or "trending downwards" for the channel?
3. UNDEFINED-RULE: "Bounces off the channel" - how much bounce required? Contact = enough?
4. UNDEFINED-PARAM: "Forcefully rejected back in the opposite direction" - what speed/distance qualifies as "forceful"?
5. SUBJECTIVE: "Previous market swing" identification and proximity assessment
6. UNDEFINED-PARAM: Distance between channel and daily open for confluence - how close for "together around the same price level"? [09:30]

### Mechanizability
PARTIAL
The EMA channel calculation is fully mechanical (200-period EMA on highs and lows), and daily open is fixed. However, gaps prevent full automation: bounce magnitude definition (what counts as sufficient bounce?), trend confirmation for channel (how many bars trending?), and confluence proximity threshold (how close for "together"?). Pin bar confirmation adds UNDEFINED parameters.

---

## Strategy 3: Heiken-Ashi at Daily Open Price

### Indicators and settings
- Heiken-Ashi candles (chart type, not an indicator)
- Daily open price line
- Green candles indicate uptrend; red candles indicate downtrend
- Wicks matter: "green candlesticks with no lower shadow or wick indicate a strong uptrend" [12:30]

### Context / bias filter
- Price must be above daily open line for long trades; below for short trades [12:00]
- Heiken-Ashi color must align with direction: green HA candles above daily open for longs; red HA candles below daily open for shorts [12:00-12:30]
- Trend must be established: green HA bars for uptrend, red for downtrend [12:00]

### Entry trigger
- "If the price is above the opening price line, with the Heikin-Ashi candle turning green from red, it indicates that the price is about to turn higher. So, you want to trade green Heikin-Ashi bars above the opening price line" [12:00-12:30]
- For shorts: "If the price is below the line and Heikin-Ashi candle turns red, it indicates that the price is about to go down. Again, trade red bars below the line" [12:00-12:30]
- Candlestick structure: "green candlesticks with no lower shadow or wick indicate a strong uptrend" [12:30]

### Stop loss
- NOT STATED (no specific stop loss location or distance mentioned)

### Take profit / exit
- "you can remain in the trade until the color of the Heikin-Ashi candlestick changes from green to red. This allows your profits to run while riding the short-term uptrend" [12:30]
- Exit when HA color flips

### Invalidation / skip conditions
- Do not enter if HA candle color doesn't match price location relative to daily open [12:00-12:30]
- Exit if HA color changes [12:30]
- Skip if HA candles show "flip-flop constantly from a green bar to a red bar" indicating choppy market [11:30]

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "no lower shadow or wick" - what counts as "no wick"? (0 pips, 1 pip, 0.1% of candle height?)
2. UNDEFINED-RULE: "Turning green from red" - does this require a full previous red candle or any color change?
3. SUBJECTIVE: How much wick in a HA candle is acceptable - the brief mentions "ideally with no wick" but doesn't quantify
4. UNDEFINED-RULE: When to define a trend as "established" on HA - how many consecutive same-color candles?

### Mechanizability
PARTIAL
Heiken-Ashi is a mechanical chart type, and daily open is fixed. However: wick definition for "strong uptrend" (threshold for "no wick"), color flip detection (is one candle change sufficient?), and trend establishment criteria (how many consecutive bars?) are undefined. Mechanical calculation is possible but these subjective rules prevent full automation.

## Notable claims and caveats
- "The opening price provides a standard support and resistance function on the price chart" [01:30]
- Daily open represents "the balance between bullish and bearish forces" [01:30]
- Movement above daily open = bullish, below = bearish [01:30]
- "the open price sets the general tone for the price action" [03:30]
- Biasing trades based on open relationship to previous open will "save you many losing trades" [04:00-04:30]
- When daily open lines are close together and price is range-bound, "false signals" are common [05:00]
- Moving average channel reduces market noise compared to single moving average [09:00]
- "This strategy also works as a scalping setup" for Heiken-Ashi method [12:30]
- No transaction costs, spread, slippage, or commission mentioned
- No discussion of drawdown or losing streaks
- Speaker mentions academy program promotion [13:30]
