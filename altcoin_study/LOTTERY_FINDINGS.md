# The Lottery-Ticket Thesis — Findings

The question: forget shorting liquid perps. Buy small tickets in random shitcoins, let them
run, accept that most go to zero, get paid by the fat right tail. Is that a strategy, or at
least a business?

**Verdict: it was a real strategy in 2020-2021. It has been a negative-expectancy game
since 2022, and the reason it fails is structural, not a matter of picking better.**

---

## 1. What the lottery actually pays

Survivorship-free: all 786 Binance USDT perps ever listed, dead ones included. Buy at
listing, equal weight.

| | reached at some point | still there at the end |
|---|---|---|
| 2x | 39.5% | 5.1% |
| 3x | 27.1% | 3.2% |
| 5x | 16.8% | 1.8% |
| **10x** | **8.3%** | **1.2%** |
| 50x | 1.7% | 0.0% |
| 100x | 0.5% | 0.0% |

Median coin peaks at **1.61x** and ends at **0.19x**. The best coin in six years peaked at
332x (AXS).

So the 10x is real — 1 in 12 coins touches it. But *holding* it is not: 7 of every 8 coins
that reach 10x give it all back.

---

## 2. The exit rule matters far more than the pick

Equal-weight ticket in every coin, buy at listing, benchmarked against just holding BTC over
the identical window:

| exit rule | mean | median | P(>10x) | vs BTC |
|---|---|---|---|---|
| **hold to today / death** | **0.75x** | 0.19x | 1.2% | **-0.71** |
| take profit at 2x | 1.01x | 0.89x | 0.0% | -0.24 |
| take profit at 10x | 1.21x | 0.19x | 0.0% | -0.25 |
| trailing stop 50% off peak | 1.21x | 0.73x | 0.8% | **+0.11** |
| **trailing stop 70% off peak** | **1.32x** | 0.60x | 1.2% | +0.07 |
| free ride: bank stake at 3x, trail rest | 1.31x | 0.42x | 1.4% | +0.00 |
| hard stop -50%, else hold | 0.77x | 0.50x | 0.5% | -0.48 |

Three things fall out:

- **"Buy and hold forever" is the worst rule tested.** 0.75x mean, -71% versus BTC. Diamond
  hands are the single most expensive habit in this game.
- **Tight take-profits destroy the thesis.** Selling at 2x caps you out of the only outcome
  that pays.
- **Wide trailing stops are the only rules with a positive mean.** You must let it run *and*
  you must eventually leave. That combination is the entire edge.

Even the best rule beats BTC by only +0.07 to +0.11 on the mean, while **losing to BTC on
70-74% of individual tickets**.

Entering at a random point in a coin's life instead of at listing is worse across the board
(trailing-50% falls from 1.21x to 1.03x). Being early is most of what you are being paid for.

---

## 3. When it worked — and it stopped working in 2022

Listing cohort, trailing 70% rule:

| cohort | n | mean | median | P(>5x) | P(>10x) | vs BTC | beat BTC |
|---|---|---|---|---|---|---|---|
| **2020** | 80 | **4.29x** | 1.84x | 20.0% | 7.5% | +1.82 | 40.0% |
| 2021 | 58 | 1.03x | 0.46x | 5.2% | 1.7% | +0.23 | 19.0% |
| 2022 | 26 | 0.89x | 0.38x | 3.8% | 0.0% | -0.43 | 15.4% |
| 2023 | 99 | 0.93x | 0.66x | 0.0% | 0.0% | **-0.95** | 8.1% |
| 2024 | 131 | **0.65x** | 0.45x | 0.8% | 0.0% | -0.58 | 6.1% |
| 2025 | 241 | 1.17x | 0.46x | 1.2% | 0.8% | +0.23 | 22.8% |
| 2026 | 146 | 0.98x | 0.93x | 0.0% | 0.0% | +0.14 | 61.0% |

The entire lottery was the **2020 cohort riding the 2021 bull**. Since 2022 the mean sits at
or below 1.0x and P(>5x) is essentially zero. The 2026 cohort is only a few months old and
tells us nothing yet.

Note: an earlier cut of this ranked coins by *full-history* volume and appeared to show big
coins paying 9x. That was circular — "ended up with $200M/day volume" is a label for "won".
Re-run with **first-30-day volume**, which is what you actually know when you buy, the tier
effect largely disappears and the small tiers do not outperform.

---

## 4. The diversification paradox — why this cannot be fixed by buying more tickets

Bootstrap, best rule, small listings (<$20M/day at listing):

**All listings including the 2020-21 bull** — the lottery works and scale helps:

| tickets | median | P(lose money) |
|---|---|---|
| 10 | 1.23x | 32.1% |
| 50 | 1.49x | 5.9% |
| 100 | 1.61x | 1.0% |

**Small listings from 2022 onward** — the lottery is dead and scale *hurts*:

| tickets | median | P(lose money) | P(>2x) |
|---|---|---|---|
| 10 | 0.85x | **74.7%** | 0.3% |
| 25 | 0.88x | 75.6% | 0.0% |
| 50 | 0.89x | 79.7% | 0.0% |
| 100 | 0.90x | **86.3%** | **0.0%** |

This is the crux of the whole idea, and it is a mathematical trap:

> Diversification only rescues a lottery if the **mean ticket is above 1.0x**. Post-2021 the
> mean small-cap ticket is **0.91x**. Below 1.0x, buying more tickets does not reduce your
> risk — it makes losing *more certain*, because you converge on a losing mean.

And the tension is unavoidable: the concentration that makes it a lottery is exactly what
you have to destroy to make it survivable. In the full sample, going from 1 ticket to 200
raises the median from 0.60x to 1.25x but drops **P(>2x) from 10.9% to 3.3%**. You cannot
buy both the upside and the safety.

