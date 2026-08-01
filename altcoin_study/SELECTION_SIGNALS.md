# Launch Selection Signals — Findings

The gap left open by `LOTTERY_FINDINGS.md`: is there anything observable at launch that
predicts which shitcoin runs?

**Answer: yes, one signal is real, replicable and counterintuitive — but it predicts the
wrong thing. It tells you which coins bleed less, not which coins 10x. It does not make the
lottery profitable in the current regime.**

---

## Design

Tested on the survivorship-free Binance perp universe (772 launches with a clean window,
dead coins included) because that is where the statistical power is. The DEX firehose is
tested separately below.

Strictly causal:

- **Observation window:** the first 7 days of trading. All signals computed from this only.
- **Forward outcome:** the lottery result measured from the *end* of that window onward,
  using the trailing-70%-off-peak rule that won in `LOTTERY_FINDINGS.md`.
- A signal never sees any part of the return it is predicting.
- **Out-of-sample split:** fit on 2020-2023 (n=263), test on 2024-2026 (n=509).

Because the outcome distribution is dominated by rare outliers, every signal is judged on
rank statistics (Spearman IC, decile medians) *and* on the mean, and separately on whether
it moves the **body** or the **tail**.

---

## 1. What predicts, and in which direction

Full sample, Spearman IC between signal and forward multiple:

| signal | IC | p | top-decile median | bottom-decile median |
|---|---|---|---|---|
| **week-1 daily $ volume** | **-0.389** | 0.000 | 0.39x | 1.02x |
| realised volatility | -0.296 | 0.000 | 0.46x | 1.02x |
| give-back from week-1 peak | +0.253 | 0.000 | 0.99x | 0.42x |
| best gain within week 1 | -0.177 | 0.000 | 0.43x | 0.95x |
| average trade size | -0.132 | 0.000 | 0.56x | 0.80x |
| BTC vs its EMA200 at listing | -0.108 | 0.003 | 0.53x | 0.90x |
| first-week return | +0.119 | 0.001 | 0.50x | 0.44x |
| mean funding rate in week 1 | +0.073 | 0.044 | 0.65x | 0.58x |
| volume trend (2nd half / 1st) | +0.002 | 0.964 | 0.57x | 0.69x |

Every sign is the opposite of intuition. **More volume, more volatility, a bigger first-week
pump, bigger trades — all predict WORSE forward returns.** The launches that look like
they are running are the ones to avoid.

Six of nine kept their sign out of sample. The strongest, week-1 volume, went from
**IC -0.356 in train to -0.415 in test** — it got *stronger* on unseen data.

---

## 2. Is it one signal wearing six hats? Partly

The first principal component explains **46%** of the variance across the six survivors.
Volume, volatility, week-1 peak and give-back are correlated 0.5-0.7 — they are all proxies
for one underlying factor, **hype at launch**. Average trade size and the BTC regime are
close to independent of it.

A 6-signal composite (IC +0.355) did **not** beat week-1 volume alone (IC +0.389). One
signal is the whole finding; the rest is packaging.

---

## 3. Is it just a listing-era proxy? No

The obvious trap: 2020 listings were both quiet *and* lucky, so "quiet" could just mean
"2020". Computing the IC **within each cohort**:

| signal | pooled IC | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | mean within |
|---|---|---|---|---|---|---|---|---|---|
| **week-1 volume (inverted)** | +0.389 | +0.22 | +0.46 | +0.02 | +0.14 | +0.21 | +0.16 | +0.31 | **+0.219** |
| realised volatility (inv) | +0.296 | +0.19 | +0.19 | +0.12 | +0.11 | +0.22 | -0.02 | +0.41 | +0.173 |
| average trade size (inv) | +0.132 | +0.23 | +0.36 | +0.14 | +0.15 | +0.10 | +0.22 | -0.15 | +0.151 |
| give-back from peak | +0.253 | -0.04 | +0.09 | +0.01 | -0.07 | +0.20 | +0.11 | +0.39 | +0.099 |
| BTC regime at listing | +0.108 | +0.12 | +0.07 | -0.11 | +0.09 | +0.26 | +0.07 | +0.10 | +0.086 |
| best gain in week 1 | +0.177 | +0.04 | +0.01 | -0.08 | -0.04 | -0.00 | -0.01 | +0.29 | +0.030 |

About half of the pooled IC is era effect — but **week-1 volume stays positive in all seven
cohorts** with a mean within-cohort IC of +0.22. That is a genuine cross-sectional signal,
not a disguised bet on the 2021 bull. Give-back, week-1 peak and the BTC regime largely
collapse once you control for the era; they were mostly artifacts.

---

## 4. The thing that kills it: body, not tail

Robustness across different definitions of the forward outcome:

| forward outcome | IC (all) | IC (2024+) | quietest-Q5 median | loudest-Q1 median |
|---|---|---|---|---|
| trailing-70% (headline) | +0.389 | +0.415 | 1.03x | 0.45x |
| plain hold to today | +0.404 | +0.515 | 0.90x | **0.10x** |
| hold 90 days | +0.324 | +0.382 | 0.99x | 0.63x |
| **best it ever reached (MFE)** | **+0.012** | **-0.158** | **1.26x** | **1.55x** |

