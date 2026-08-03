# Categorical Trading: what it would take to make it a system

Companion to VIDEO_EXTRACT.md. This file is analysis and proposal. Nothing here has been
backtested. No number below is a result.

---

## 1. The blunt verdict first

There is no system in the video to make profitable. There is a **lens** (classify the tape as
consolidation, direction, or unreadable) and a **risk wrapper** (fixed brackets, one short
session, hard no-trade filters, journaling). The two pieces that turn a lens into a system are
both missing:

- the classifier that assigns the label
- the trigger that fires the entry once the label is assigned

Those are not details. They are the strategy. Everything the video does specify sits *around*
them. So "make this profitable" is really "build the missing 80% and find out whether the 20% he
gave us has any predictive content at all."

That is worth doing. The core claim is falsifiable and cheap to test, and if it is true it is
true generally. But be clear about what we would be testing: our classifier and our trigger, not
his. His results cannot validate our build and our results cannot invalidate his trading.

---

## 2. The cost arithmetic, which the video never once mentions

This is the most important section. A 1:1 bracket on 4 to 5 NQ points is the single most
cost-sensitive configuration a retail trader can construct, and the video spends 41 minutes on it
without saying the word "commission."

Setup. Symmetric bracket of `T` points. Round-trip costs in points:

| Component | Assumption | Points (NQ, $20/pt) | Confidence |
|---|---|---|---|
| Commission round turn | ~$4.20/contract | 0.21 | verify against TradeDay's actual schedule |
| Entry (market order) | 1 tick of spread | 0.25 | conservative-to-fair at 9:33 |
| Exit on winner (limit at target) | no spread paid | 0.00 | but see adverse-selection note below |
| Exit on loser (stop market) | 1 tick + slippage | 0.50 to 1.00 | at the open this is optimistic if anything |

So, approximately:

```
win  = +T - 0.46
loss = -(T + 0.96)
break-even win rate  p* = (T + 0.96) / (2T + 0.50)
```

Run it:

| Target T | Cost as % of R | Break-even win rate |
|---|---|---|
| 4 pts | ~18% | **58.1%** |
| 5 pts | ~14% | **56.8%** |
| 10 pts | ~7% | **53.4%** |
| 20 pts | ~3.5% | **51.8%** |
| 40 pts | ~1.8% | **50.9%** |

**The video's recommended configuration needs roughly a 57% win rate to break even.** The
published sample account win rate is **57.6%**.

That is not an edge. That is a rounding error, and it is inside the error bar of the slippage
assumption. Move stop slippage from 0.5 to 1.0 points and the 5-point configuration's break-even
goes to 57.8% and the account is a net loser.

### 2.1 The contradiction in the published stats

imantrading.org reports average win **$161.93** against average loss **$101.83**. Payoff ratio
**1.59**, not 1.0.

At 57.6% and a 1.59 payoff, expectancy is `0.576 x 161.93 - 0.424 x 101.83 = +$50.09` per trade.
Genuinely good. But that number is produced by the payoff asymmetry, not by the win rate. Strip
the asymmetry back to the 1:1 the video teaches and the same win rate yields roughly zero.

So one of these is true:

1. the brackets are not actually 1:1 in live trading, or
2. winners are managed discretionarily (runners, scaling, manual exits) despite [35:06] saying
   "I do not move profit targets further," or
3. the sample mixes bracket configurations across the six months.

Any of the three means **the taught rules are not the rules that produced the track record.** The
single highest-value thing to test is therefore not his win rate. It is whether the payoff
asymmetry can be produced mechanically.

### 2.2 Adverse selection on the limit exit

Modeling the winner as a free limit fill is generous. A resting limit at the target gets filled
preferentially when price is about to keep going, and gets passed over when it merely kisses the
level. Real fill rates on touched limits at the NQ open are well under 100%. Any backtest that
assumes "high >= target means filled" will overstate the win rate. This needs an explicit
pessimistic fill rule (require a tick or two of penetration beyond the limit) or the whole test
is fiction.

---

## 3. Formalizing the classifier

The thesis is literally one-dimensional: "all price action exists on a spectrum ... somewhere
between consolidation and Direction." That maps cleanly onto a single bounded statistic.

**Primary candidate: Kaufman Efficiency Ratio.**

```
ER_n(t) = |C_t - C_{t-n}| / sum_{i=t-n+1}^{t} |C_i - C_{i-1}|
```

Bounded on [0, 1]. Zero means every tick of movement was retraced (pure consolidation). One means
every tick went the same way (pure direction). This *is* his spectrum, as one number, in one line
of code, with no free parameters other than `n`.

Proposed labels, thresholds to be fit only in-sample and then held fixed:

```
ER < a        -> CONSOLIDATION
ER > b        -> DIRECTION
a <= ER <= b  -> NO TRADE (the "chaotic" bucket)
```

