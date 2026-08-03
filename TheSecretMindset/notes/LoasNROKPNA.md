# Explosive VWAP Trading Strategy For Scalping & Day Trading Stocks (For Beginners)

- video_id: LoasNROKPNA
- url: https://www.youtube.com/watch?v=LoasNROKPNA
- duration: 10:22
- classification: STRATEGY

## Summary

The video teaches a VWAP-based day trading and scalping strategy for stocks. The core approach waits for retracements to VWAP after strong directional moves, then enters when price touches a confluence zone formed by VWAP and 50%-61.8% Fibonacci retracement levels at key support/resistance areas. The strategy filters setups by market bias, volume quality, and retracement precision, with a target of at least 1:1.5 risk-reward ratio.

## Instruments and timeframes stated

- markets: stocks, specifically large-cap equities [09:30]
- timeframes: intraday; mentions 1-minute and 30-minute charts as examples [02:00], but timeframe for trading not explicitly specified
- sessions/hours: Avoid pre-market, post-market, and first 15 minutes after market open [09:30]

## Strategy 1: VWAP Retracement Confluence

### Indicators and settings

- VWAP: standard cumulative intraday VWAP, one calculation per trading day [00:00]
- Fibonacci retracement: 50% level as primary, 50%-61.8% zone for confluence [05:30]
- Fibonacci precision: "approximate 50% retrace, say anywhere from a 50% retrace to a 60% retrace" [05:30]

### Context / bias filter

- A strong directional trend must first be established with momentum [03:00]
- Market bias must be assessed and correct; "The market bias trumps any individual VWAP trading setup. If you get the market bias wrong, regardless of the quality of the trading setup, it will not work out over the long run" [07:00-07:30]
- Trade only large-cap equities with "sufficient average daily volume, typically familiar names that move smoothly and follow VWAP levels" [09:30]
- Avoid pre-market, post-market, and first 15 minutes after the open; "VWAP tends to be jumpy and unreliable during those periods while it establishes itself" [09:30]

### Entry trigger (LONG)

"We look for a bullish price move that clears above a previous swing high with strong momentum. We mark out a 'retracement zone' between 50% and 61.8% of the price move. If price falls down to the retracement zone and the VWAP offers additional support, we aim to buy a possible rejection of that area." [06:00-06:30]

### Entry trigger (SHORT)

"Look for a bearish price move that clears below the previous swing low with strong momentum. Mark out a 'retracement zone' between 50% and 61.8% of the price move. If price rises up to the retracement zone and the VWAP offers additional resistance, we aim to sell a possible rejection of that area." [07:30-08:00]

### Stop loss

For longs: "Stop loss below the confluence area" [07:00]
For shorts: Implied above the confluence area
General principle: "our stop-loss is always on the other side of it [VWAP]" [04:00]. Stop should be at a "solid support point in a bullish market or a resistance point in a bearish market" [04:30].

### Take profit / exit

"aim for at least 1:1.5 risk reward ratio" [07:00]

No explicit exit rule beyond the risk-reward target. The speaker advises looking for "additional confirmation signals from candlestick patterns, chart patterns, or other price action signals" [10:00].

### Invalidation / skip conditions

- If "the price will cut though the VWAP with ease," the setup is not high quality [04:00]
- If market bias is wrong, skip the setup [07:00-07:30]
- If the stock is in pre-market, post-market, or within 15 minutes of open [09:30]

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: "strong momentum" for the initial swing high/low breakout is not defined as a measurable quantity (e.g., ATR multiple, % move, volatility threshold) [06:00]
2. UNDEFINED-RULE: "retracement zone" is specified as 50%-61.8%, but the exact base move for Fibonacci calculation is not stated (high to low? open to high?) [05:30]
3. SUBJECTIVE: "buy a possible rejection" / "sell a possible rejection" — what constitutes a rejection in terms of candle structure, wick, or price action? [06:00-06:30]
4. UNDEFINED-RULE: The exact entry point within the confluence zone is not specified; does entry occur on close, wick touch, or confirmation candle? [06:30]
5. VISUAL-ONLY: "candlesticks that followed had lower shadows implying bullish pressure" — this is a visual observation, not computable from OHLCV alone [06:30]
6. SUBJECTIVE: "high quality setup" is defined conceptually (at key S/R levels, good reward-risk) but lacks mechanical criteria [04:30]
7. UNDEFINED-PARAM: "key support or resistance level" for the context filter is not pre-defined [04:30]

### Mechanizability

PARTIAL

The skeleton is computable: identify swing highs/lows, apply Fibonacci retracements, overlay VWAP. However, critical gaps prevent full automation: (1) "strong momentum" has no quantitative definition; (2) "rejection" is subjective; (3) the exact entry candle within the confluence zone is discretionary; (4) visual cues (candlestick shadows) are referenced but not defined computationally. The stop placement below confluence is clear, but entry precision and momentum filtering require manual judgment.

## Notable claims and caveats

- "While VWAP is no holy grail, it is an effective instrument for differentiating between random (meaning choppy price action) and non-random (meaning trending behaviour)" [00:00]
- "Often times, the price will cut though the VWAP with ease. It's not about taking a signal, it's about filtering and trading only the high quality setups" [04:00]
- The speaker acknowledges that adding "additional confirmation signals from candlestick patterns, chart patterns, or other price action signals" is recommended [10:00]
- "The greatest value of a trading setup is not the entry it offers, but the stop-loss it implies" [04:00]
- No discussion of commissions, spreads, slippage, or transaction costs
- Strategy limited to large-cap liquid stocks; does not cover forex, commodities, or illiquid securities
