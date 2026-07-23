# Market Cipher 103 — Part 1

Source lesson: market-cipher-103-part-1
(First of a 3-part session tying Market Cipher into a full trade-execution process.)

## The 6-timeframe framework
Building on the multi-timeframe technique from Market Cipher 102, this lesson formalizes it into **3 "environmental" timeframes + 3 "execution" timeframes**, each group averaged into a single directional read rather than treated as 6 separate signals:
- For **swing/day trades**: environmental = 4H, 2H, 1H; execution = 24-min, 12-min, then entry on 3-min or 1-min.
- For **scalps**: compress to one environmental timeframe (e.g. 24-min) plus execution timeframes like 6-min/3-min/1-min (or even 3-min/1-min/30-second on paid TradingView tiers).
- Process: only start this analysis once **price has reached a pre-marked level** (S&R, Fibonacci, volume-based — from earlier lessons). Then read the 3 environmental timeframes, form one overall directional bias, then read the 3 execution timeframes *through the lens of* that bias (not as a fresh independent question) to time the actual entry.

## The three Market Cipher B signals used per timeframe
1. **Momentum waves** — described here as *leading* money flow: momentum waves getting progressively lower while money flow is still thick/rising is read as an early warning that money flow is about to roll over (and vice versa for bottoms). Framed as "the momentum waves show what money flow is about to do before it happens."
2. **Money flow** — direction/color as covered before.
3. **VWAP momentum wave** (Cipher B's own VWAP, not a price VWAP) — also checked for direction and divergence against price.

For each environmental timeframe, judge whether these three are collectively bullish or bearish (e.g. "2 of 3 bearish, 1 of 3 bullish → net bearish for this timeframe"), then combine the 3 environmental timeframes into one overall bias.

## Divergence definition reinforced across all three signals
A divergence = price and an oscillator moving in opposite directions from a shared reference point:
- Bearish: price prints a higher high, the signal (momentum wave, money flow, or VWAP) prints a *lower* high → warns of a top.
- Bullish: price prints a lower low, the signal prints a *higher* low → warns of a bottom.
- The lesson stresses checking for divergence across **all three** Cipher B signals independently (momentum-wave divergence, VWAP divergence, money-flow divergence) — the more of the three show divergence, the stronger the case. In the worked trade example, all three showed bearish divergence on the 1-hour chart, described as making the setup "airtight."

## Worked example: a real short trade (ETH, ~2277 entry)
- Price reached a Fibonacci golden-pocket resistance (0.618–0.65, pulled from a specific swing high/low).
- Environmental timeframes (4H, 2H, 1H) each showed money flow still rising/high but momentum waves and VWAP both printing lower highs against price's higher highs → net bearish bias on all three.
- Execution timeframes (24-min, 12-min) confirmed the same divergence pattern sustained over multiple days, not just a single candle — the lesson stresses that day-trade-scale divergences should be read as a multi-day *trend* in the indicator, not a single-bar event (as opposed to scalps, where even a single small divergence swing can be tradable).
- Entry trigger: money flow crossing from bullish to bearish color on the 1-minute (tightest) or 3-minute chart, right as price rejected the resistance. Instructor noted the actual live entry was slightly less precise than the "ideal" textbook entry (got a worse fill due to a stop-hunt wick above the level) — illustrating that real entries are often less clean than a backward-looking analysis suggests, and that getting wicked out of a still-valid setup is a normal reason to re-enter rather than abandon the trade idea.
- **Market Cipher A** was checked last, purely as a minor reassurance layer (one blood diamond appeared on the 24-min chart) — explicitly described as *not* a required confirmation, consistent with earlier lessons' framing of Cipher A as secondary to Cipher B.

## Fourth confirmation layer: visible "reaction off the level"
Beyond the indicator readings, the instructor also wants to see price physically struggle at the level before entering — any of:
- Repeated failed attempts to close beyond the level (e.g. 3 rejections in a row).
- A sharp wick beyond the level that's immediately rejected.
- A slower-forming sequence of progressively lower highs right at the level.
Any of these, combined with the Cipher B divergence stack, is treated as confirmation that the level is actually holding, not just theoretically important.

## Scope note
This is Part 1 of 3 — explicitly framed as covering the general environmental/execution framework and the short-trade example; Parts 2 and 3 (separate lessons) cover longing and scalping specifically.
