# Categorical Trading - Source Extraction

Source: https://www.youtube.com/watch?v=gvuSYdGox0s
Title: "The Trading Strategy I Invented That Got Me Funded - Categorical Trading"
Author: Iman (imantrading.org). Runtime 41:29. Auto-generated captions, 1327 segments.
Supplementary source: https://www.imantrading.org/howimantrades

Extraction status: faithful. Timestamps are from the auto-caption stream and are approximate to
the block, not the word. Where the captions are garbled it is flagged rather than guessed.

---

## 1. Core thesis

> "all price action exists on a spectrum of extremes somewhere between consolidation and
> Direction everything else exists along this line and every condition has clearly defined high
> probability wins and losses" [00:37]

Two poles, one axis:

- **Consolidation**: "price is more likely to stay where it has already been" [00:54]
- **Direction**: "price is more likely to go to a new area" [00:54]
- **Chaotic**: neither label holds, or the label flips faster than you can act on it. Explicit
  no-trade state. "if price action can't be categorized because it's too chaotic this approach
  won't have an edge" [21:03]

Every trade is a bet that the *current* category persists:

> "every trade should be fundamentally based on expecting what's happening to continue" [01:11]
> "the only reason you should be wrong on a trade is if conditions change" [01:27]

## 2. The two trade templates

| | Consolidation | Direction |
|---|---|---|
| Bias | Mean reversion | Continuation |
| Profit target | Inside the range [01:11] | At a new area [02:00] |
| Stop loss | Outside the range [01:11] | Inside the range [02:00] |
| Fails when | Regime turns directional [19:51] | Price pulls back / turns to consolidation [19:51] |
| High-prob loss | Long the top, short the bottom [01:27] | Fading it for a pullback [02:16] |

Symmetry is the whole idea: the directional template is the consolidation template with target
and stop swapped.

> "you will lose all your money if you're doing mean reversion in direction or targeting new
> areas in consolidation" [03:07]

## 3. Bracket sizing

Targets and stops are sized off recent candle range, not off structure.

- **Rule of thumb**: target ~half the size of recent candles [04:29], [06:11].
  - 30m candles at 25 pts -> 10 pt target and stop [04:11]
  - 30s candles at 9 pts -> ~4 pt target and stop [05:18]
- He immediately undercuts it as non-canonical: "there is no rule like doing a 50% Target based
  on the size of the previous candle it all just comes down to personal preference" [05:01].
- Secondary sizing cue: NinjaTrader's native horizontal price-interval gridlines. "if candles are
  going through these Sixpoint intervals pretty easily maybe I'll Target Five Points if they're
  only going through a little or not at all I'll probably Target Four Points" [09:55]. 15-pt
  intervals = "serious Direction ... high volatility" [10:11].
- Stated design intent for the bracket: a size "that doesn't require any change from Price action
  to work with" [39:39]. i.e. the trade must pay out under conditions that already exist.

## 4. ATR usage

> "I use ATR but not in the traditional way it's used ... ATR is just a tool for quantifying
> volatility" [06:29-06:48]

- Default period 14 [06:48].
- **Period set to 1** to read the exact top-to-bottom size of each candle [06:48]. This is the
  setting that actually drives bracket sizing.
- Preferred operating range: **6 to 14 points per candle** on NQ [08:47]. The chart timeframe is
  changed until ATR lands in that band.
- NinjaTrader price-axis auto-adjust must be turned off so outlier candles do not skew the scale
  [08:47-09:05].

## 5. Timeframe as a volatility control

The timeframe is not fixed. It is the knob used to force volatility into the preferred band:

> "in the morning for now I'll use a 20 second chart if volatility is high a 30 second chart if
> it's average or a 40-second chart if it's low" [07:24]

> "adjusting the time frame of the chart to artificially create the volatility conditions you
> like" [25:09], reaffirmed [39:23]

He will swap timeframes several times inside a single 17-minute session [09:23].

## 6. Risk and R:R

- Recommended starting point: **1:1** [11:53], [13:01], [28:33]. Rationale: a 1:1 bracket is a
  coin flip at 50%, so only a small edge is needed to flip it. "risk reward ratios on their own
  mean nothing until an edge is introduced" [13:01].
- His own current R:R is stated to differ from 1:1 but **the value is never given** [11:35].
- Position sizing: never specified anywhere in the video.
- Max daily loss: mandated but never quantified. "think of it as the point of no return" [25:42].
  He admits his own was "too high" for months because he ignored his own data [14:46].
- No trailing, no partials, no moving targets: "I do not move profit targets further, go for
  bigger trades, try to time when the low or high of day will break or anything else" [35:06].

## 7. Filters and no-trade conditions

These are the most mechanical statements in the entire video.

1. **Session window**: 9:33-9:50 a.m. ET only [16:25]. Arrived at by testing full day, from
   10:00, the open, long/medium/short sessions, and returning to the open "because the data said
   to" [16:44].
2. **News blackout**: stop at 9:42 ahead of 9:45 releases; forexfactory.com checked daily
   [27:08], [39:19]. Intent is to never be *in* a trade across a release.
