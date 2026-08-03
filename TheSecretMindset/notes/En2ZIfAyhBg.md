# Amazingly Simple 21/55 Moving Average Strategy For Day Trading & Scalping

- video_id: En2ZIfAyhBg
- url: https://www.youtube.com/watch?v=En2ZIfAyhBg
- duration: 10:06
- classification: STRATEGY

## Summary

The video teaches a trend-following strategy using two moving averages (21-period fast, 55-period slow) based on the "contraction-expansion principle." Rather than relying on MA crossovers, the strategy monitors the distance gap between the two MAs. Strong trends expand the gap (MAs diverge); pullbacks contract it (MAs converge). Entries occur when price rejects the dynamic zone formed by the MAs during a pullback, followed by a breakout in the trend direction. Candlestick patterns (engulfing, pin bars) confirm entries. The 55 MA slope indicates trend strength.

## Instruments and timeframes stated

- markets: NOT STATED (general application for day trading & scalping)
- timeframes: NOT STATED
- sessions/hours: NOT STATED

## Strategy Overview: Contraction-Expansion Principle

### Indicators and settings

- 21-period moving average (fast): "will be located more closely to price resulting in more touches" [01:30]
- 55-period moving average (slow): "gets touched less frequently during a normal trending market" [01:30]
- Choice of 21 and 55: "Because 21 and 55 are Fibonacci numbers" [00:30]
- Note: "This setup will provide a clearer picture of trend strength on a slower and faster time frame" [01:00]

### Key Principle: Contraction-Expansion

"When in a strong trend, the price will pull the 21 MA with it, which in turn will diverge further away from the 55 MA, causing a larger gap between the two moving averages. This is an expansion. As price pulls back, or transitions into a sideways pattern, the moving averages will close in together, often creating a contraction" [02:00-02:30]

- Expansion = strong trend (MAs diverge)
- Contraction = pullback or consolidation (MAs converge)

### Entry Logic (Three Steps)

**Step 1: Identify Contraction/Pullback**
"We analyze price action to find for a contraction in the moving averages. Essentially a pullback into the dynamic support or resistance area, determined by the 2 moving averages" [05:00]

"When in a strong trend, the price will pull the 21 MA with it... Notice how the distance between the two MAs is fairly consistent... When the market does pull back, it bounces fairly accurately from the 21 – 55 dynamic zone" [03:00]

**Step 2: Analyze Confluence and Trend Room**
"Does the dynamic zone also line up with a round number or a major horizontal support and resistance zone? Is the trend headed into a key swing high /low?" [05:30]

**Step 3: Trade Breakout After Rejection**
"The final step is to trade a breakout, after the price resumes in the initial direction, and the price was unable to break below the dynamic zone of the 2 moving averages" [06:00]

"After we identified strength in the market, meaning that the price found support/resistance at the dynamic zone... we also need a breakout. We want a trend line breakout or a swing breakout" [06:00-06:30]

### Entry trigger

1. Price pulls back into the 21-55 MA dynamic zone (contraction)
2. Price rejects this zone (does NOT break through)
3. Candlestick confirmation pattern: "engulfing candlesticks and pin bars are ideal as a trade entry" [07:00]
4. Breakout occurs from wedge/triangle pattern or swing high/low [06:30-07:00]

Critical rule: "wait for the price to return to dynamic zone, the 2 moving averages must not cross each other during this pullback, and after the price rejects the dynamic zone, search for a breakout in the direction indicted by the 2 moving averages" [08:30]

### Stop loss

Conservative: "below or above it [the dynamic zone], depending on the trade we take, in this example, below it" [07:00]

Aggressive: "below the most recent correction" [07:30]

### Take profit / exit

"I aim for at least 1:1.5 risk reward ratio" [07:30]

### Invalidation / skip conditions

- "In real time, we don't know if the price will indeed reject the dynamic area. It might push through the zone, and go the other way" [08:00]
- Do NOT enter during contraction without breakout confirmation [08:00]
- MAs crossing during pullback violates the setup [08:30]
- Trend reversal signal: "As the 55 MA shifts from strongly pointing upwards during a bull trend, to going sideways, it can provide early warning signals about a shift in sentiment" [08:30-09:00]

### Claimed performance

NONE CLAIMED; speaker states: "This is not a perfect strategy, you will encounter losing trades" [09:30]

## Vagueness log

1. UNDEFINED-PARAM: Type of moving average (EMA or SMA) — not specified, though video uses "EMA" terminology [08:30]
2. UNDEFINED-RULE: "Dynamic zone" width — gap between the two MAs is variable; exact distance threshold not defined [02:00]
3. SUBJECTIVE: "Strong trend" vs "weak trend" — based on visual assessment of gap size [02:00]
4. UNDEFINED-RULE: "Extended pullback" — how extended? [03:30]
5. SUBJECTIVE: "Round number" for confluence — specific levels not predefined [05:30]
6. UNDEFINED-PARAM: Candlestick patterns (engulfing, pin bars) — NOT mechanically defined [07:00]
7. UNDEFINED-RULE: Wedge/triangle breakout — what constitutes a valid wedge/triangle? [06:30]
8. UNDEFINED-PARAM: "Most recent correction" for aggressive stop — how many bars back? [07:30]
9. SUBJECTIVE: 55 MA slope assessment — "strongly pointing upwards" or "going sideways" — visual judgment [09:00]
10. UNDEFINED-RULE: Entry timing when multiple candlestick patterns present — priority not specified [07:00]

## Mechanizability

PARTIAL

The 21 and 55 period moving averages are mechanically computable. Gap detection (divergence) between MAs can be automated. However, significant gaps prevent full automation: (1) "dynamic zone" rejection is subjective (exact price level for rejection?); (2) candlestick pattern detection (engulfing, pin bars) not mechanically defined; (3) wedge/triangle identification is discretionary; (4) "strong" and "extended" pullback have no quantitative thresholds; (5) round number confluence relies on manual judgment; (6) MA slope assessment ("strongly upwards" vs "sideways") is visual; (7) breakout confirmation criteria not explicitly defined. Entry signal framework is computable, but confirmation and exact entry timing require manual interpretation.

## Notable claims and caveats

- "This setup will NOT be a crossover strategy" [01:00]; strategy focuses on gap distance, not crosses [01:00]
- "Moving averages are lagging, which means that they react to price rather than price reacting to them. That also means that the contraction of the MAs isn't the cause of the resumption of the downtrend, but is rather an effect of price resuming the trend" [04:00]
- "The dynamic zone also acts as a magnet, because when price is too far from it, it tends to pull price back to this zone" [06:30]
- "This is not a perfect strategy, you will encounter losing trades" [09:30]
- "don't try to gamble and enter earlier, without breakout confirmation, because that's not the point of this strategy" [08:00]
- "The best tip I can share with you is to always pay attention to the slope of the 55 moving average" [08:30]
- No specific win rate or Sharpe ratio provided
- No discussion of commissions, spreads, slippage, or transaction costs
