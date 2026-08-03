# Super Easy London Breakout Strategy (Scalping Forex Market With A Simple System)

- video_id: q8kIpbtS1nw
- url: https://www.youtube.com/watch?v=q8kIpbtS1nw
- duration: 10:02
- classification: STRATEGY

## Summary

This video presents a London Breakout Forex scalping strategy that fades (trades against) initial breakouts of the Asian session range during London open hours, rather than trading in the breakout direction. The strategy exploits the fact that many retail traders chase breakouts while institutional traders fade them. During the Asian session, a small support/resistance range is established (typically the last hour of Asian session). When the London session opens with increased volume, price breaks this range, but the strategy enters when price returns and breaks the opposite side, capturing trapped retail traders. Positions are small, targeting quick profits rather than large moves. The strategy works best during Asian-to-London session overlap on major currency pairs like GBP/USD and GBP/JPY.

## Instruments and timeframes stated
- markets: verbatim: "Forex; specifically GBP/USD, GBP/JPY, EUR/USD, USD/JPY" [06:30-07:00]
- timeframes: verbatim: "5-minute chart example" [07:30]; intraday scalping style
- sessions/hours: verbatim: "London open session, Asian session, London session" [02:00-02:30]; emphasis on Asian-to-London overlap [02:30-03:00]

## Strategy 1: London Breakout Fade (Anti-Breakout)

### Indicators and settings
- Support/resistance levels: horizontal lines drawn manually around Asian session range [05:30-06:00]
- No technical indicators used; price action only
- Focus: "last hour before the London open" or "few candles prior to the London open" [05:30-06:00]

### Context / bias filter
Market structure: [02:00-02:30] London is "known to be the start of strong volatility as London is one of the biggest capital markets in the world."

[02:30-03:00] "The beginning of the London session is also the end of the Asian session. Right before the London open, the Asian markets are beginning to close down and square off their open positions...That's why during the London open hours, a sudden spike in volatility occurs causing momentum in the Forex market."

[03:00-03:30] "The price action during the Asian session is quite range bound. Prices don't make any big moves during this period."

Core concept [04:30-05:00]: "That's why during London session, I don't take trades in the direction of the breakout. I fade the breakout."

### Entry trigger
Two-step process [05:30-06:30]:

Step 1 - Identify initial London breakout [06:00]:
"Then wait for the price to break that range, either below or above it."

Step 2 - Wait for fake-out and counter-direction break [06:00-06:30]:
"When this happens, you simply wait for the price to break on the other side of the range. So, you don't need to trade the breakout. You fade it. You want to see trapped traders attempting to catch that breakout. If the price returns into the range and breaks it on the other side, you can search for trades in the opposite direction of the London breakout."

Example long entry [07:30-08:00]:
"We have the Tokyo range here. The market opened with a downward breakout. At this point, we know that we want to go long when the price returns on the other side of that range. The market returned almost immediately on the other side of the range, offering a good trade to the upside with a lot of traders trapped below the range."

### Stop loss
[06:30] "I usually place my stop loss on the other side of the breakout"

Stop placed on opposite side of the breakout range (e.g., if breakout was down, stop placed above the range).

### Take profit / exit
[06:30] "I aim for small profits"

Specific target NOT STATED; implied to be modest/intraday scalp profits.

[09:00-09:30] "Once the trade has reached the day's profit, you don't need to stay glued to your chart and wait for other trading opportunities."

Exit when daily profit target reached (NOT MECHANICALLY SPECIFIED).

### Invalidation / skip conditions
[08:30-09:00] "This London breakout trading system is not a foolproof system. So, you will have trading losses and days with a true breakout. You will encounter days where the price breaks the range and trades above it or below it for the rest of the day."

Skip if breakout is genuine and continues (determined via backtesting).

[08:30] Recommendation: "You have to do some work and backtest to see which pairs offer most false breakouts during the London session."

Also skip if price does NOT return to the range; true breakouts continue in original direction.

### Claimed performance
NONE EXPLICITLY STATED. Implied via examples showing successful fades; caution that "not a foolproof system" and losses will occur.

### Vagueness log
1. UNDEFINED-RULE: "small range of few candles" [05:30-06:00] — "few" is vague; no specific candle count (3 candles? 5?)
2. UNDEFINED-RULE: "Asian session range" identification is visual; no quantified high/low definition
3. UNDEFINED-RULE: "price breaks that range" [06:00] — no specific close requirement or wick threshold
4. UNDEFINED-RULE: "returns into the range" [06:00-06:30] — how much of the range must be retraced? Complete? 50%?
5. UNDEFINED-RULE: "breaks it on the other side" [06:00-06:30] — similar to rule 3; no quantified breakout definition
6. UNDEFINED-RULE: "small profits" [06:30] — no pips or percentage target specified
7. UNDEFINED-PARAM: "day's profit" [09:00-09:30] — daily profit target NOT SPECIFIED
8. UNDEFINED-RULE: "trapped traders" [06:30] — no mechanical definition; inferred from price action
9. SUBJECTIVE: "True breakout" vs "false breakout" distinction requires backtesting per pair [08:30]

### Mechanizability
PARTIAL. The strategy requires:
- Manual Asian session range identification (visual or discretionary time window)
- First breakout detection (mechanizable: price close beyond range)
- Return detection (mechanizable: price touches range again)
- Counter-direction breakout (mechanizable: price closes beyond range on opposite side)
- Stop placement "on other side of breakout" (mechanizable once range is defined)
- Take profit target (NOT SPECIFIED; requires user input)

A basic skeleton can be coded with range bounds + breakout detection, but key gaps remain:
- Asian session range selection criteria not mechanical (just "visual inspection")
- "Small profits" target not quantified
- Entry confirmation when price "breaks on other side" lacks precision (close? wicks?)

The strategy can be partially automated but requires user definition of range boundaries and profit targets.

## Notable claims and caveats

- [01:00-01:30] "Breakouts fail simply because the smart minority has to make money off the majority."
- [01:30] "Retail traders like to trade breakouts. The smart minority, the institutional, more seasoned traders, prefer to fade breakouts."
- [04:00-04:30] "That's a losing system with no chance of consistency on the long term. Anyone who's tried a breakout strategy will know how challenging it can be. Too many breakouts don't work out the way you expect them to."
- [04:30-05:00] "Many breakouts that start off strongly quickly fade and start to track back into a range."
- [05:00-05:30] "Fading breakouts simply means trading in the opposite direction of the breakout. You would fade a breakout if you believe that the breakout from a support or resistance level is false and unable to keep moving in the same direction."
- [05:30] "In cases in which the support and resistance level broken is significant, fading breakouts may prove to be even smarter than trading the breakout."
- [06:00-06:30] "you want to see trapped traders attempting to catch that breakout."
- [08:30-09:00] "This London breakout trading system is not a foolproof system."
- [08:30-09:00] "You will have trading losses and days with a true breakout."
- [09:00] "The main advantage of trading the London breakout trading strategy is that is very simple. There is no complicated use of multiple indicators."
- [09:30] "when you stick to one or two currency pairs using the London breakout trading strategy, you can make small profits on a daily basis."

No mention of transaction costs, spread, slippage, or commission. No explicit drawdown or losing streak analysis. The speaker cautions against true breakouts that continue and recommends currency pair selection via backtesting. Acknowledges strategy is not foolproof and losses will occur.
