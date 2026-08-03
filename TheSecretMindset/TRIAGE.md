# Triage: what can and cannot be backtested

Source: 266 videos from the YouTube channel @TheSecretMindset (267 listed, 1 has no captions).
Roughly 62 hours of video, 3.8M characters of transcript.

## Headline

**530 strategy blocks were extracted. Not one of them is backtestable exactly as taught.**

A first pass rated 33 blocks as fully mechanical. A second, stricter audit knocked down all 33:
25 are testable only after inventing 2 to 6 parameters, and 8 are not testable at all. Every
remaining block was already flagged PARTIAL or DISCRETIONARY on the first pass.

This is not a criticism of the channel. It is the normal state of taught discretionary trading.
It does mean that any P&L number produced downstream is a number about an assumption set that
somebody chose, not about the strategy as the creator teaches it. That attribution has to be
written down before any backtest runs, not after the results look good.

## Corpus breakdown

| Video classification | Count |
|---|---|
| STRATEGY | 104 |
| MULTI-STRATEGY | 69 |
| CONCEPT | 48 |
| TOOLING | 28 |
| PSYCHOLOGY | 16 |
| PROMO | 1 |

| First-pass mechanizability (per strategy block) | Count |
|---|---|
| FULL | 33 |
| PARTIAL | 384 |
| DISCRETIONARY | 43 |
| unrated / malformed | 70 |

## Shortlist: the 25 that survive with declared assumptions

Ranked by how many parameters a coder must invent. Fewer is better.