That last row is the whole story. The signal has **no power at all** over how high a coin
gets — and in the modern era the sign actually flips: **loud launches reach HIGHER peaks
(median 1.55x vs 1.26x)**. They simply give it all back (hold-to-today median 0.10x vs
0.90x).

> The quiet-launch signal is a **decay-avoidance** signal, not a tail-finding signal.
> For "don't lose money" it is excellent. For a lottery thesis, which needs the tail, it is
> the wrong instrument.

Confirming this directly — chi-square on whether the count of >5x outcomes differs across
quintiles:

| signal | p | verdict |
|---|---|---|
| week-1 volume | 0.004 | tail effect (full sample) |
| realised volatility | 0.015 | tail effect (full sample) |
| give-back, week-1 peak, trade size, BTC regime | 0.23-0.73 | none |

But that full-sample tail effect is entirely the 2020-21 bull. See below.

---

## 5. The regime split — where it all comes apart

Quintiles of inverted week-1 volume (Q5 = quietest):

**2020-2021 (n=97).** Spectacular. IC +0.456, chi-square p=0.000.

| quintile | median | mean | P(>1x) | P(>5x) |
|---|---|---|---|---|
| Q1 loudest | 0.50x | 1.34x | 32.1% | 3.6% |
| **Q5 quietest** | **3.01x** | **6.02x** | **96.4%** | **35.7%** |

**2022-2023 (n=125).** Nothing. IC +0.115, chi-square p=0.543.

**2024-2026 (n=509).** The ranking still works — IC **+0.415** — but the payoff is gone:

| quintile | median | mean | P(>1x) | P(>2x) | P(>5x) |
|---|---|---|---|---|---|
| Q1 loudest | 0.40x | 0.59x | 11.8% | 2.0% | 0.0% |
| Q3 | 0.53x | 0.75x | 18.8% | 5.9% | 0.0% |
| **Q5 quietest** | **0.96x** | **1.00x** | 44.1% | 3.9% | **0.0%** |

**P(>5x) in the best modern quintile is 0.0%.** The signal sorts correctly and sorts you
into breakeven.

---

## 6. Would the basket make money?

Buying the quietest 20% of each year's listings:

| | n | mean | median | bootstrap 95% CI on mean | P(mean <= 1) |
|---|---|---|---|---|---|
| all years | 158 | 1.75x | 0.90x | [1.21x, 2.54x] | **0.000** |
| **2024+ only** | 104 | **0.96x** | 0.73x | [0.76x, 1.23x] | **0.674** |
| 2024+, after 5% round trip | 104 | 0.91x | — | — | 0.795 |
| 2024+, after 10% round trip | 104 | 0.86x | — | — | 0.889 |

And the effect lives where you can least afford to trade it. Excluding the thinnest launches
decays it monotonically:

| minimum week-1 volume | n | IC | IC (2024+) |
|---|---|---|---|
| none | 772 | +0.389 | +0.415 |
| $5M/day | 668 | +0.260 | +0.259 |
| $10M/day | 620 | +0.236 | +0.218 |
| $20M/day | 532 | +0.129 | +0.153 |

---

## 7. Statistical power — how much can this sample even say?

Of 772 launches, only **23 (3.0%)** returned >5x after the observation window. A top-decile
selector holds ~77 names and would contain ~2.3 such coins by chance.

| selector quality | expected winners in top decile | p vs chance |
|---|---|---|
| 2x better than chance | 4.6 | 0.084 |
| 3x better than chance | 6.9 | 0.009 |
| 5x better than chance | 11.5 | 0.000 |

So this sample can only detect a **large** tail edge. A subtle one is invisible. Absence of
evidence here is weak evidence of absence, and that caveat applies to everything in section 4.

---

## 8. The obvious follow-up: short the loud ones. It does not work.

If loud launches held to today have a median outcome of 0.10x, the actionable trade looks
like shorting them rather than buying quiet ones. Tested properly — entry at the day-7
close, 2x ATR stop, 2R target, real funding, pessimistic same-bar fills, loudness ranked
within each cohort:

| bucket (week-1 volume) | n | E net R | win rate | t-stat | train | test |
|---|---|---|---|---|---|---|
| Q1 quietest | 152 | +0.185 | 43.4% | 1.47 | -0.030 | +0.293 |
| Q3 | 154 | +0.089 | 40.3% | 0.71 | +0.165 | +0.050 |
| Q4 | 154 | -0.120 | 35.7% | -0.95 | -0.208 | -0.074 |
| **Q5 loudest** | 158 | **+0.139** | 43.0% | **1.12** | +0.288 | +0.061 |

**Shorting the loudest launches is no better than shorting the quietest ones** (+0.139R vs
+0.185R). The loudness ranking, which sorts buy-and-hold outcomes so cleanly, carries no
information in the short trade. What remains is just the generic "shorting new listings
works a little" effect already documented in `SHITCOIN_FINDINGS.md`, at t=1.12.

