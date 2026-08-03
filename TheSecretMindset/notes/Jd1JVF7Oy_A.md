# The FASTEST & Most AGGRESSIVE EMA Indicators For ZERO Lag Scalping Trading

- video_id: Jd1JVF7Oy_A
- url: https://www.youtube.com/watch?v=Jd1JVF7Oy_A
- duration: 13:03
- classification: TOOLING

## Summary
This video explains Double Exponential Moving Average (DEMA) and Triple Exponential Moving Average (TEMA) indicators as alternatives to traditional moving averages for scalping and short-term trading. It describes how these indicators reduce lag, hug price action more closely, and can be used for trend analysis, dynamic support/resistance identification, and entry triggers. The video emphasizes volume confirmation and slope analysis but does not present a complete mechanizable strategy.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: Daily example shown; 10-day and 50-day crossovers mentioned [08:00]; 50-day and 200-day for longer-term [08:00]
- sessions/hours: NOT STATED

## Indicator descriptions

### Double Exponential Moving Average (DEMA) [00:00-02:00]
- Reduces lag of traditional EMA by allocating more weight to recent data points [00:00-00:30]
- Formula: combination of single and double EMA that results in another EMA (uses EMA of another EMA) [01:30]
- More responsive to recent price action; closer to price than SMA or EMA [01:00]
- More sensitive to market volatility [01:30]
- Lower period DEMA more volatile and incorporates price changes more accurately [02:30]

### Triple Exponential Moving Average (TEMA) [02:30-03:30]
- Uses triple smooth EMA along with single and double smoothers [02:30-03:00]
- Even more sensitive to recent price action than DEMA [03:00]
- Better suited for short-term trading due to more sensitive nature [03:00]
- Reacts to price changes quicker than DEMA [03:00-03:30]

## Trading applications

### Method 1: Trend Analysis [03:30-04:30]
Use DEMA or TEMA direction to identify market trend:
- Price above DEMA/TEMA with line sloping upward: uptrend [04:00-04:30]
- Price below DEMA/TEMA with line sloping downward: downtrend [04:30]
- Price trading sideways with flat moving average: no trend/no clear direction [04:30]

### Method 2: Dynamic Support and Resistance [05:30-06:30]
DEMA/TEMA can identify dynamic support/resistance levels:
- In uptrend: DEMA/TEMA acts as support level [05:30-06:00]
- In downtrend: DEMA/TEMA acts as resistance level [06:00]
- Price moves away from indicator then pulls back: creates support/resistance area [05:30-06:00]

**Important caveat [06:00-06:30]**: "This movement depends on the proper look back period for the moving average. If the indicator didn't provide support or resistance in the past it probably won't be doing this in the future" [06:30]

### Method 3: Entry Trigger [07:00-08:30]

**Simple crossover [07:00-07:30]**
- Long entry: price crosses above DEMA/TEMA line [07:00]
- Short entry: price crosses below DEMA/TEMA line [07:00]

**Moving average crossover signals [07:30-08:30]**
- Shorter-term EMA crosses above longer-term EMA: bullish signal [07:30]
- Shorter-term crosses below longer-term: bearish signal [07:30]

**Examples of timeframe combinations [08:00]**
- Short-to-medium term: 10-day and 50-day moving averages
- Longer-term: 50-day and 200-day moving averages

**Three-moving-average crossover system [08:30]**
- Bullish: medium-term above long-term AND short-term crosses above medium-term [08:30]
- Bearish: long-term above medium-term AND short-term crosses below medium-term [08:30]

**Caveat [08:00-08:30]**: "A crossover signal may come very late in the new trend and this lateness is increased as the length of the moving averages increases" [08:00-08:30]

### Method 4: Volume Filtering [09:30-10:30]
Use volume to filter false signals:
- Ignore DEMA/TEMA crosses during low trading volumes [10:00-10:30]
- Enter only when price crosses DEMA/TEMA during high trading volumes [10:00-10:30]
- "Low volumes are the major causes for the sideways price action" [09:30-10:00]

Example: signals ignored during light volume range, entered when volume increased and price formed bullish candle [10:30]

### Method 5: Slope Analysis [10:30-11:00]
Monitor the angle/slope of DEMA/TEMA line:
- Line sloping up: price moving up [10:30-11:00]
- Line angled down: price moving down [10:30-11:00]
- Caveat: small lag still exists; indicator may not change angle immediately when price changes quickly [11:00]

## Vagueness log
1. **UNDEFINED-PARAM**: DEMA/TEMA period not specified for trend analysis method [03:30-04:30]
2. **UNDEFINED-PARAM**: Specific look-back period for support/resistance NOT STATED; only states it must have worked in past [06:00-06:30]
3. **UNDEFINED-RULE**: What constitutes "strong continuing trend" for best performance of crossovers [08:30]
4. **UNDEFINED-PARAM**: Exact volume threshold - what is "high volume" vs "low volume"? [09:30-10:00]
5. **UNDEFINED-PARAM**: How steep must slope be to constitute clear direction? [10:30-11:00]
6. **SUBJECTIVE**: Visual identification of trend slope change [11:00]

## Limitations and caveats [11:30-12:30]

- DEMA/TEMA work well in trending markets but provide little insight in choppy/range-bound markets [11:30-12:00]
- Price frequently crosses back and forth across lines in choppy conditions [11:30]
- Reduced lag can be good (exits quickly on actual reversals) or bad (over-trading on minor moves) [12:00-12:30]
- Reduced lag can cause premature exits: "You close your position only to watch the price continuing in its original direction" [12:30]
- Example: if incorrect period chosen, indicator tells you to close position on minor move against you [12:00-12:30]
- "Choosing the correct length is very important. It's up to you to find the balance and determine exactly how much lag works for you" [12:30]

## Mechanizability
PARTIAL. DEMA and TEMA are standard indicators with defined formulas, crossovers are mechanical, but 6 specific gaps must be filled by assumption: (1) DEMA/TEMA period selection for trend, (2) look-back period for support/resistance validation, (3) definition of "strong continuing trend", (4) volume threshold between high and low, (5) slope steepness threshold, (6) period selection methodology for crossover systems.

## Notable claims and caveats
- "Double EMA was developed in order to reduce the lack of traditional moving average indicators and to provide more timely entries" [00:30]
- "Double EMA hugs the price action better than both SMA and EMA" with "least deviations" [01:00-01:30]
- "Triple EMA reacts to price changes quicker than double EMA" [03:00-03:30]
- "Sometimes lag is good and sometimes it isn't. It depends on what you want from the indicator" [12:30]
- No specific win rate or performance statistics provided
- No discussion of costs, spreads, slippage, or commissions
- No drawdown or risk management details
- Educational framework only, not a complete strategy
