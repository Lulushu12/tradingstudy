# Pre-registration — H3-Multi (multi-asset replication of H3)

**Committed before the test was run.** No strategy code has been executed against any of the
25 new assets at the time of writing.

---

## This is a replication, not a variant

The H3 registration carried a standing commitment: *H3 is the last variant of this bar shape
that will be tested, whatever the result.*

H3-Multi does not breach it. **Zero parameters change.** The entry thresholds, direction,
stop multiple, target, time stop and gap guard are all imported from `hypothesis_h3.py`,
which imports the bar identification from `hypothesis_h1.py`. Nothing is re-tuned, and no
alternative rule is being searched.

What changes is only the **sample**. H3's own conclusion named the binding constraint
precisely: at the observed effect size, resolving it needs ~6,000 trades against the 467
available — about 13× the data — and *"widening to more assets gets there faster than
waiting."* This is that widening, and nothing else.

## The universe — selected mechanically

Chosen by a rule fixed before any test, with no discretion over membership:

1. USDT **spot** pairs on Binance with `TRADING` status.
2. Excluding stablecoins, wrapped/staked proxies and FX pairs by name pattern
   (`USDC, FDUSD, TUSD, BUSD, DAI, USDP, EUR, TRY, BRL, WBTC, WBETH, BETH, PAXG, XAU, USD1,
   RLUSD`).
3. **Must have a 1h candle at the first bar of the EARLY window** (2023-03-02 13:00 UTC).
   This coverage test is what makes the list usable: ranking by today's volume alone returns
   tokenized equities, stablecoin pairs and 2025 listings, all of which fail coverage
   automatically.
4. Of those that survive, the **top 28 by 24h quote volume**.
5. **ETH, LINK and SOL are removed from the primary test** and reported separately as
   context, because every rule in this study was derived on them.

That leaves **25 assets that no part of this study has ever touched**: BTC, BNB, XRP, ZEC,
ADA, TRX, DOGE, BICO, UNI, NEAR, DEXE, AAVE, AVAX, LTC, XLM, FIL, FET, ALGO, DOT, INJ, HBAR,
SHIB, COTI, SYN, WAXP.

Any symbol whose fetch returns fewer than 10,000 bars for a window is dropped from that
window and the drop is reported.

## The test

H3, unchanged, on all **three** windows (EARLY, PRIOR, MAIN). For these 25 assets all three
windows are equally virgin — the rule was never fitted to any of them — so pooling across
windows is legitimate here in a way it explicitly was not for ETH/LINK/SOL.

Expected sample: roughly 150 trades per asset per window, so on the order of **10,000–12,000
trades**, comfortably past the ~6,000 that H3 identified as the resolution threshold.

## Statistics — the part that matters most here

Crypto majors are **highly cross-correlated**. Twenty-five assets do not supply twenty-five
times the independent information; when BTC dumps, most of the universe produces a signal in
the same direction within the same hour.

**Naive per-trade resampling would badly overstate significance**, and with a sample this
size it would almost certainly manufacture a false positive.

So the block bootstrap resamples **calendar-week blocks spanning the entire universe**: a
drawn week brings *every asset's* trades from that week together, preserving cross-sectional
correlation. 8,000 resamples. This is registered now precisely because it is the choice that
makes the test harder, and it would be easy to quietly not make it later.

## Success criteria — fixed in advance

- **SUPPORTED:** pooled mean R > 0, the **95%** cross-sectional block-bootstrap CI excludes
  zero, **and** the mean is positive in **≥ 60% of individual assets**, **and** positive in
  **all three windows**.
- **SUGGESTIVE:** pooled mean R > 0 and positive in ≥ 60% of assets, but the CI includes zero.
- **NOT SUPPORTED:** anything else.
- **UNDERPOWERED:** pooled n < 3,000.

## Not allowed after seeing results

- Changing any H3 parameter, or the universe, or the window set.
- Dropping individual assets that perform badly, for any reason offered afterwards.
- Substituting per-trade bootstrap for the cross-sectional one because it gives a tighter
  interval.
- Reporting the limit-entry variant as the headline if the market-entry primary fails.

## What a pass would and would not mean

A pass would mean the effect survives on 25 assets it was never derived from, across three
regimes including a bull market, under a bootstrap that respects cross-asset correlation.
That is a genuinely strong result by backtest standards.

It would still **not** mean the strategy is deployable. It would remain: one exchange, spot
candles used as a proxy for perp execution, funding modelled as a constant, no order-book
depth, and a signal whose per-trade edge is small enough that fee-tier changes matter. The
correct next step after a pass is forward testing on data that does not exist yet — not
deployment.

## Known limitations

- **Survivorship bias.** The universe is drawn from pairs trading *today*; assets delisted
  between 2023 and now cannot appear. The direction of this bias on a bar-shape signal is not
  obvious, but it exists and is not corrected.
- Volume-ranked selection favours assets that grew into liquidity over the period.
- Spot candles are used throughout; the cost model assumes perp-style taker/maker fees and
  funding.
