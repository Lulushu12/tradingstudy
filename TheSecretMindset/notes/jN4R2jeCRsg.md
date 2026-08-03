# Trading Trendlines & Channels In Forex & Stock Market (Price Action Strategies)

- video_id: jN4R2jeCRsg
- url: https://www.youtube.com/watch?v=jN4R2jeCRsg
- duration: 11:31
- classification: STRATEGY

## Summary

The video teaches trendline and channel-based trading strategies. Uptrends are identified by connecting price lows with rising support lines; downtrends by connecting highs with falling resistance lines. Channels are formed by drawing parallel lines around a trendline to define volatility zones. The strategy uses trendline breaks as trend reversal signals and trades bounces within channel zones at the bottom/top 10-15%. Higher timeframes (weekly/monthly) identify primary trends; shorter timeframes (daily/H4) time entries and exits.

## Instruments and timeframes stated

- markets: Forex, stocks (general application)
- timeframes: Start analysis on weekly/monthly; apply to daily/H4/hourly for entry timing [01:00-01:30]
- sessions/hours: NOT STATED

## Strategy 1: Trendline Identification and Breakout

### Indicators and settings

- Trendline construction: "In an uptrend, you look to connect the lows of the price. In a downtrend, you connect the highs of the price" [02:00]
- Validity: "A valid trend line connects two or more points that define the trend" [02:00]; "at least two, and preferably three or more major low points" [09:30]

### Context / bias filter

- Uptrend: "positive slope and acts as support. As long as the market price remains above this trend line, the uptrend is considered intact" [02:30-03:00]
- Downtrend: "negative slope and acts as resistance. As long as the market price remains below this trend line, the downtrend is considered intact" [03:00]
- Trendline relevance based on: length (longer = more important) [04:30], number of retests [04:30], slope (steep slopes break sooner) [05:30]

### Entry trigger (breakout)

"A close of the price below the uptrend line suggests that a change in trend could be on the cards" [02:30-03:00]

"A close of the price above the downtrend line suggests that a change in trend might happen" [03:00]

"When prices move through the trend line heading higher, the downtrend has been penetrated" [03:30]

Confirmation rule: "once the price has penetrated a trend line, it must remain penetrated for some time period in order to confirm the new trend because most false penetrations correct quickly" [06:30]

Alternative confirmation methods [07:00-07:30]:
- Wait a set time period to confirm penetration
- Wait for a reversal after the penetration
- Create a safety zone (band/channel) around the trendline

### Stop loss

NOT STATED (implied: on the opposite side of the broken trendline)

### Take profit / exit

"A long position is entered when the price crosses a downward trend line moving higher. The trade is held until the price moves below the upwards trend line" [09:00]

Profit target: trend continuation or retest of broken line

### Invalidation / skip conditions

"Most often, prices that have been moving higher will cross below the trend line, then re-cross moving higher, then move lower again" [06:30]

"Most of the biggest profits result from breakouts that never pull back" [08:00]

### Claimed performance

- "Trend following is the most profitable and consistent trading style" [11:00]
- No specific metrics provided

## Strategy 2: Channel Trading (Breakout Support/Resistance)

### Indicators and settings

- Channel formation: "A channel is formed by a trend line and another line drawn parallel to the trend line enclosing a sustained price move" [08:30]
- Purpose: "define the volatility of the price move and establish reasonable entry and exit points" [08:30]

### Context / bias filter

- Established trendline and direction (up or down) [09:30]

### Entry trigger (Uptrend Channel)

"We buy as prices approach the support line (in this case the upwards trend line), and we sell as prices near the resistance line. These buy and sell zones should be around the bottom and top 10%-15% of the channel" [10:00]

### Entry trigger (Downtrend Channel)

"In a downward trending channel, it is best to sell short in the upper zone and cover the short in the lower zone. Buying in the lower zone is not recommended; trades are safest when they are entered in the direction of the trend" [10:30]

### Stop loss

"If prices continue through the lower trend line after a long position has been set, the trade is closed" [10:30]

### Take profit / exit

Exit at opposite channel line (resistance for longs, support for shorts)

### Invalidation / skip conditions

"Buying in the lower zone is not recommended; trades are safest when they are entered in the direction of the trend" [10:30]

### Claimed performance

NONE CLAIMED

## Vagueness log

1. UNDEFINED-RULE: "Two or more points" vs "at least two, preferably three" — exact minimum not specified [02:00, 09:30]
2. UNDEFINED-RULE: "Major low points" — what makes a low "major"? Minimum swing size? [09:30]
3. SUBJECTIVE: "Trend line is perceived as being subjective" — speaker acknowledges this [01:30]
4. UNDEFINED-PARAM: "A set time period to confirm penetration" — what time period? [07:00]
5. UNDEFINED-PARAM: Safety zone (band/channel) width — how wide? [07:30]
6. UNDEFINED-PARAM: Stop loss placement not specified; implied below/above broken line
7. UNDEFINED-RULE: "10%-15% of the channel" for entry zones — how to calculate? [10:00]
8. UNDEFINED-PARAM: Profit target — not specified, only "move to opposite line"
9. SUBJECTIVE: Channel parallel line placement — exactly parallel or approximate? [08:30]
10. UNDEFINED-RULE: "Steep trend is difficult to maintain" — how steep qualifies as steep? [05:30]

## Mechanizability

PARTIAL

Trendline drawing (connecting price extrema) can be mechanized using linear regression or two-point line fitting. Parallel channel lines are straightforward. Break detection is computable. However, gaps prevent full automation: (1) "major" low/high points require defining minimum swing size; (2) trendline validity (when to use new points) is discretionary; (3) confirmation methods ("set time period") are vague; (4) 10-15% channel zones require specific width calculation rules; (5) stop placement is implied but not explicit; (6) profit targets are undefined. The framework is partially mechanizable, but entry filtering and exit placement require manual interpretation.

## Notable claims and caveats

- "It is easier to see the trend on a chart after it has occurred. Trying to identify the trend as it is developing is much more difficult" [00:00]
- "Most successful traders and investors start by evaluating a weekly or monthly chart, and then apply the lines and values developed on those charts to a daily chart" [01:00-01:30]
- "A trend line is more important if it has been retested many times" [04:30]
- "the steepest trend lines are the soonest broken" [05:30]
- "Most of the biggest profits result from breakouts that never pull back... I know you want the textbook breakout, with the price retesting the breakout level, but in some cases the price just keep on going and never reaches the breakout area" [08:00]
- "Trend following is the most profitable and consistent trading style" [11:00]
- No specific win rate or Sharpe ratio provided
- No transaction costs discussed
