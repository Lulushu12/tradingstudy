# The 2 Lines That Predict Tomorrow's Trades (Previous Day High and Low Trading Strategy)

- video_id: 4pYxq6gt3oQ
- url: https://www.youtube.com/watch?v=4pYxq6gt3oQ
- duration: 16:04
- classification: STRATEGY

## Summary

The video presents a trading system based on marking yesterday's high and low prices and identifying confluence zones where these levels align with VWAP bands. The core idea is that price tends to revisit and respect these psychological levels from the previous session. The system uses VWAP bands as a filter to confirm high-probability entries, distinguishes between genuine and false breakouts of these levels, and adapts the approach based on market structure (trending vs range-bound).

## Instruments and timeframes stated

- markets: NOT STATED (examples mention Bitcoin and Tesla but no market specification)
- timeframes: NOT STATED (examples suggest intraday, mentions "first few hours of the session" [14:30])
- sessions/hours: "first few hours of the session" [14:30]; "afternoon, its power begins to diminish" [14:30]

## Strategy 1: Previous Day High/Low with VWAP Confluence

### Indicators and settings

- Previous day's high: quoted as primary level [11:30]
- Previous day's low: quoted as primary level [11:30]
- VWAP bands: with standard deviation [11:00], specific standard deviation value NOT STATED
- VWAP bands composition: "upper band becomes resistance in sideways markets, lower band becomes support, middle line is the balance" [11:00]

### Context / bias filter

Market structure determines entry approach [11:28-12:00]:
- In trending markets: "trade against movements back to yesterday's levels with confluence" [11:30]
- In sideways/range-bound markets: "trade the rebounds" [11:30]
- Strongest validity in "first few hours of the session" [14:30]; "in the afternoon, its power begins to diminish" [14:30]
- Price must have volume at the level: "You also need volume at the level" [14:00]; volume threshold NOT STATED
- Avoid "Random highs and lows from sessions with low volume... ignore them" [14:00]

### Entry trigger

Price approaches yesterday's high or low with confluence to VWAP bands [10:00-10:30]:
- Step 1: "Mark yesterday's high and low" [11:30]
- Step 2: "Add the VWAP bands with standard deviation. Look for overlap with yesterday's levels" [11:30]
- Example: "The price falls to yesterday's low and simultaneously bounced off the lower band" [10:30]
- Range-bound example: "The price fell to the previous day's low and hit the lower VWAP band at the same point. Double confluence. I bought it immediately." [08:00]
- Confluence definition: levels overlapping or nearby [10:30], NOT STATED how close qualifies as overlap

### Stop loss

"Stop loss just outside both levels" [08:00]
"Stop loss just below both levels" [13:00-13:30]
Specific distance from levels NOT STATED
Mistake to avoid: "I used to place my stop-loss orders exactly at yesterday's levels. Big mistake. Now, I'm giving the price room to move." [14:30]

### Take profit / exit

"Use the opposite level as your target" [12:00]
Example: "the target was the previous day's high" [08:00] when entering at low
Alternative in confluences: "This convergence not only provides better entry points. It also offers better exits." [04:00]; specifics NOT STATED

### Invalidation / skip conditions

"If both levels failed, the structure would be broken and I would have to bear a small loss" [13:30]
Fake breakouts return and break through the level again [09:00-09:30]
Do not trade on "random highs and lows from sessions with low volume" [14:00]

### Claimed performance

"This setup gave me a 4-to-1 profit last week" [10:30] - single anecdotal example, no statistical claim
Tesla example described as successful trade [13:00-13:30], trade details: "entered the confluence zone already having bought my ticket" but no final profit result stated
No win rate, expected payoff ratio, or drawdown mentioned
One statement: "This filter alone eliminates 70% of the false signals that used to take me out of the market" [03:30] - referring to VWAP confluence filter

### Vagueness log

1. UNDEFINED-PARAM: VWAP standard deviation value not stated; standard standard deviations for VWAP are typically 1 or 2 but speaker does not specify
2. UNDEFINED-RULE: "Overlap" or "nearby" for VWAP band confluence not defined numerically; what distance qualifies as confluence [10:30]
3. UNDEFINED-PARAM: Volume requirement at level stated as necessary [14:00] but threshold not specified
4. UNDEFINED-RULE: "Institutional positioning" inferred from candle appearance ("explosive," "violent," "without hesitation") [06:00-06:30]; these are subjective visual terms
5. UNDEFINED-RULE: "Liquidity capture" pattern described conceptually but entry/exit criteria not mechanically specified [05:00-05:30]
6. SUBJECTIVE: "Explosive candle" vs "gradual candle" as institutional signal [06:00-06:30]
7. SUBJECTIVE: Distinguishing "real breakout" from "fake breakout" based on post-breakout price behavior ("skyrocketing" vs "fluctuating") [09:00-09:30]
8. SUBJECTIVE: "Read the footprints of smart money" based on candle patterns and oscillation [06:00]
9. VISUAL-ONLY: Example at [04:00] references chart visuals "observe this configuration" - exact support/resistance values not stated
10. UNDEFINED-RULE: How to interpret VWAP midpoint crossing as "net long" vs "net short" for actual trading signals [11:00]
11. UNDEFINED-PARAM: Range of "first few hours" - exact hours or market open duration NOT STATED
12. UNDEFINED-RULE: How to measure "oscillation means confusion" vs legitimate consolidation [06:30]

### Mechanizability

PARTIAL - The skeleton is computable (mark previous day's high/low, overlay VWAP bands, identify market structure, check price approach), but critical entry timing and confluence thresholds require assumption-filling. The definitions of "overlap," "explosion," "institutional footprints," and breakout validity are subjective or visual-only and would require discretionary judgment or invented parameters to code.

---

## Notable claims and caveats

- No mention of costs, spread, slippage, or commission impact
- No drawdown, losing streak frequency, or failure rate discussed
- Video emphasizes strategy works "because it is based on three pillars: psychology, structure, and flow" [12:00], but does not quantify success rate
- Warns against overcomplicating: "The market respects simplicity. Complex systems fail when you need them most." [14:30]
- Strategy strength declines significantly in afternoon sessions [14:30]
- Cannot be applied to all market conditions; range-bound markets are highlighted as optimal environments [07:30]
