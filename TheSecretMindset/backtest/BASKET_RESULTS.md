# Basket results: 87 crypto perpetuals

Same spec, same parameters as the single-symbol run. Only the number of instruments changed.
Full output in `results/basket_summary.csv`.

## Basket

87 USDT-quoted Binance USD-M perpetuals whose daily archive begins on or before 2021-01,
selected by that availability rule alone and never by performance. **11 are delisted** and
were kept, so the basket is not a set of survivors. 85 have enough history for the EMA200
warmup on daily, 86 on 4h. 177,458 daily bars and roughly 1.06M 4h bars, all from the official
`data.binance.vision` archive, the same venue as the files already in this repository.

Studied span ends 2024-12-31. The holdout from 2025-01-01 was never loaded.

## The control

| Buy and hold every basket member, daily, same costs | |
|---|---|
| Median symbol return | **+8.1%** |
| Mean symbol return | +401.8% |
| Median max drawdown | **-94.7%** |
| Symbols with positive return | 55.3% |

This is a much fairer test bed than BTC alone. On BTC the buy-and-hold control returned +799%
and swamped everything; across the basket the median coin gained 8% while drawing down 95%.
A strategy here has to earn its result rather than inherit it.

## Results

Mean R per trade. The month-block interval is the one that counts: crypto's dominant
dependence is cross-sectional at a point in time, so 87 coins inside one month are close to
one observation, not 87. Bonferroni corrects for four strategy families.

| run | trades | mean R | naive 95% CI | month-block 95% CI | Bonferroni | % symbols +ve |
|---|---|---|---|---|---|---|
| s1_flat | 4522 | +0.065 | +0.053 to +0.078 | +0.009 to +0.131 | includes 0 | 95.3% |
| s1_flip | 8979 | +0.029 | +0.023 to +0.036 | +0.002 to +0.062 | includes 0 | 83.5% |
| s2_mid | 4434 | +0.258 | +0.188 to +0.332 | +0.060 to +0.489 | +0.014 to +0.567 | 77.6% |
| s2_band | 11774 | +0.037 | +0.021 to +0.053 | includes 0 | includes 0 | 67.1% |
| s3_atr | 2925 | +0.104 | +0.017 to +0.206 | includes 0 | includes 0 | 45.9% |
| s3_nostop | 2908 | +0.013 | includes 0 | includes 0 | includes 0 | 47.1% |
| s4 | 374 | +0.252 | +0.098 to +0.426 | +0.064 to +0.438 | +0.002 to +0.501 | 63.0% |
| s1_flat_4h | 30404 | +0.005 | +0.004 to +0.007 | includes 0 | includes 0 | 90.7% |
| s1_flip_4h | 60391 | +0.001 | +0.000 to +0.002 | includes 0 | includes 0 | 60.5% |

Note the gap between the naive and month-block columns. Seven of nine runs look significant
on the naive interval and are not. `s1_flip_4h` is the clearest illustration: +0.001R over
60,391 trades is statistically distinguishable from zero and economically worthless, being
roughly the size of one round-trip cost.

## Final answer: nothing survives

Two runs cleared correction and doubled costs: **s2_mid** and **s4**. Both then failed a
routine outlier check.

| | mean R | top 1% winsorised | dropping best 5 trades | winsorised Bonferroni CI |
|---|---|---|---|---|
| s2_mid | +0.258 | +0.169 | +0.205 | **-0.022 to +0.382, includes 0** |
| s4 | +0.252 | +0.196 | +0.134 | **-0.031 to +0.404, includes 0** |

s4's five best trades out of 374 carry **47.4%** of its total R, with a single trade at
+14.85R. s2_mid's best single trade is +73.91R. Cap the top 1% at the 99th percentile, which
is a mild adjustment and not a hostile one, and both intervals cross zero.

An edge that exists only in its own top 1% of trades is not an edge you can size or survive.
It is a small number of lucky trends. Across four strategies, nine configurations, 87
instruments and five years, **none of them demonstrates an edge that holds up.**

## What is still worth noting

**s4 was the most broadly distributed result before the outlier test.** 374 trades, 58.6% win
rate, positive in four of five calendar years, 63% of symbols positive, and a coherent trade
profile: lose 1R, or take the 1R partial and stop at breakeven for about +0.5R, with a rare
trailed winner. It is the only one of the four that behaved like a designed system rather than
like an accident. It is also the one whose signal is rarest, which is why it needed the basket:
387 signals across 85 symbols, against 4 on BTC alone in the same span. That is confirmation
that the creator's framing was right, it is a scanning strategy, not a single-chart strategy.
It still does not clear the bar.

**The regime table is kinder to s4 than to anything else.**

| net R by year | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| s2_mid | 37.5 | **518.7** | 148.5 | 172.2 | 268.8 |
| s4 | -14.0 | 26.5 | 20.2 | 43.8 | 17.8 |

s2_mid earns 45% of its total in 2021 alone. s4 is the only run whose yearly record does not
lean on one bull year.

## A bug that inverted a result

The first basket run reported s4 at -1.007R with 0% of symbols positive, every trade a stop-out
and not a single partial recorded. That was an engine bug, not a market fact. Under the tiered
exit, a trade that scaled out at 1R and then closed its remaining half was passed to the close
routine with frac=0.5, which treated the final close as another partial and **never recorded
the trade**. Every s4 winner was being deleted; only clean stop-outs reached the statistics.

The single-symbol BTC result reported earlier suffered from the same bug and has been re-run:
s4 there is now 4 trades, profit factor 1.25, mean R +0.134, still undecidable on 4 trades.

This is the second bug in this project that flipped a verdict, after the Donchian midpoint exit
being modelled as a target instead of a give-back. Both were caught because a result looked
structurally impossible rather than merely disappointing. That is not a reliable detector, and
the honest conclusion is that some smaller errors are probably still in here.

## What has not been done

- The holdout is untouched.
- No portfolio model. Each symbol runs an independent equity track; concurrent positions across
  87 correlated coins would drawdown together and that is not modelled. No portfolio-level
  return is claimed anywhere in this file.
- Sensitivity to the invented parameters has not been mapped. S2's two exits, both offered by
  the video as interchangeable, differ by roughly 7x in mean R. The other invented values
  deserve the same treatment and have not had it.
- These are stock and forex strategies run on crypto. That transfer assumption applies to
  every number here and was never tested.
