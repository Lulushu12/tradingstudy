# Altcoin / "Shitcoin" Study — Findings

Question asked: can the knowledge from the BTC study be turned into a trading strategy, or
at least a viable business plan, for shitcoins?

Short answer: **yes, but it is the opposite of what most people try, it is a worse product
than it looks, and it is incompatible with the prop-firm account this repo was originally
built around.**

---

## Data

Binance USDT-margined perpetuals, pulled from the public Binance data archive.

- **786 symbols, every USDT perp ever listed**, 4H bars, 2020-01 to 2026-06 (3.52M bars).
- **Survivorship-bias free.** The archive retains delisted and dead symbols
  (1000LUNCBUSD, 1000SHIBBUSD, FTMUSDT and similar). Backtests built from a current
  top-200 list are wrong in a way that always flatters the long side; this one is not.
- **Real funding history** for all 787 symbols (2.42M funding stamps), so carry is measured,
  not assumed.
- **15-minute bars for all 407 signal-generating symbols (1.6 GB)**, used to resolve every
  trade on the true intrabar path — the same standard `study/STRATEGY_FINDINGS.md` used
  for BTC.

Costs charged throughout: **10bp round-trip fee (Binance taker) + 5bp entry slippage**, and
actual funding paid or received over the exact holding period.

---

## 1. The structural fact that drives everything

Buy a randomly chosen Binance perp on its listing day and hold:

| | all 786 |
|---|---|
| median return | **-81.2%** |
| share of coins with a positive return | **16.5%** |
| median decay from peak to latest | **-92.9%** |
| median best-case exit (MFE from listing) | +76.1% |
| p95 / p99 return | +99% / +1195% |

Coins listed in 2024 or later are no better (median -77.4%).

Two consequences:

1. Even with **perfect timing**, the median coin only offers about +76% before it dies. The
   fat right tail is real but it is p99, not a plan.
2. The drift is strongly negative. Any long-biased shitcoin strategy is fighting the base
   rate. Any short-biased one has the base rate as a tailwind.

Note on "death": only 3.6% of symbols were actually delisted. Coins on Binance do not
usually get removed — they just go to zero while remaining tradeable. So the risk is not
delisting, it is decay.

---

## 2. The BTC edge transfers to alts — and it is almost entirely short

Applying the **exact** surviving strategy from `study/STRATEGY_FINDINGS.md`, unchanged and
untuned (4H, close vs EMA200 trend filter, volume > 1.8x its 20-bar average, bar closes in
the trend direction, stop 1.5 x ATR14, target 2R, entry next bar open):

| universe | n | expectancy |
|---|---|---|
| BTC only (the original study) | 490 | +0.087R |
| liquid alts, long side | 9,540 | **-0.096R** |
| liquid alts, short side | 10,457 | **+0.097R** |

This is a genuine out-of-sample test of the rule set: the parameters were derived on BTC in
the earlier study and not touched here.

The gain over the BTC study is **not** a bigger per-trade edge — it is the same edge with
**21x the sample**, because you run it across hundreds of instruments at once. BTC alone
produced a t-stat of 1.3, which is nothing. That is the actual case for going wide.

Universe selection is **point-in-time**: a signal only counts if that symbol's *trailing*
30-day median volume already exceeded $50M/day. An earlier version that filtered on
full-history volume was picking known winners in advance; that bias is removed.

---

## 3. Statistical honesty

Trades cluster heavily (all alts move together), so naive t-stats lie. Using a **monthly
block bootstrap**, which resamples whole calendar months and preserves that clustering:

| book | expectancy | 95% CI | P(edge <= 0) |
|---|---|---|---|
| **short** | +0.097R | [+0.007, +0.179] | **0.019** |
| **long** | -0.096R | [-0.162, -0.029] | 0.998 |
| both sides | +0.005R | [-0.041, +0.053] | 0.421 |

Read this carefully. The short edge clears zero, but the lower bound of the confidence
interval is **+0.007R — effectively zero**. The finding that is genuinely solid is the
*negative* one: **buying altcoin volume-spike breakouts is a reliable, statistically strong
loser.** That result is far more certain than the short edge is.

Per-year net R per trade:

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| long | -0.01 | -0.07 | -0.13 | -0.09 | -0.13 | -0.07 | -0.15 |
| short | +0.34 | **-0.02** | +0.26 | **-0.10** | +0.11 | +0.11 | +0.10 |

Longs lose in all seven years. Shorts win in five of seven, losing in 2021 (alt bull) and
2023 (grind). It is not purely a regime bet — shorts are positive in alt bull markets too
(+0.051R) as well as alt bears (+0.107R) — but the good years are the bad years for alts.

### The modelling assumption that mattered most

How stops fill is worth more than the signal itself:

| assumption | short-book expectancy |
|---|---|
| 4H bars, stops fill exactly at the stop price | +0.132R (fantasy) |
| 4H bars, stops fill at the bar close | +0.041R (too harsh) |
| **15m path, stops fill at the 15m close** | **+0.097R (best estimate)** |

Worst single trade -7.02R. 1.36% of shorts lose more than 1.5R. The squeeze tail is real
and stop orders do not protect you from it.

