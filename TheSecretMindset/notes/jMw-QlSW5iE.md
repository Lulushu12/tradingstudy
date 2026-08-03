# STOP Trading Gold With Broken Setups! Use This Simple XAUUSD Strategy Instead

- video_id: jMw-QlSW5iE
- url: https://www.youtube.com/watch?v=jMw-QlSW5iE
- duration: 11:09
- classification: STRATEGY

## Summary

This video presents a XAUUSD (Gold) trading strategy based on Dollar Index (DXY) movements and the inverse correlation between them. The core principle is that the Dollar Index moves first, and Gold follows; thus watching DXY for support/resistance breaks provides an anticipatory edge over watching Gold directly. The strategy involves identifying support and resistance levels on the DXY chart, waiting for clean (non-wick) price closes beyond these levels, then entering Gold trades on the subsequent pullback with rejection candles. Stop losses are placed 15-30 pips below the pullback low for longs, and take profits target the next resistance level. Three filters prevent low-probability trades: major news events, weak breaks with small candles, and Gold trading at major round-number levels.

## Instruments and timeframes stated
- markets: Gold (XAUUSD), Dollar Index (DXY)
- timeframes: verbatim: "1-hour or the 30 minutes chart. Sometimes the 4-hour if I want to zoom out. Anything lower is just noise. Anything higher is too slow" [02:30-03:00]
- sessions/hours: NOT STATED

## Strategy 1: Dollar Index Break → Gold Entry (Long Setup)

### Indicators and settings
- Dollar Index (DXY): support and resistance levels identified via horizontal lines at prior bounce points [02:30-03:00]
- No technical indicators used; price action only
- Gold chart: resistance and support levels [04:00-04:30]

### Context / bias filter
[01:00-01:30] Economic relationship: "Gold is priced in dollars. So when the dollar gets stronger, gold becomes more expensive for the rest of the world. They stop buying, so gold drops. Flip it around. Dollar weakens, so gold gets cheaper. Everyone piles in, and gold rises."

[01:30] "the dollar moves first. Not always. But often enough to matter."

Bias determination [01:30-02:00]: "When the DOLLAR INDEX breaks down, I buy gold. When DOLLAR INDEX breaks up, I sell gold."

### Entry trigger
Long entry requires two steps:

Step 1 - Dollar Index breakout [03:30-04:00]:
"A candle closes below that support level. Not a wick below. A close below. That's the difference between a fake and a break."

Step 2 - Gold pullback and rejection [04:00-04:30]:
"I wait. Price spikes up on gold. That's the initial reaction. Then it always pulls back. Comes down to test a level. Maybe previous resistance becoming support. Maybe the breakout level itself. This is where I want to enter. I look for a rejection candle on that pullback. A wick or an engulfing pattern. Something that shows buyers are stepping in. That's my long entry."

[04:30] "Stop loss goes below the pullback low."

### Stop loss
[04:30] Placed "below the pullback low. Tight but logical, usually 15 to 30 pips on gold."

### Take profit / exit
[04:30] "Target is the next resistance level on gold."

Exit at next resistance level on Gold chart.

### Invalidation / skip conditions
Three filter conditions that require skipping the trade [08:00-10:00]:

1. Major news events [08:30-09:00]: "First, major news events. Fed interest rate decisions, CPI releases… Jobs reports. These create chaos. DOLLAR INDEX spikes one way then reverses. Gold does the same and the correlation breaks down temporarily. I don't trade 30 minutes before or after major news."

2. Weak breaks [09:00-09:30]: "Not all breaks are equal. Small candle barely closing past the level. That's low conviction. Gold might not follow. I want strong breaks with big candles. Clear closes beyond the level. This is where most traders get trapped. They see any break and they rush to gold. Then the break fails, gold reverses and they're stuck. So wait for strong breaks at obvious levels."

3. Gold at major levels [09:30-10:00]: "Sometimes DOLLAR INDEX breaks but gold is sitting right at a major round number, like $4000. These levels have their own gravity. Gold might respect its own level more than it follows DOLLAR INDEX. Before I enter, I check where gold is sitting. If it's right at a major psychological level, I'm more careful. I wait for extra confirmation."

## Strategy 2: Dollar Index Break Up → Gold Short (Bearish Setup)

### Indicators and settings
- Dollar Index (DXY): resistance and support levels [02:30-03:00]
- Gold chart: support and resistance levels [04:00-04:30]

### Context / bias filter
[01:30-02:00] Short bias triggered when: "When DOLLAR INDEX breaks up, I sell gold."

[05:00-05:30] Behavioral note: "Gold drops faster than it rises. So that bounce window is tiny. If you hesitate, you miss it."

### Entry trigger
[05:00-05:30] Similar two-step process:

