# Strategy catalog: TradingLab "Day Trading" playlist

Source: https://www.youtube.com/playlist?list=PLH-wQt3UtmKNNZUlkzUohevXqIEpUMo9X
159 videos. 134 transcripts recovered, 3 private/unlisted, the rest blocked by
YouTube bot detection during bulk download and retried separately.

Per video triage lives in `triage/`. That pass labelled 68 videos STRATEGY, but
that count is an artifact of counting videos rather than ideas. Collapsed by
actual mechanics, the playlist contains roughly a dozen distinct systems plus
one very large family of restatements.

## What this playlist actually is

Two thirds of the "strategy" videos are the same setup told again with a
different thumbnail: sweep a liquidity level, break structure, enter on the
return into a fair value gap. Videos 008, 017, 022, 043, 044, 048, 049, 074,
075, 077, 079, 080, 083, 084, 088, 089, 091, 094, 095, 097, 101, 104, 108, 111,
112, 115 and 116 are all variations on it. Testing them as 27 systems would
produce 27 nearly identical result rows. It is tested here as ONE parameterised
strategy with switchable components.

The channel also runs a heavy affiliate pattern (HankoTrade broker links, a paid
Discord, "the rest of the backtest results are in my Discord"). That is not a
reason to dismiss the strategies, but it is a reason to treat every claimed
result as marketing until reproduced.

## Tier 1: fully mechanical, every component reimplementable

| # | Name | Videos | Core rules | Timeframe stated |
|---|------|--------|-----------|------------------|
| S1 | Fibonacci ABCD 0.88 | 010 | impulse leg, retrace into 0.5-0.618, recover into 0.382-0 without new extreme, enter at 0.88, target the leg extreme, stop beyond leg origin | 30m, forex |
| S2 | Donchian + LWTI + volume | 053, 054 | price touches upper Donchian(96), LWTI(25,20) green, volume above its MA(30); stop at Donchian mid, target 2R | 5m |
| S3 | Raschke 3/10 MACD | 067 | MACD(3,10,16) new extreme, then cross and reverse on the pullback; target prior swing, stop beyond recent extreme | hourly example |
| S4 | RSI 80/20 + VWAP | 065 | RSI band 80/20 not 70/30; mean reversion at bands, or pullback entry at RSI midline in trend; partials at midline, rest at VWAP | 1m to daily |
| S5 | EMA trend meter + SMI | 087 | EMA 13/21/34/55 all aligned, SMI cross in the same direction; 2R target, stop beyond recent extreme | 1h, 4h, daily |
| S6 | Impulse MACD | 034 | LazyBear Impulse MACD cross, only when outside the OB/OS zone; exit on opposite cross, stop at swing low | unstated |
| S7 | Smoothed Heikin Ashi | 061 | smoothed HA (10,10) colour flip, pullback to HA support, green candle confirm; half off at 1.5R, rest on colour flip | unstated |
| S8 | ABC pattern + RSI | 026 | A low, B high, C pullback holding above A, enter on B break, RSI>50 at B; stop below C, target 2R | any, higher better |

## Tier 2: the SMC family, tested as one parameterised system

| # | Name | Videos | Components |
|---|------|--------|-----------|
| S9 | Liquidity sweep to FVG | 008, 017, 022, 043, 044, 048, 049, 074, 075, 077, 079, 080, 083, 084, 088, 089, 095, 097, 104, 112, 116 | sweep of a prior high/low, then break of structure, then entry on return into the fair value gap left by the displacement leg; stop beyond the sweep, target 2R or the opposing liquidity pool |

Switchable pieces, each independently testable: require the sweep or not,
require BOS or not, enter at FVG edge or midpoint, target fixed R or opposing
liquidity, restrict to a discount/premium half of the range.

## Tier 3: not testable as specified, and why

| # | Name | Videos | Blocker |
|---|------|--------|---------|
| X1 | Hedge fund order block indicator | 016, 018 | closed source indicator, calculation never disclosed |
| X2 | Green/red arrow indicator | 052 | closed source, no rules given at all |
| X3 | The Next Pivot + SSL Hybrid | 064 | "Next Pivot" projection is proprietary; its output is the entry trigger |
| X4 | UT Bot + regression candles | 063 | UT Bot is reproducible, but the stop references a "black line" the video never defines, and no exit rule is given |
| X5 | On-chain reversal zones | 090 | needs ChainExposed unrealised profit/loss data, not price data |
| X6 | Kullamaggie momentum breakout | 060 | requires a screener universe of stocks that moved 30-100% in a month. It is a cross-sectional stock selection method. On a single crypto series there is nothing to screen, so it cannot be tested here without a multi-asset universe |

X6 is worth calling out separately. It is probably the most credible strategy in
the playlist, being a well documented equities momentum method, and it is the
one this data set cannot evaluate at all.

## Ambiguities that repeat across nearly every strategy

These are not per strategy quirks. The same four gaps appear again and again, so
resolving them once as house conventions unblocks the whole catalog.

1. **"Stop below the recent low"** (S3, S5, S6, S7, S9 and most of Tier 2).
   No video defines "recent". Candidates: lowest low of the last N bars, or the
   last confirmed swing pivot, or an ATR multiple.
2. **"Find a strong trend" / "a large move"** (S1, S4, S7, and every Tier 2
   video). No video gives a size threshold. Needs a minimum leg size, in percent
   or ATR, before a setup is eligible.
3. **Setup expiry.** Every multi step setup (S1's four steps, S9's sweep then
   BOS then FVG) is described as a sequence with no time limit. Without a
   maximum bar count between steps, a pending setup stays armed forever and the
   backtest silently waits years for step three.
4. **Target when not stated as R.** Several say "target the previous high" with
   no definition of which high.

## Claimed results, for later comparison

| Video | Claim |
|-------|-------|
| 010 | 62% win rate, 1,040% profit, 77 trades |
| 053 | $10k to $1.1M in 12 months |
| 060 | $9,100 to $82M in 8 years, 30% win rate |
| 061 | "2x more profitable than normal Heikin Ashi", $70,536 in 60 days |
| 064 | $28,000 profit on a $100,000 deposit |
| 087 | trend table filter adds 9% win rate |
| 034 | "three times as good as normal MACD" |

Video 010 is worth flagging before any code runs. Entry at the 0.88 retracement
with the target at the leg extreme is roughly a 7:1 reward to risk. Combined
with the claimed 62% win rate that implies about +4.4R of expectancy per trade,
which would compound an account to absurdity within a year. The claim is
internally inconsistent, so the interesting question is not whether it
reproduces but which part of it breaks.
