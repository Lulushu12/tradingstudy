# Day Trading Strategy For Pivot Points Traders (Forex Trading System For Beginners)

- video_id: Pdpcy_FGV7I
- url: https://www.youtube.com/watch?v=Pdpcy_FGV7I
- duration: 08:50
- classification: STRATEGY

## Summary

This video presents a day trading strategy combining pivot points with Accumulation/Distribution (ADL) line and exponential moving average. The core approach: enter trades at the central pivot point when the ADL/200 EMA crossover confirms the trend direction. Targets are at R1/R2 for long trades and S1/S2 for short trades. The strategy is designed for Forex and cryptocurrency; the speaker explicitly warns against using it on stocks due to gaps affecting the ADL calculation.

## Instruments and timeframes stated

- markets: Forex (EUR/USD, GBP/USD examples), cryptocurrencies mentioned; NOT stocks [08:00]
- timeframes: 15-minute (EUR/USD example) [04:00], 30-minute (GBP/USD example) [05:30]; backtest to find optimal [05:30]
- sessions/hours: Tokyo, London, New York sessions referenced [04:00-05:00]

## Strategy 1: Pivot Point Trend Trading with ADL Confirmation

### Indicators and settings

- Pivot Points: Central Pivot Point (CPP), Support 1 (S1), Support 2 (S2), Resistance 1 (R1), Resistance 2 (R2)
- Accumulation/Distribution (ADL) Line: period = NOT STATED
- Exponential Moving Average: period = 200, applied to ADL line [02:30-03:00]
- Alternative MA periods: "test other moving averages" but "longer-term moving average added on the ADL line will work better than a short-term moving average" [03:00]

### Context / bias filter

Establish the main trend first using the ADL/200 EMA crossover [02:30-03:00]:
- If 200 EMA is BELOW the ADL line = uptrend; only look for long signals [03:00-03:30]
- If 200 EMA is ABOVE the ADL line = downtrend; only look for short signals [03:30]

The central pivot point is the "intraday point of balance between buyers and sellers" [01:30]. Price location relative to CPP defines bias [01:30-02:00]:
- Price above CPP = bullish outlook, consider long positions only [01:30-02:00]
- Price below CPP = bearish outlook, consider short positions only [01:30-02:00]

### Entry trigger

**Critical Rule**: "Very important, we only take signals around the pivot point. That's the main rule of our system" [03:30].

For long entries:
1. ADL line is above 200 EMA (uptrend confirmed) [03:00-03:30]
2. Price is at or retraces to the central pivot point [01:30-02:00]
3. Enter when price rejects the CPP upward [04:00]

For short entries:
1. 200 EMA is above ADL line (downtrend confirmed) [03:30]
2. Price is at or retraces to the central pivot point
3. Enter when price breaks below CPP [04:00-04:30]

Examples from charts:
- EUR/USD: "price rejected the central pivot point and a crossover between the ADL line and the 200 EMA indicated an uptrend" [04:00]
- GBP/USD: "price retraced to the central pivot point. Observe how the AD line is moving lower and lower, confirming the downtrend" [06:00-06:30]

### Stop loss

NOT STATED explicitly. The speaker mentions "move your stop loss to break even" after taking part of profits at R1/R2 levels [07:30], but initial stop loss placement is not defined.

### Take profit / exit

Take profits at R1 and R2 levels:
- Long entry: first target is R1; if price continues, second target is R2 [02:00]
- Short entry: first target is S1; if price continues, second target is S2 [02:00]

"Take a part of your profits at R1 or R2 levels and leave the trade run to its full potential by moving your stop loss to break even" [07:30].

### Invalidation / skip conditions

Do not trade if price does not retrace to the central pivot point [04:30]: "the second day, the price didn't retrace to the central pivot point, so we didn't open a new position" [04:30]. Do not trade away from the pivot point, despite temptation [07:30]: "you will be tempted to take a trades in other areas of the chart, but my advice is to be disciplined and enter the market at the central pivot point" [07:30].

### Claimed performance

The speaker claims "you will be on the right side of the market most of the times" [07:00-07:30] and states "at the end of the week, you will be in profit" if you stick to the rules [07:00-07:30]. Chart examples show multiple winning trades (4-5 trades per trading day in EUR/USD example, 3+ trades in GBP/USD) but no overall win rate percentage is provided. Losses are acknowledged: "of course, you will take some losses" [07:00-07:30].

### Vagueness log

1. UNDEFINED-PARAM: ADL line period not stated; indicator calculation default assumed
2. UNDEFINED-RULE: "Rejects the central pivot point" - no specific criteria for rejection (number of candles, specific distance, candlestick pattern)
3. UNDEFINED-PARAM: Initial stop loss placement not stated; only "move to break even" is mentioned
4. UNDEFINED-RULE: "Retraces to central pivot point" - tolerance/precision not stated; does price have to close at CPP, or just touch it
5. UNDEFINED-RULE: Optimal timeframe selection: "backtest and see which time frame offers the higher probability setups" [05:30] - no specific guidance

### Mechanizability

FULL (for pivot levels and ADL/EMA crossover) to PARTIAL (for entry conditions). Pivot Points are mathematically calculated. ADL and EMA crossover are mechanically computable. However, "price rejects the pivot point" and "price retraces to pivot point" lack precise definitions. Initial stop loss placement is unspecified. Entry confirmation likely requires price action judgment (specific candle pattern at CPP) that is not mechanically defined.

---

## Notable claims and caveats

The speaker emphasizes that pivot points are "an accurate indicator and most market participants are watching and trading these key levels" [01:00-01:30], which makes them reliable. He claims the strategy "solve[s] both problems" of trend establishment and market entries [00:00-00:30].

**Important caveat**: "Don't trade stocks with this system because the AD line does not include gaps in its calculation and the signals will not be 100% reliable" [08:00]. This limits the strategy to Forex and crypto.

The speaker advises strict discipline: "Remember to take the trades only around the central pivot point. Stick to this important rule as it will benefit you in the longer term" [07:00-07:30]. He recommends backtesting: "Backtest other currency pairs, commodity, or even cryptocurrencies and see which time frame is suited for them" [07:30-08:00].

He expects traders to "take some losses" but claims disciplined adherence yields weekly profits [07:00-07:30]. No mention of spread, slippage, or commission. Multiple entries per day are expected (several entries on same pivot in EUR/USD example [04:00-05:00]), suggesting high-frequency intraday trading.