Note the no-trade bucket is the *middle* of the ER range, not a separate dimension. That is a
design decision worth flagging: the video's "chaotic" is described as *rapid label switching*
[18:44], which is a different thing from being mid-scale. So model chaos two ways and compare:

- **static**: ER in the ambiguous middle band
- **dynamic**: the label flipped within the last `k` bars (closer to what he actually describes)

**Horse-race alternatives** (all cheap, all one function each):

| Classifier | Note |
|---|---|
| ADX(14) | the conventional answer, laggier than ER |
| Lo-MacKinlay variance ratio VR(q) | statistically principled; VR<1 mean-reverting, VR>1 trending, and has a known null distribution so you get a significance test for free |
| (High_n - Low_n) / sum(TrueRange_n) | near-identical to ER, uses range instead of close |
| Hurst exponent | theoretically the right object, noisy at small n |

I would run ER as primary and VR as the statistical cross-check, because VR is the only one that
comes with a null hypothesis attached.

---

## 4. The gate that comes before any strategy

**Do not build a trading rule yet.** The whole framework rests on one unverified claim:

> in consolidation price is more likely to stay where it has already been; in direction price is
> more likely to go to a new area

That is a statement about conditional forward distributions, and it can be tested directly with
zero entry logic, zero exits, and zero cost assumptions. This is the correct Gate 0.

**Study design.** For every bar `t`, compute `ER_n(t)` on closed data only. Bucket bars by ER
decile. Within each bucket measure, over horizons of 5, 10, 20, 40 bars forward:

1. `P(touch range midpoint before range extreme)` versus `P(touch new extreme before midpoint)`
2. the first-passage race that the actual strategy would care about: from an entry at the outer
   `q%` of the range, `P(hit +T before -T)`
3. serial correlation of returns, per bucket
4. the same, per bracket size `T`, expressed in ATR units

**Pass condition.** The consolidation deciles must show mean-reversion probability materially
above 50% and the direction deciles must show continuation above 50%, with the gap monotone
across the ER spectrum. Monotonicity matters more than any single bucket, because monotonicity is
what a real underlying mechanism looks like and a lucky bucket is what noise looks like.

**Kill condition.** If the ER label does not separate forward behavior, the framework has no
predictive content and no entry trigger can rescue it. Stop there. This costs a day and it can
save months.

This study can run today on the BTC parquet data already in `study/data/`. BTC is not NQ and the
open is not crypto, so a pass on BTC is evidence of generality rather than proof of his claim, and
a failure on BTC does not kill the NQ-open version. But it is free, the data is loaded, and the
existing engine can drive it.

---

## 5. If the gate passes: the missing entry trigger

The video gives target and stop placement and never gives an entry. Proposed minimal
formalization, deliberately dumb so it can be beaten later:

**Range definition.** Donchian over `n` bars: `R_hi = max(high, n)`, `R_lo = min(low, n)`. Same
`n` as the ER window so there is one lookback parameter, not two.

**Consolidation (mean reversion):**
- Enter long when price trades into the lower `q%` of `[R_lo, R_hi]` and the bar closes back
  inside. Mirror for short.
- Target: range midpoint, or `k x ATR(1)_avg`, whichever the sweep prefers. Start at `k = 0.5`
  per [04:29].
- Stop: `R_lo - buffer`. This is his "stop outside the range."
- Entry at next bar open. Never at the signal bar close.

**Direction (continuation):**
- Enter on a close beyond the `n`-bar extreme.
- Target: `k x ATR` extension into new territory.
- Stop: inside the range, at the midpoint or a fixed ATR fraction.

**Filters, each implemented as a switchable flag and measured as an ablation, never assumed:**

| Filter | Source | Formalization needed |
|---|---|---|
| Session window | [16:25] | 9:33-9:50 ET. Trivial. |
| News blackout | [27:08] | flat by 9:42, or general: flat `m` minutes around any high-impact release |
| No trade at HOD/LOD | [24:03] | within `x` ATR of the session extreme |
| No trade after high-vol candle | [31:53] | true range > `z` percentile of trailing `n`; skip `k` bars |
| No trade at pivots | [31:12] | undefined in source; propose fractal pivot within `x` ATR |
| Direction disabled | [39:44] | consolidation-only mode as a headline variant |

Every one of these filters is a free parameter he fit to himself on a few hundred trades. Treat
each as a hypothesis to be knocked down, not inherited. The prior should be that most of them are
noise-fitting. The ablation table is the deliverable: signal count and expectancy with each filter
on and off, so we can see which ones pay for the trades they cost.

---

## 6. Where the real leverage is

Ranked by expected impact on final expectancy, highest first.

### 6.1 Raise the bracket size

