# VWAP

Source lesson: vwap
(Guest lesson taught by a Discord moderator, not the main instructor.)

## What VWAP is
Volume-weighted average price — a moving average that resets on a chosen period, giving the average traded price adjusted for volume during that session. Acts as a dynamic S&R level, similar in spirit to the EMA-based dynamic S&R covered earlier.

## Setup
- TradingView indicator: search "VWAP" → Volume Weighted Average Price.
- Recommended style tweak: turn off the upper band, lower band, and band fill, leaving just the plain VWAP line (repeated preference throughout the course for clean, single-line indicators).
- Multiple VWAPs can be run simultaneously at different "Anchored Period" settings (input setting, default "Session"): session/daily, weekly, monthly, quarterly, yearly, decade — each resets to snap to price at the start of its period. Daily/weekly/monthly are the three the instructor(guest) actually uses; quarterly/decade left untested.

## How each period-VWAP behaves
- **Daily VWAP**: resets at the start of each trading day (UTC midnight in this walkthrough); acts as an intraday dynamic S&R level, best suited for day trades since it's close to current price action.
- **Weekly VWAP**: resets at the start of each new week (session close/open boundary); acts as a higher-timeframe dynamic S&R, described as more reliable/"powerful" than the daily one.
- **Monthly VWAP**: resets at the start of each new month; same idea at an even higher timeframe.

## "VWAP close" and Naked VWAP — the most useful part of this lesson
- Just before a VWAP resets (snaps to the new period's price), its final value ("VWAP close") often becomes a meaningful support/resistance level going forward — mark it the same way you'd mark other levels.
- **Naked VWAP**: a VWAP-close level that has *not* been retested on the very next period (day/week/month) — analogous to a naked point of control from the volume lessons. If price returns and taps the VWAP-close on the *same* period it formed, it's not "naked." Naked VWAP-close levels are described as noticeably more reactive/reliable than ones that get tapped immediately — same "untouched levels are more reactive" principle from earlier lessons, just applied to VWAP.
- This applies at all three scopes: naked daily VWAP-close, naked weekly VWAP-close (described as more powerful than daily), naked monthly VWAP-close (most powerful of the three, used more sparingly since there are fewer of them).

## Anchored VWAP
- Tool location: left toolbar → second option ("Tools") → Anchored VWAP.
- Unlike the fixed daily/weekly/monthly resets, an anchored VWAP lets you manually click a start point (a significant high, low, or the start of a defined range) and it recalculates from there.
- Style tip: same as above — hide upper/lower bands, keep just the line; color-code it (e.g. red when price is below it → acting as resistance, green when price is above it → acting as support).
- Common anchor points demonstrated:
  - **From the low of a trading range** — acts as intraday dynamic S&R across that range; multiple bounces/rejections shown as it's retested.
  - **From the start of a range** (subjective — judgment call on whether an early consolidation counts as part of the range) — same dynamic S&R behavior.
  - **From a major swing high/low** on a higher timeframe (e.g. anchored to the all-time high, or to a level right before a major dump) — used to track long-term dynamic S&R across an extended move; example given of two short trades taken off rejections from a range-anchored VWAP, each capturing roughly 7–8% moves.
- Same caveat as any dynamic level: it moves with price, isn't an exact fixed number, and works best combined with other confluence rather than traded alone.