3. **No trades at high or low of day** [24:03], [31:12].
4. **No trades at pivots** [31:12]. "Pivots" is never defined.
5. **No trade immediately after a high-volatility candle** [31:53]. Rationale given is sound:
   "a huge candle is a break of the recent structure and is therefore the start of a new price
   action category" [31:53], and you cannot know the new category yet: "we don't know what
   category it is until we get a couple candles" [32:03].
6. **No trade when the category is flipping too fast** [18:44], [19:34].
7. **Ignore Direction entirely** - his live amendment recorded mid-video: "I just adjusted this
   document to ignore Direction ... I wait for consolidation or do nothing" [39:44]. Reason: "I'm
   terrible with this in Direction and on higher time frames" [18:27]. He is on record that his
   own edge exists in consolidation only.

## 8. Instrument, platform, and process

- Platform: NinjaTrader [08:47].
- Instrument: NQ (NASDAQ futures) for scalping; S&P 500 suggested for higher-timeframe
  applications "for its liquidity and potential to largely scale the size" [21:20].
- Prop firm: TradeDay, affiliate code [10:44], [11:00] (code garbled in captions).
- Screen-record every session (OBS) and review [22:10], [25:09], [38:38].
- A written "reminder document" reviewed on a 3-minute bell during the session [33:14], [39:39].
  Its stated focuses: ATR/price structure, bracket size, category rules, and the high-probability
  loss.
- Second channel streams the live open sessions [41:11].

## 9. Performance claims

From the video:
- "two weeks without a red day" [37:38], immediately followed by an editorial insert admitting
  he "ruined all that progress" after filming [37:45].
- "right now I'm taking less trades in a week than I used to do in a single day and my results
  have never been better" [15:04]. Unquantified.
- ~1 year of daily trading to converge on his variables [14:11], [36:26].
- **No win rate, R multiple, account size, or drawdown figure is stated anywhere in the video.**

From imantrading.org (sample funded account, Sept 2025 - Mar 2026):
- Win rate 57.6%
- Average win $161.93, average loss -$101.83
- Career payouts >$34,000 since July 2024

Note the internal contradiction: average win is **1.59x** average loss, which is not a 1:1
bracket. Either the brackets are not 1:1 in practice, or exits are discretionary, or the sample
mixes configurations. This matters, see the systemization notes.

## 10. Trade-quality framework

Judge the decision, not the outcome [20:09]:

| | Worked | Did not work |
|---|---|---|
| Good trade | success | success |
| Bad trade | failure (got lucky) | failure |

And the meta-rule he calls the most valuable thing he found [16:08], [36:44]:

> "if you trade for a while look back on everything and realize you'd be consistently profitable
> if you avoided Direction ... then obviously avoid Direction"

with the guard that you need a representative sample first: "one week is not enough" [13:54],
"you're going to absolutely ruin your chances of success if you set hard rules for yourself too
early" [15:37].

## 11. Named psychological failure modes

- **Mistake reversion**: "the problem of overcoming an issue only to end up doing it again at
  some point in the future" [34:22].
- The urge to **time change** rather than trade the current condition: "the desire to time change
  instead of trading according to the current price action conditions" [20:44]. He names this as
  the primary route to consistent unprofitability.
- The **reverse-it heuristic**: when the impulse to take a trade fires, identify what the
  high-probability *loss* would be under the current category, and take the other side [35:41].
- Pressure as self-generated: "a madeup thing by your brain and based on an irrational fixation
  on short-term results" [38:52].
- Forcing a trade every session [15:53], [19:34].

---

## 12. What is NOT in the source

This is the important half of the extraction. The following are load-bearing and absent:

1. **No regime classifier.** There is no rule, threshold, indicator, or lookback that converts a
   chart into the label consolidation / direction / chaotic. It is eyeballed. This is the single
   largest gap - it is the entire strategy.
2. **No entry trigger.** Given "we are in consolidation," nothing states *when* to buy. Not a
   level, not a percentage of range, not a candle pattern, not a touch rule. The video says where
   the target and stop go, never where the entry goes.
3. **No range definition.** "Inside the range" and "outside the range" are used constantly.
   "Range" is never defined - no lookback, no swing rule, no session-based construction.
4. **"Pivots" undefined**, though used as a hard exclusion filter [31:12].
5. **"High volatility candle" unquantified** [31:53]. No ATR multiple, no percentile.
6. **His actual R:R never stated** [11:35].
7. **Max daily loss never quantified** [25:42].
8. **Position sizing absent entirely.**
9. **Costs never mentioned once.** For a 1:1 scalp on 4-5 point NQ brackets this is the dominant
   term in expectancy, and it is not discussed at any point in 41 minutes.
10. **Timeframe selection is discretionary and intra-session**, which means the bar series itself
    is a free parameter chosen by feel while the trade is live.

## 13. Honest characterization

This is a **discretionary framework plus a risk-and-process wrapper**, not a mechanical system.
The video is roughly 25% classification concept, 15% bracket heuristics, and 60% journaling,
psychology, and self-selection advice. The author is explicit and repeatedly honest about this:

> "almost none of you are going to trade like me ... anyone who is truly trading this strategy
> will be following the same fundamentals of categorization where it differs is how you choose to
> implement everything" [13:19], [18:11]

He is not claiming to hand over a system. He is handing over a lens and telling the viewer to
spend a year finding their own parameters inside it. Any backtest of "categorical trading" is a
backtest of choices the author did not make, and results cannot be attributed to him either way.
