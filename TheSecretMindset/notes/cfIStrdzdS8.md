# The Hidden "One Candle" Pattern AI Finds on Every Chart | EASY Trading Strategy

- video_id: cfIStrdzdS8
- url: https://www.youtube.com/watch?v=cfIStrdzdS8
- duration: 13:22
- classification: STRATEGY

## Summary
A day trading strategy based on the "outside candle engulfing three" pattern—a fourth candle that wraps around the highs and lows of three preceding smaller consolidation candles. The pattern is filtered by trend (50 EMA on the 30-minute chart), positioned at key support/resistance levels, and followed by a pullback. Includes two entry methods (conservative with break confirmation, or aggressive at market), stop loss, and minimum 2R profit target. The video also demonstrates automating pattern detection via AI-generated Pine Script.

## Instruments and timeframes stated
- markets: Examples given for Forex (EUR/USD), stocks (Apple), crypto (Bitcoin); specific instruments NOT STATED
- timeframes: "5-minute chart" for pattern identification [03:30]; "30-minute chart" for trend confirmation via 50 EMA [03:00, 04:00]; day trading frequency of 3-4 trades per day [00:00]
- sessions/hours: NOT STATED; results shown within "2 hours" [02:00] and "within hours" [02:30]

## Strategy 1: Outside Candle Engulfing Three

### Indicators and settings
- 50 Exponential Moving Average (EMA): timeframe = 30-minute chart [03:00, 04:00]
- No other indicators; pure price action pattern

### Context / bias filter
**Trend Filter via 50 EMA** [03:00-04:00]: "If price is above the 50 EMA, only take bullish patterns. If price is below the 50 EMA, only take bearish patterns." [03:00]. "I check the 30-minute chart first. Before I even look for patterns. Is price above or below the 50 EMA? That's my bias for the entire day." [04:00]. Speaker emphasizes: "I ignore every pattern that goes against it. No exceptions. This discipline is what separates you from the traders who donate their accounts." [04:00].

**Location Filter** [05:30-07:00]: Patterns must occur at high-probability locations, not "in the middle of nowhere" [07:00].
- **Bullish patterns** [05:30-06:00]: Position at support—"Previous lows that held. Round numbers like $50 or $100. The 50 moving average in an uptrend. Yesterday's low." [05:30-06:00]
- **Bearish patterns** [06:00]: Position at resistance—"Previous highs that rejected price. Round numbers from above. Moving averages in downtrends. Yesterday's high." [06:00]
- **Pullback into level** [06:00-06:30]: "You want to see several candles pulling back into your level before the outside candle appears. This pullback shows temporary weakness that's about to reverse." [06:00-06:30]. Example: "Three small red candles form right at that level. Then a massive bullish outside candle appears. That's an A+ setup." [06:30]

### Entry trigger
**Pattern Definition** [01:00-02:00]: "Three small candles. Usually quiet. Nothing special happening. Then the fourth candle appears. And it's completely different. The high of this candle is above all three previous highs. The low is below all three previous lows." [01:00].

**Close Position (Bullish)** [01:30-02:00]: "For a bullish signal, the outside candle must close in the top 25% of its range." [01:30]. Stronger version: "Close in the top 10% of the range." [02:00]. "A close in the top 25% means buyers didn't just show up. They dominated." [01:30].

**Close Position (Bearish)** [01:30]: "For a bearish signal, it must close in the bottom 25%." [01:30].

**Two Entry Methods** [10:00-10:30]:
1. **Conservative Entry** [10:00-10:30]: "After your outside candle closes, you place a buy stop order just above its high for bullish trades. Or a sell stop below its low for bearish trades. You only enter if price actually breaks beyond the outside candle. This confirms momentum is continuing." [10:00-10:30]
2. **Aggressive Entry** [10:30]: "The second that outside candle closes, you enter at market. No waiting. No confirmation. Just immediate execution." [10:30]. Recommendation: "If you're new to this method, start conservative." [10:30-11:00]

### Stop loss
[11:00-11:30]: "Your stop loss is non-negotiable. It goes beyond the opposite extreme of the outside candle." [11:00]. For longs: below the outside candle's low. For shorts: above the outside candle's high. Example: "Stop loss goes below the outside candle's low. That's also below the 50 moving average. Double protection." [12:00-12:30]