| # inv. | Strategy | Instrument stated | Timeframe stated | Beyond OHLCV |
|---|---|---|---|---|
| 2 | MACD Crossover (n72tM2HLv34) | Forex, crypto, and stocks mentioned gene | NOT STATED as a rule (daily, 5-m | no |
| 2 | Donchian Channel Breakout Entry with Channel-Based Exit (fmS_rUcKF6c) | Stocks mentioned primarily | Daily charts | no |
| 2 | MFI 50-Level Crossover (bAT6F7x9K8M) | NOT STATED for this specific sub-strateg | NOT STATED | no (MFI requires volume, |
| 2 | Mechanical Swing Trading (Daily Outside Bar) (s4DSY3Y_N4Y) | General; examples shown include Gold, Cr | Daily (explicitly stated as non- | no |
| 3 | Inside-Outside-Inside Pattern (IZLMN_L3b0s) | NOT STATED | NOT STATED ("all timeframes" cla | no |
| 3 | StochRSI with MACD Confirmation (Market Strength) (3GmofkcVO58) | Bitcoin, Forex, and stock indices (Dow J | NOT STATED (video says "day trad | no (StochRSI, MACD, and  |
| 3 | Opening Channel Breakout with 200 EMA Confirmation Filter (BvUJ9upqpyI) | Forex, unspecified pair ("the world's la | Intraday, session-anchored (Fran | no, but requires GMT-ali |
| 3 | Confluence Breakout Scalping Strategy (5ZYVXiSKfxU) | NOT STATED (examples shown: Apple, Tesla | 5-minute chart | no (volume is standard O |
| 3 | MACD Trend System (S2HaCa0b-bY) | NOT STATED | multiple examples used (daily, 4 | no |
| 3 | Order Block with 200 EMA Channel (Long and Short) (7Zvt6efiHME) | NOT STATED | NOT STATED | no |
| 3 | Short Entry (Red Renko Brick) (CtelYJ5lFr8) | verbatim "stock market" (no specific tic | NOT STATED (Renko bricks are eve | no |
| 3 | Yellow Line Crosses 50 Level (A5IgJuaKHdc) | NOT STATED (general application to any m | NOT STATED (speaker says the sig | no |
| 3 | Momentum 0-Line Crossover (Basic Approach - Not Recommended Alone) (ULd9DYzOI7E) | NOT STATED (Tesla is used only as an ill | NOT STATED as a strict requireme | no |
| 4 | Golden/Death Cross Strategy (Red and Blue Lines) (0nRWsm4oAss) | Forex and stocks mentioned generally, no | NOT STATED | no |
| 4 | Opening Channel Breakout (European Session) (BvUJ9upqpyI) | Forex generally (no specific pair named) | Intraday, keyed to Frankfurt ope | no (requires timestamped |
| 4 | Three-Layer Bollinger Bands Trading (_8q3ZJ5afFA) | NOT STATED (implied multi-asset: stocks, | Daily and 4-hour charts | no |
| 4 | Pivot Point Trend Trading with ADL Confirmation (Pdpcy_FGV7I) | Forex (EUR/USD, GBP/USD examples) and cr | 15-minute (EUR/USD example) or 3 | no (ADL uses volume, whi |
| 4 | VWAP Trading - Basic Buy/Sell Signals (w_VNaTAB64c) | NOT STATED across the course (examples r | Daily VWAP reset stated explicit | no (VWAP uses volume, pa |
| 4 | Multi-Timeframe Heiken Ashi Color Change (Ci1hKIHL9VY) | Forex, stocks, crypto (stated genericall | NOT STATED as a specific pair —  | no |
| 4 | Pivot Point Trading (oF_NsJLMXEs) | stocks, currencies, crypto mentioned as  | NOT STATED (intraday day-trading | no |
| 5 | VWAP Entry (oF_NsJLMXEs) | NOT STATED (stocks, currencies, crypto m | NOT STATED (intraday day-trading | no (VWAP uses volume, pa |
| 5 | Round Number Support/Resistance Trading (_8q3ZJ5afFA) | NOT STATED (examples imply multi-asset:  | daily and 4-hour charts | no |
| 5 | Fibonacci Pivot Point Trend Following (bkSS_kPCctQ) | NOT STATED (forex and stock markets ment | 1 hour and higher (stated; "the  | no (pivot levels are der |
| 5 | EMA + RSI + ADX Scalping (vBM0imYSzxI) | Forex or major indices (stated) | 5-minute (explicitly stated) | no |
| 6 | Ultimate Oscillator Divergence Trading (DQXqjjFz11k) | NOT STATED (forex and stocks mentioned g | NOT STATED as a single required  | no |

## The 8 that cannot be tested at all

| Strategy | Why |
|---|---|
| Chandelier Exit as Trailing Stop/Exit Indicator (fmS_rUcKF6c) | Use a 22-period, 3x-ATR "Chandelier Exit" trailing stop set below the recent high (for longs) or above the recent low (for shorts) to manage an alread |
| Daily Average Range (ADR) Tracking (vvuWY3cFzpY) | Compare the day's current high-low range at midday to its 10/20-day average true range to judge whether the market is "overextended" (caution against  |
| 10-Period SMA Daily Chart Trend Filter (iB3dt0Kk8j0) | Use the slope and position of price relative to a 10-period daily SMA as a bias filter before taking (unspecified) trades on shorter timeframes. |
| MACD Confirmation System (Multi-Timeframe Filter) (S2HaCa0b-bY) | Require MACD zero-line bias on a higher timeframe, a crossover/divergence signal on a middle timeframe, and a histogram-flip trigger on the entry time |
| Range Analysis (Bar Expansion/Contraction) (luEbG761C50) | Interpret whether a candle's high-minus-low range is expanding (energy/volatility, possible breakout) or contracting (indecision, possible coiling bef |
| Moving Average for Trend Direction Confirmation (yPbUn3Wuh98) | Use the direction of price relative to an unspecified moving average, and its slope, as a discretionary directional bias rather than a defined trade t |
| TPO Charts (Time Price Opportunity) (luEbG761C50) | Read intraday Time-Price-Opportunity profiles (point of control, value area, acceptance/rejection patterns) to gauge whether the market is accepting o |
| 21-Period EMA Channel Trading (_8q3ZJ5afFA) | Trade bounces or breakouts of a 21-period EMA-of-high/EMA-of-low channel when they align with a round-number level, but "round number," "bounce," and  |

Most of these fail for the same structural reason: they are filters, exits, or commentary
with no entry trigger of their own. Coding them means inventing an entire surrounding system,
which tests that invention rather than anything the channel taught.

## Instrument and data mismatch

Across all 266 notes, the markets named are: stocks 104, forex 89, futures 80, crypto 27,
gold/XAU 16, and no market stated at all in 133. This channel is not crypto-first.

The OHLCV data currently in this repository is BTCUSDT.P and XRPUSDT.P only. Several shortlist
entries are session-anchored (a 07:00-08:00 GMT opening channel, London-to-New-York hours) or
quoted in pips on FX pairs. Porting those to 24/7 crypto is itself an untested assumption, and
a large one. Testing them properly needs FX, index, or gold data that is not here yet.

## Files

- `channel_index.tsv` — all 267 videos with classification and strategy count
- `transcripts/` — cleaned, timestamped transcripts, one file per video id
- `notes/` — structured strategy note per video: rules, exact quoted parameters, vagueness log
- `VERIFICATION_VERDICTS.md` — per-candidate audit with the specific assumptions each one needs
- `EXTRACTION_BRIEF.md` / `VERIFY_BRIEF.md` — the instructions the extraction and audit agents ran under