Monthly block bootstrap on the loud bucket: E=+0.139R, 95% CI **[-0.133, +0.413]**,
P(E<=0)=0.161. Not established. Only ~26 trades a year.

Parameter sensitivity improves monotonically with wider stops (3x ATR / 3R reaches +0.271R,
t=2.21) — but that is the best of nine cells tried, uncorrected, and a monotone gradient
toward the edge of the grid is a warning sign, not a result.

**Why the contradiction is only apparent:** the -90% decay of a hyped launch is real but
*slow and violent*. A stop-based short gets squeezed out long before the decay pays. The
decay is visible in a buy-and-hold statistic and not harvestable with a stop.

---

## 9. The DEX arm: what I could and could not measure

I stood at the launch firehose and recorded **599 new pools live at creation** across
Solana, Base, Ethereum and BSC over 6.2 hours — winners and failures alike, which is the
sample the ranked GeckoTerminal endpoints cannot give you. Launch-time attributes were
captured at first sighting so any test would be strictly causal.

**The signal test was not feasible, and the reason is the finding.** Of 599 launches, only
247 traded enough to be worth requesting price history for, and of those only a handful had
any indexed minute OHLCV at all — the retrieved paths topped out at ~31 minutes of bars.
GeckoTerminal does not index a price series for pools that barely trade, because there is
barely a price. I am reporting this as a failed measurement rather than dressing up an
n=6 result.

What the cohort itself shows is more useful than the signal test would have been:

| | |
|---|---|
| median initial liquidity | **$1,327** |
| median FDV at launch | $2,283 |
| **median volume in the first hour** | **$3** |
| median unique buyers in the first hour | **1** |

| threshold | share of launches |
|---|---|
| any volume at all in hour 1 | 67.6% |
| > $1,000 volume in hour 1 | 24.5% |
| > $5,000 volume in hour 1 | 10.2% |
| > $50,000 volume in hour 1 | **1.3%** |
| initial liquidity > $100,000 | **4.5%** |

Median buys per unique buyer in hour one: **1.00**. The typical launch is one wallet making
one trade.

This reframes the selection question rather than answering it:

> For roughly 90% of launches **there is nothing to select.** They never acquire enough
> liquidity to take a position in, and never generate enough trades to have a price. The
> real universe is the ~1-10% that get any traction — and by the time traction is visible,
> you are no longer buying a launch, you are buying after the move. Stage H measured that
> directly: entering at a random later point instead of at listing cost 15-20% of the mean.

So the DEX end is squeezed from both sides. Before traction there is nothing tradeable;
after traction the entry edge is gone.

---

## 10. What this means

1. **A real, replicable selection signal exists, and it is the opposite of how people pick.**
   Quiet launches beat loud ones — consistently, within every cohort, and more strongly out
   of sample than in. If you are going to buy launches at all, buy the ones nobody is
   talking about.
2. **It does not find the tail.** It has zero power over how high a coin goes, and negative
   power in the modern era. It only predicts how much of the move a coin keeps.
3. **It does not rescue the lottery.** The best modern basket is mean 0.96x with a 67%
   chance the true mean is at or below breakeven — 89% after realistic costs.
4. **The tradeable version is the weakest version.** Impose a liquidity floor you can
   actually execute against and the IC roughly halves.

5. **The short version of the signal does not work either** (section 8), and on the DEX end
   there is nothing to select from in the first place (section 9).

Combined with `LOTTERY_FINDINGS.md`: the lottery is not fixable by better selection. The
best available selection signal turns a 0.6x median into a 1.0x median. That is a real
improvement and still not a business.

The honest use of this finding is **defensive** — as a filter for what *not* to buy. On the
loud end, Q1 launches held to today have a median outcome of **0.10x**. Avoiding those is
worth more than anything the signal does on the quiet end.

## What I did not do

- No holdout beyond the 2024+ split, which I have now seen.
- Signals are limited to price/volume/funding observables. On-chain launch data that would
  actually test the original hypotheses — holder concentration, LP lock status, deployer
  wallet history, social velocity — needs paid or indexed sources not available here. I
  captured unique-buyer counts as a concentration proxy on the DEX cohort but could not
  pair them with forward returns (section 9), so those hypotheses remain untested.
- The DEX signal test failed for data reasons, not because a signal was ruled out. Testing
  it properly needs an archive node or a paid indexer, not a public rate-limited API.
- The short-the-hype grid in section 8 tried nine parameter cells with no multiple-testing
  correction; I am reading it as "not established", not as "the best cell is real".
- Binance perp listings already reflect a prior move elsewhere, so "week 1" here is not the
  same as a DEX genesis window.

## Reproduce

```
altcoin_study/n_selection.py    # causal signal test, OOS split, power analysis
altcoin_study/o_signal_audit.py # collinearity, era-proxy test, body-vs-tail
altcoin_study/p_modern.py       # regime split, within-cohort ranking, basket economics
altcoin_study/m_snapshot.py     # live DEX launch-cohort collector
altcoin_study/r_short_hype.py   # is shorting the loud launches tradeable?
altcoin_study/q_dex_signals.py  # same causal test on the DEX firehose (see section 9)
```
