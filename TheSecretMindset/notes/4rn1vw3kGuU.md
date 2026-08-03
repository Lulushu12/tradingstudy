# ADX DMI Day Trading Strategy | How To Use The ADX Indicator

- video_id: 4rn1vw3kGuU
- url: https://www.youtube.com/watch?v=4rn1vw3kGuU
- duration: 10:32
- classification: STRATEGY

## Summary

This video presents a day trading strategy using ADX (Average Directional Movement Index), DMI (+DI and -DI), and On Balance Volume (OBV) as a trend confirmation filter. The strategy trades DMI crossovers in the direction of the OBV trend. Entry signals come from DMI crossovers; trades are only taken when ADX is above 25 and OBV momentum confirms the direction.

## Instruments and timeframes stated

- markets: Forex, stocks, indices (Apple, Netflix, Dow Jones, GBP/JPY, EUR/USD mentioned as examples)
- timeframes: 4-hour (example shown) [07:00], higher timeframes recommended [05:30]
- sessions/hours: NOT STATED

## Strategy 1: DMI Crossover with OBV Confirmation

### Indicators and settings

- ADX: threshold = 25 (for strong trend), alternative threshold = 20 for faster signals [01:30], 50+ = very strong trend [04:30]
- Positive Directional Movement Indicator (+DMI): period = NOT STATED
- Negative Directional Movement Indicator (-DMI): period = NOT STATED
- On Balance Volume (OBV): period = NOT STATED
- Simple Moving Average applied to OBV: period = 100 [07:00]

### Context / bias filter

ADX must be above 25, indicating a strong trend [01:00]. Before entering any trades, determine the main trend direction using the 100 SMA applied to OBV: when OBV is above its 100 SMA, bullish momentum is present; when below, bearish momentum [07:00]. Only take trades in the direction of this OBV momentum. Avoid trading when ADX is below 25, as the market is in accumulation or distribution [02:30]. Do not trade on "choppy" signals [08:00] or in ranging/low-volatility markets [09:00].

### Entry trigger

Long: +DMI (green line) crosses above -DMI (red line) [06:30], confirmed when OBV momentum is bullish [07:00]. Short: -DMI crosses above +DMI [06:30], confirmed when OBV momentum is bearish [07:00].

### Stop loss

NOT STATED

### Take profit / exit

The speaker states "I personally go for a 2:1 or 3 to 1 risk reward ratio, when I'm trading stocks that have good volatility" [09:30]. The exact exit price or profit target mechanism is not defined beyond the risk/reward ratio.

### Invalidation / skip conditions

Exit all trades when ADX drops below 25, signifying end of trend or entry into non-trending zone [02:30]. Skip trades if OBV momentum does not align with the DMI crossover signal. Do not trade on "ranging markets or instruments with low volatility" [09:00].

### Claimed performance

No explicit win rate or profit percentage claimed. The speaker shows example charts with multiple winning and losing trades and states the strategy "is efficient on higher timeframes and on instruments with some volatility" [09:00].

### Vagueness log

1. UNDEFINED-PARAM: +DMI and -DMI period not stated; OBV period not stated
2. UNDEFINED-RULE: "choppy signals" - no definition of what constitutes a choppy signal; how to identify or filter them
3. UNDEFINED-RULE: "instruments with some volatility" - no specific ATR threshold or volatility measure given [09:00]
4. SUBJECTIVE: Stop loss placement not mentioned; risk determination subjective without stated method
5. UNDEFINED-RULE: Entry confirmation criterion "OBV and 100 SMA align" - exact tolerance or degree of alignment not specified

### Mechanizability

PARTIAL. The DMI crossover is mechanically definable, and OBV with 100 SMA can be computed. However, the confirmation rule (when to consider OBV and the signal as "aligned"), the definition of "choppy signals," and the exact stop loss placement are not mechanically specified. A coder must make assumptions about alignment tolerance and choppy-signal filtering, which introduces discretion not stated by the speaker.

## Notable claims and caveats

The speaker emphasizes that ADX is a lagging indicator and may cause traders to miss the inception of the trend [05:30]. He also warns that ADX "offers many false signals when used on shorter timeframes" [05:30], and thus recommends trading on higher timeframes. The strategy explicitly requires combining ADX with other tools; ADX alone is insufficient [05:30-06:00]. The speaker stresses that "price is the single most important signal on a chart" and advises reading price first, then ADX in context [09:30]. No mention of spread, slippage, or commission. Trade management depends on trader personality and trading plan [09:00].