---

## 4. What the product actually feels like

Portfolio simulation: 0.5% equity risk per trade, max 8 concurrent positions, compounding.

| | short alt book | BTC study, for comparison |
|---|---|---|
| CAGR | +29.8% | +21.6% |
| max drawdown | **-38.5%** | -12.3% |
| Calmar | 0.78 | 1.76 |
| positive months | **53%** | 67% |
| longest losing streak | **41 trades** | 9 trades |

And the number that matters most:

> **77% of all profit came from the best 5 months out of 77.**
> Only 53% of months were positive at all.

This is not an income strategy. It is a **crash-harvesting / convexity** strategy that
bleeds slowly and gets paid in bursts when alts break. The top 10 symbols of 386 produced
33% of the P&L.

Two hard implications:

- **It is incompatible with a prop firm account.** Breakout-style rules cap drawdown around
  6-10%. This book draws down 38% and can lose 41 trades in a row. Running it on a funded
  account fails the account, not the strategy.
- **It is psychologically the hardest possible product** for a trader whose intuition was
  built on 15m divergence entries: you are short, alone, wrong for months at a time, and
  most of your year arrives in about three weeks.

### Cost headroom

Dies at roughly **+25bp/side of additional slippage** beyond what is already charged. That
is real but not generous, and slippage on a $50M/day alt during a crash — exactly when the
strategy makes its money — is worse than in calm conditions. Treat the headroom as thinner
than it looks.

---

## 5. Capacity — the business-plan ceiling

Median stop distance is 5.4% of price, so a 0.5%-risk position is about 0.09x equity in
notional. Constraining each position to a sane share of that symbol's daily volume:

| position size cap | account ceiling |
|---|---|
| 0.5% of daily volume | ~$4M |
| 1.0% of daily volume | ~$8M |
| 2.0% of daily volume | ~$16M |

So the honest business shape:

- **$100k account → ~$30k/year with a 38% drawdown.** Not a living, and a brutal ride.
- **$1M account → ~$300k/year.** A real business.
- **Above ~$10M it stops scaling.** Capacity-capped.

The 8-position cap already rejects 64% of signals, so the strategy is signal-rich and
capital-poor. Adding concurrency raises CAGR but that is leverage on a correlated book, not
more edge — drawdown rises just as fast.

---

## 6. What this means, plainly

**The strategy that is supported by the evidence:** a systematic, short-biased,
volume-spike trend-continuation book run across the whole liquid alt perp universe, sized
small, held about a day, with the long side switched off entirely.

**The single most valuable finding is defensive.** With P = 0.998, buying altcoin breakouts
loses money persistently. If any current activity is long-biased alt momentum, stopping is
worth more than adopting anything new here.

**Where the edge comes from** is structural, not technical: alts have severe negative drift,
retail buys volume spikes, and perp funding mildly pays shorts (61% of symbols have
positive mean funding). That is a plausible, durable reason for the edge to exist, which is
worth more than the backtest is.

**The business plan is capital-gated and psychologically brutal**, not a route from a small
account to an income. It needs patient capital that can sit through a 38% drawdown and a
year like 2021 or 2023.

---

## 7. What I did not do, and what would change the verdict

Being explicit, in the spirit of `CLAUDE_CODE_PROMPT.md`:

1. **No holdout was reserved.** 2025-2026 was used as a test split, but I have now seen it.
   A true blind holdout should be designated before any of this is traded.
2. **"Short only" was chosen after seeing the per-side results.** It is defensible because
   the -81% median drift is independent prior evidence, not a backtest artifact — but it is
   still a post-hoc selection and should be discounted accordingly.
3. **Everything is Binance.** Feed, fee schedule and funding are Binance's. A different
   venue changes the numbers.
4. **Fills are still modelled.** 15m-path resolution is much better than 4H, but a stop that
   trades through in a squeeze may fill worse than the 15m close.
5. **Not tested:** the lower-variance businesses this data could support — funding/basis
   harvesting, listing-event effects, cross-sectional momentum ranking, and market making.
   Given that 77% of P&L arrives in 5 months, a carry sleeve to pay the bills between
   bursts is the obvious next question, and I have the funding data to test it.

Surviving these tests means "not yet falsified". Nothing more.

---

## Reproduce

```
altcoin_study/build.py           # 19,723 monthly 4H zips  -> panel_4h.parquet
altcoin_study/build_funding.py   # 18,920 funding zips     -> funding.parquet
altcoin_study/a_universe.py      # survivorship-free base rates
altcoin_study/b_transfer.py      # does the BTC edge transfer? cost sweep
altcoin_study/c_portfolio.py     # portfolio sim with concurrency + funding
altcoin_study/d_honest.py        # point-in-time universe, regimes, capacity
altcoin_study/e_kill.py          # gap/squeeze risk, block bootstrap, cost cliff
altcoin_study/f_truth.py         # resolve every trade on the true 15m path
altcoin_study/g_final.py         # final verdict
```

Data is fetched from `https://data.binance.vision` (no API key required) and is not
committed — the download scripts regenerate it.
