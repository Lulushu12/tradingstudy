# Market Cipher 101

Source lesson: market-cipher-101

## Overview
Market Cipher has three parts: **Market Cipher A** (overlays on price — EMA ribbon + icons), **Market Cipher B** (the oscillator panel below the chart), and **Market Cipher Support & Resistance** (not covered in this lesson). This lesson's framing: use Market Cipher A as "reassurance," Market Cipher B as the main "confirmation" tool — never trade off either in isolation.

## Market Cipher A

### EMA ribbon
- A stack of several EMAs of undisclosed length; find each one's actual period by overlaying a manually-configured EMA of a guessed length until it exactly overlaps a ribbon line (trial and error) — same technique as the Moving Averages lesson.
- All ribbons crossing and turning gray = bearish/short signal; all crossing and turning blue/white = bullish/long signal. Reliability increases with timeframe.
- Critical rule: **wait for the ribbon to fully confirm a color change**, not just for price to cross the ribbon — price crossing back and forth through an unconfirmed ribbon will "slice you up" with false signals. This is what differentiates Market Cipher's ribbon from a plain EMA ribbon (which gives no clear bullish/bearish read on its own).

### Icons (all described as "reassurances," not standalone signals)
- **Yellow diamonds**: bullish trend-continuation icon in an uptrend; more meaningful in clusters.
- **Red diamonds** ("blood diamonds" when large): weakening-trend / bearish icon. A large blood diamond following yellow-diamond clusters, especially alongside a red trigger wave on Cipher B, is treated as a good scalp-short entry or a good place to take profit on a long.
- **Green dots**: bullish reassurance, but explicitly stated to be **most reliable only on 6-hour and higher timeframes** — on lower timeframes they can just as often precede a drop, so they're unreliable there. More trustworthy when they appear next to a blue triangle.
- **Blue triangles**: signal that the *previous* trend has already reversed (not a prediction of a future reversal) — a lagging confirmation, not leading.
- **Yellow X**: flagged as one of the more reliable Market Cipher A signals, including on lower timeframes — described as indicating large-holder ("whale") selling/market manipulation. Seeing one while long is treated as a strong reason to exit.
- **Red X**: smaller/weaker bearish version of the yellow X; most meaningful when combined with a red diamond and a tightly-constricted, gray-turning EMA ribbon.
- General rule for weighting icons: judge them together with what the EMA ribbon is doing — e.g. a green dot printed while ribbons are still tightly bunched (not yet fanning out) is low-confidence; a green dot after ribbons were bearish and are now visibly fanning out is higher-confidence.

## Market Cipher B (the primary confirmation tool)

### Structure
- An oscillator panel scaled roughly -100 to +100 around a "zero line" (like a pendulum's center). ±60 lines mark overbought/oversold; smaller dotted lines near ±52 warn that price is approaching that zone.

### Money flow (red/green wave)
- Represents money entering (green, above zero) or leaving (red, below zero) the asset. Described as one of the most important, most-overlooked parts of Market Cipher B — a clean cross from red to green (or vice versa) frequently coincides directly with the start of a pump or dump, even before other icons/waves confirm. Worth isolating and back-testing on its own per timeframe.

### Momentum waves (light/dark blue)
- Two overlapping waves whose crossovers print the well-known green/red dots.
- **Anchor wave**: a large wave that extends past ±60 — marks a "reference point" (a clear top or bottom) that subsequent waves are read against.
- **Trigger wave**: a shorter subsequent wave; on the bullish side these print progressively **higher lows**, on the bearish side progressively **lower highs**.
- Key methodological point (repeated emphasis): don't fixate on measuring individual wave height or dot color — instead, use the drawing/pen tool to trace the *overall shape* of Market Cipher B like a "sea serpent," and read the whole structure for where it's forming a top or bottom. Market Cipher B's shape often visibly turns *before* price actually reflects that turn.
- In a strong uptrend, momentum essentially stops printing below the zero line at all (and vice versa in a strong downtrend) — when that's true, ignore the topside anchor/trigger waves and focus only on the bottom-side structure (or vice versa), since that's where the actionable signal is.
- **Double/multiple large green dots at a bottom** ("snake eyes") = a notably significant bottom, worth specifically watching for as a long trigger — same logic mirrored for double red dots at a top.

### VWAP momentum wave (Cipher B's own VWAP, distinct from a standard price VWAP)
- A momentum-based approximation of VWAP built into Cipher B, not the same calculation as the VWAP lesson's indicator. Crossing above zero tends to coincide with upward moves, below zero with downward — but explicitly warned that trading every single VWAP cross alone in a sideways/choppy market will "slice you up" (repeated losses). Only trust a VWAP cross when the broader Cipher B direction (traced shape) already agrees with it.
- "Perfect storm" entry described: anchor wave established at a bottom + a tight trigger wave forming + money flow crossing + VWAP crossing zero, all together — presented as the highest-confidence Cipher B entry pattern.

### RSI and Stochastic RSI (explicitly called "icing on the cake" — lowest priority of everything covered)
- Standard RSI included in the Cipher B panel: >80 ≈ overbought, <20 ≈ oversold, used as one more layer of confluence, not standalone.
- Divergence concept introduced (deferred to next lesson for depth): price making a new high/low while RSI moves the opposite direction signals weakening strength and a possible reversal.
- Cipher's Stochastic RSI is a modified single-line version (color change instead of a two-line crossover) of the standard two-line stochastic RSI; same overbought/oversold logic.

## Priority ranking given at the end (Cipher B, from most to least important)
1. Overall direction/shape of Market Cipher B (the traced "sea serpent" structure).
2. The momentum waves themselves (anchor/trigger structure).
3. Money flow.
4. VWAP momentum wave.
5. RSI / Stochastic RSI (least weight — supplementary confluence only).

## Worked example (bull flag breakout)
A bull-flag pattern breaking out was checked against Cipher B: a bottom (anchor wave) had printed, followed by a higher trigger wave, with the VWAP crossing above zero at the same time — treated as reasonable supporting confluence for the pattern's expected bullish resolution, while noting Market Cipher A showed no supporting icons at that moment (illustrating that not every signal source needs to agree, but more agreement = higher confidence).