---

## 5. Real memecoins, measured directly

Everything above is Binance-listed coins — the *favourable* end. A coin that earns a Binance
perp listing already survived a brutal funnel. So I went to the DEX data (GeckoTerminal,
Solana/Base/BSC).

**First finding, unplanned: the entire top of the DEX volume leaderboard is pools created in
the last 24-48 hours.** That churn *is* the memecoin market. There is no stable population
of small caps to sample — there is a conveyor belt.

Following 43 of the day's highest-volume launches minute by minute:

- Median peak **1.14x** from first observable price; median final **1.04x**.
- Median time to peak: **284 minutes**. 16% peaked within the first hour.
- Buying 30 minutes in and holding: **median 1.01x**, P(>1x) 62.8%.
- With a realistic 5% round-trip cost: **median 0.96x**, P(>1x) falls to **46.5%**.

And the decisive number:

> Mean outcome **75.8x**. Median outcome **1.01x**.
> **One coin (a 3,141x) accounted for 96.4% of all proceeds in the sample.**
> Bootstrap 95% CI on that mean: **[1.33x, 223x]** — statistically meaningless.
> Remove that one ticket and the mean collapses from 75.8x to 2.79x.

That is the lottery in its purest form, and it is also the reason you cannot run it as a
business: an expectation you cannot estimate is an expectation you cannot size against.

**Sample limits, stated plainly:** n=43, one day's launches, top-volume pools only, no rugs
and no failed launches included, no fees charged in the raw figures. Every one of those
biases flatters the lottery. It is indicative, not conclusive — but it points the same way
as the Binance data, which is conclusive.

---

## 6. What friction does

On Binance-listed coins with the best rule (baseline mean 1.32x):

| round-trip cost | mean | vs BTC |
|---|---|---|
| 0.1% (Binance perp) | 1.32x | +0.07 |
| 5% | 1.25x | +0.00 |
| 10% | 1.18x | -0.06 |
| 20% | 1.05x | -0.20 |

Plus rug risk — the tickets that go to *exactly* zero, which Binance coins essentially never
do and DEX tokens routinely do:

| rug rate | mean @10% cost |
|---|---|
| 0% | 1.18x |
| 10% | 1.11x |
| **20%** | **0.90x** |
| 30% | 0.81x |

Breakeven: with no rugs the basket tolerates a 24% round trip. **At a 20% rug rate it is
already below 1.0x before you pay any costs at all.** Beating BTC is a much higher bar again
— that goes at roughly 5% round-trip cost.

Real DEX friction (0.6-2% LP fee each way, priority fees, MEV sandwiching, price impact both
sides, token transfer taxes) is 5-15% round trip. Real rug rates on fresh launches are well
above 20%. Both of those independently put the game underwater.

---

## 7. So is there a business here?

**Not as "buy random shitcoins and let them run." That is negative expectancy after
realistic costs, and it has been since 2022.** The honest summary of why:

1. The mean ticket is below 1.0x, so diversifying converges you onto a loss.
2. The mean is dominated by single outliers, so it cannot be estimated or sized.
3. Friction and rug rates in the real memecoin market sit past the breakeven point.
4. The one era it worked (2020-21) was a regime, and it is over.

**What the data does support, in descending order of confidence:**

- **Exit discipline beats selection.** Every positive-mean configuration came from a wide
  trailing stop, not from picking better coins. If tickets are bought anyway, the rule that
  matters is "let it run, trail it 50-70% off the peak, and actually leave." Buy-and-hold
  and tight take-profits were both strictly worse than that.
- **Be early or do not play.** Entering at a random point rather than at listing cost roughly
  15-20% of the mean. There is no version of this where you buy after the move and win.
- **Size it as consumption, not as a business.** A lottery you cannot estimate the mean of
  cannot carry a return target. If the appeal is the convexity, the defensible form is a
  small fixed slice of net worth, wide trailing stops, and no expectation of contributing
  income.
- **The reliable money is on the other side of this trade.** The previous study found a
  short-biased alt book with a genuine (if fragile) edge, and 83.5% of all listed perps
  finish below their listing price. The lottery buyers' losses are what funds that. Being
  the house — shorting decay, providing liquidity, harvesting funding — is where the
  measurable edge sits.

---

## 8. What would change this verdict

- A new regime like 2020-21. It would show up as the listing-cohort mean pushing back above
  1.0x, which is a live number anyone can track quarterly rather than a thing to predict.
- A genuine *selection* edge — some observable at launch that predicts the tail. I did not
  find one and did not go looking hard; that is the honest gap in this study.
- Materially lower friction (own infrastructure, priority access, no MEV tax) would move the
  breakeven, though not far enough on its own given the rug rates.

## What I did not do

- No holdout was reserved for this study.
- The memecoin sample is n=43 from a single day and is survivorship-biased upward. It is
  supporting evidence, not the basis of the verdict.
- I did not test selection signals at launch (holder concentration, LP lock, deployer
  history, social velocity). If there is a real edge in this space, that is where it would
  be, and this study says nothing about it.
- Binance perp listing prices already reflect a prior move elsewhere, so "buy at listing"
  here is not the same as buying at genesis on a DEX.

## Reproduce

```
altcoin_study/h_lottery.py     # payoff distribution, exit rules, ticket-count bootstrap
altcoin_study/i_tiers.py       # friction and rug sensitivity, breakeven
altcoin_study/j_pit_tiers.py   # liquidity tiers WITHOUT look-ahead, listing cohorts
altcoin_study/k_memecoins.py   # DEX memecoin pools via GeckoTerminal
altcoin_study/l_launch.py      # minute-by-minute memecoin launch lifecycle
```