This is the biggest single lever and it is pure arithmetic, not curve fitting. Going from a
5-point target to a 20-point target cuts the required win rate by **five percentage points**
(56.8% to 51.8%) before any change to the signal whatsoever.

The catch, and it is a real one: bigger brackets in ATR terms means a higher timeframe, and the
author is on record that he is "terrible ... on higher time frames" [18:27]. That is a statement
about *him*, not about the market. A mechanical implementation does not inherit his weakness. The
higher-timeframe version of this framework is strictly the more likely one to survive costs, and
it is the version he explicitly abandoned for personal reasons.

**Recommendation: build the higher-timeframe version first.** It has more headroom, more bars of
history, and less dependence on microstructure assumptions we cannot verify.

### 6.2 Break the 1:1 dogma

His own published numbers say the money is in the 1.59 payoff ratio, not the win rate. The video's
argument for 1:1 ("you only need a small edge to flip the coin") is backwards once costs are in:
at 1:1 with a 5-point target you need a *large* edge (7 percentage points over random) just to pay
the toll.

Sweep the payoff ratio across the regime buckets. There is a specific hypothesis worth testing:
**mean-reversion trades in consolidation want a high win rate and a low payoff; continuation
trades in direction want the opposite.** If that holds, the correct system is not 1:1 anywhere,
and a single global R:R is leaving the entire edge on the table.

### 6.3 Fix the timeframe

Changing timeframe intra-session by feel [25:09], [39:23] means the bar series is a free parameter
selected while positioned. This is unbacktestable and is a hidden discretionary input doing
unknown work. Either fix the timeframe, or make the switch rule mechanical (for example: select
the timeframe whose trailing ATR(1) sits closest to a target volatility, evaluated once at session
start and never again). The latter is testable and preserves his stated intent [08:47]. The
former is simpler. Test both, but never leave it discretionary.

### 6.4 Take the conditional-performance idea seriously, with real statistics

The best idea in the video is [16:08]: find the conditions you lose in and stop trading them. That
is exactly a regime-conditional expectancy table and it is the correct instinct.

But the sample-size problem is fatal at his trade frequency and he understates it badly. A
17-minute session with maybe one to three trades gives roughly 250 to 750 trades a year. To
distinguish a 52% win rate from 50% at 95% confidence needs on the order of 2,400 trades. To
distinguish 57% from 55% needs about 2,000. **He cannot resolve his own edge from one year of
data**, and neither can any condition-slice within it, where buckets are 50 trades deep.

He says "one week is not enough" [13:54]. Correct in direction, off by a factor of about fifty in
magnitude. This is not a criticism of his trading. It is the reason a mechanical port matters:
backtesting is the only way to get the sample size the question actually requires.

### 6.5 Treat the track record as censored

$34k of payouts since July 2024 is gross of evaluation fees, gross of failed evals, and gross of
blown accounts. Prop payouts are a right-censored sample by construction: you only ever see the
accounts that survived. This is not an accusation, it is a property of the data source. It means
the track record can support "he is probably not a net loser" and cannot support any specific
expectancy figure.

---

## 7. Proposed sequence

| Phase | Deliverable | Kill condition |
|---|---|---|
| 0 | ER/VR classifier implemented; conditional forward-behavior study on existing BTC data; no trading rules | label does not separate forward behavior monotonically -> framework dead, stop |
| 1 | Minimal entry trigger, both templates, costs from bar one, no filters | expectancy negative net of costs across all bracket sizes -> stop |
| 2 | Filter ablation table; each video filter measured on and off | filters cost more in lost trades than they save -> drop them, do not tune them |
| 3 | Payoff-ratio and bracket-size sweep; find where cost/R stops dominating | no configuration clears costs with headroom -> stop |
| 4 | Walk-forward on held-out span; then NQ or ES data if the BTC version survives | fails out of sample -> stop, and do not retune |

Same discipline as the existing audit in this repo. Thresholds written down before results exist.
In-sample results prove nothing. Surviving means not yet falsified.

---

## 8. What I would bet, stated plainly so it can be held against me

- The ER label **does** separate forward behavior. Regime-conditional autocorrelation is a real
  and repeatedly documented effect across markets. I expect Gate 0 to pass.
- The effect is **too small to pay a 14% cost-per-R toll**. I expect the 5-point 1:1 NQ scalp
  configuration to be a net loser or indistinguishable from zero once realistic stop slippage and
  limit-fill adverse selection are modeled.
- The higher-timeframe, asymmetric-payoff version has a **real chance**, because the same
  statistical effect is paying a cost of 3% of R instead of 14%.
- Most of the discretionary filters will not survive ablation.
- The author is probably a slightly-positive-expectancy discretionary trader whose real edge lives
  in execution judgment he cannot articulate, and who is at 57.6% on a configuration that needs
  57% to break even. The video is honest about being a lens rather than a system. It is the
  viewer, not the author, who is likely to mistake it for one.