Step 1 - Dollar Index breaks above resistance [06:00-06:30]:
"Look at DOLLAR INDEX again. This resistance level. Price rejected here twice. Now this candle closes above. Dollar strength confirmed."

Step 2 - Gold pullback and rejection [06:30]:
"I wait for the bounce. Right here. Gold bounces up into this previous support level. Now it's resistance. This candle is my trigger. Red body, sellers rejected the bounce. That's my short entry."

### Stop loss
[06:30] "Stop above the candle." (Above the rejection candle that served as entry trigger.)

Stop placement NOT SPECIFIED in pips for shorts; similar to longs (15-30 pips implied but not stated).

### Take profit / exit
[06:30] "Target at next support."

Exit at next support level on Gold chart.

### Invalidation / skip conditions
Same three filters apply [08:00-10:00]: major news, weak breaks, Gold at major levels.

### Claimed performance
[08:00-08:30] "This gold trading strategy works 70% of the time. The other 30%? It's a trap."

[05:30-06:00] Implied positive performance via examples: "Easy 50 pips", "Another winner", "This keeps happening, over and over."

### Vagueness log
1. UNDEFINED-RULE: "If a child could spot the level, it's valid. If you have to squint and guess, skip it" [03:00] is subjective; no quantified support/resistance identification rule
2. UNDEFINED-RULE: "Strong breaks with big candles" [09:00-09:30] lacks definition (how big is "big"? In pips, ATR, or percentage?)
3. UNDEFINED-RULE: "rejection candle" [04:30] is defined as "A wick or an engulfing pattern" but exact patterns NOT mechanically defined
4. UNDEFINED-RULE: "engulfing pattern" [04:30] lacks specific parameters (full engulf, partial engulf?)
5. UNDEFINED-RULE: "Pullback" [04:00-04:30] magnitude NOT SPECIFIED; no depth requirement
6. UNDEFINED-PARAM: Short stop loss in pips NOT STATED (implied 15-30 pips like longs, but not explicit)
7. UNDEFINED-RULE: "Major psychological level" like "$4000" [09:30-10:00] — no rule for identifying such levels
8. UNDEFINED-RULE: Entry timing on Gold: "I wait for the pullback" [04:00-04:30] but exact entry bar unclear (on close of rejection candle? On next bar?)
9. UNDEFINED-RULE: "Correction" on Gold chart is visual; no precise pullback depth or duration specified

### Mechanizability
PARTIAL. The DXY support/resistance identification is discretionary (visually identified). However, several components are mechanizable:
- DXY candle close beyond support/resistance (mechanizable with OHLC data)
- Gold chart next resistance/support identification (discretionary, but can be automated with swing point detection)
- Rejection candle detection: wicks or engulfing patterns (partially mechanizable; engulfing patterns are codable)
- Entry on specific rejection candle pattern (mechanizable with pattern detection)
- Stop loss 15-30 pips below pullback low (mechanizable)
- Take profit at next level (mechanizable with level detection)

A basic skeleton can be coded if support/resistance identification is either manual or automated via swing point algorithm. The main gaps are subjective level identification ("if a child could spot it") and breakout strength assessment ("big candles").

## Notable claims and caveats

- [00:30-01:00] "The Dollar moved first. Gold followed. That's not a coincidence. That's a cheat code."
- [01:00-01:30] "Gold is priced in dollars. So when the dollar gets stronger, gold becomes more expensive for the rest of the world. They stop buying, so gold drops."
- [01:30] "the dollar moves first. Not always. But often enough to matter."
- [01:30] "If you're only watching gold, you're waiting for gold to move. You're reacting. If you're watching DOLLAR INDEX, you see the move coming. You're anticipating. That's a completely different game."
- [02:00-02:30] "Most traders make their gold charts way too complicated. Indicators stacked on indicators. Trendlines everywhere, Fibonacci levels all over the place. They can't even see the trade anymore."
- [04:00] "If you chase the initial spike, you're buying at the worst price. The pullback happens and you're already underwater. The pullback IS the trade."
- [05:00-05:30] "Gold drops faster than it rises. So that bounce window is tiny. If you hesitate, you miss it." — Implies shorts require faster execution than longs
- [08:00-08:30] "This gold trading strategy works 70% of the time. The other 30%? It's a trap."
- [08:30-09:00] "These create chaos. DOLLAR INDEX spikes one way then reverses. Gold does the same and the correlation breaks down temporarily." — Major news events break the DXY/Gold correlation
- [10:00-10:30] "That's not a small edge. That's a completely different game."

The speaker does not mention transaction costs, spread, or slippage. No explicit drawdown or losing streak analysis. The 70% win rate claim is stated without backtesting proof. The strategy emphasizes anticipating moves (seeing DXY break before Gold moves) and avoiding traps via three filters.