### Take profit / exit
[11:00-11:30]: "Your profit target starts at 2R minimum. If you're risking $100, you're targeting $200. This is risk-reward 101. Risk one to make two. Every time. No exceptions." [11:00-11:30]. Exact exit price/mechanism NOT STATED; only the 2R ratio is specified.

### Invalidation / skip conditions
- Pattern against trend: "You might see the most beautiful bearish outside candle today. But if the trend is up, you walk away." [04:30-05:00]
- Bad locations: "Outside candles in the middle of nowhere. No clear level nearby. No pullback. Just a random pattern in empty space. These fail more often than they succeed." [07:00-07:30]

### Claimed performance
- "3-4 trades a day" [00:00]
- EUR/USD example: "50-pip move followed within 2 hours" [02:00]
- Bitcoin example: "2% rally within hours" [02:30]
- No historical win rate, profit factor, or backtest results stated. Examples are illustrative, not statistical.

### Vagueness log
1. **Close position threshold** - UNDEFINED-PARAM: "Top 25%" vs "top 10%" for bullish close [01:30, 02:00]. Which is the rule? Both are mentioned; unclear if 25% is entry-level and 10% is premium, or if one supersedes the other.
2. **Small candles definition** - UNDEFINED-PARAM: "Three small candles. Usually quiet." [01:00]. How small? Compared to what? No size threshold given.
3. **Previous lows that held** - SUBJECTIVE: Which previous swings count as "held"? How recent? 10 bars? 100 bars? [05:30-06:00]
4. **Round numbers** - UNDEFINED-PARAM: "Round numbers like $50 or $100" [05:30]. Does this apply to all instruments, or only specific price ranges? Not generalized.
5. **Several candles pulling back** - UNDEFINED-PARAM: "Several candles pulling back into your level" [06:00-06:30]. How many is "several"? 2-5? 3-7? Not specified.
6. **Support/resistance definition** - SUBJECTIVE: "Previous lows that held. Round numbers. The 50 moving average in an uptrend." [05:30-06:00]. Multiple sources; no hierarchy of which is "most important."
7. **Pullback timing** - UNDEFINED-RULE: Must the pullback immediately precede the outside candle, or can there be other candles in between? Not clarified.
8. **Stops and reversal** - VISUAL-ONLY: Example at [12:00-12:30] shows "Entry on the break of the high" but breaks the high at what specific price? Implied to be just above but not quantified.
9. **Automation caveat** - TOOLING: The Pine Script automation section [08:00-09:30] is about coding the pattern detector, not trading the pattern itself. It assumes traders will use AI or coding to automate scanning; the core strategy is manual pattern recognition.

### Mechanizability
PARTIAL. The pattern itself (outside candle wrapping three prior candles) is mechanically clear and codable (hence the Pine Script example). The 50 EMA filter is objective. However, the support/resistance location filters are partly subjective (what counts as a "previous low that held"? How to rank round numbers vs. moving average levels?). The pullback requirement ("several candles") lacks specificity. The entry methods are clear (stop order above high for conservative, market order for aggressive), and the stop loss is precise (below candle low). The take profit rule (2R minimum) is clear. Overall, the strategy could be 60-70% mechanized with reasonable assumptions about location filtering, but location judgment introduces discretion that prevents full automation.

## Notable claims and caveats

- No drawdown, losing streak, or maximum loss mentioned.
- No discussion of spread, slippage, or commissions, though day trading and quick execution likely incur both.
- The video emphasizes pattern detection via AI/Pine Script as the "future of trading," implying manual scanning is inefficient. This is marketing-adjacent; the strategy itself remains valid without automation.
- Performance examples (EUR/USD 50 pips, Bitcoin 2%, Gold chart walkthrough at [12:00-12:30]) are illustrative, not historical averages.
- Speaker mentions personal history: "I used to do this exact thing. I'd see a beautiful bearish pattern and couldn't resist... I lost a lot of money before I learned this lesson." [03:30-04:00], suggesting a lesson learned rather than live backtest results.
