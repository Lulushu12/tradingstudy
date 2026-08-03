# ETH / LINK / SOL — Hourly Trade Simulation Study

A trade entered at market on **every hourly candle close** for ETHUSDT, LINKUSDT and
SOLUSDT over the last 10,000 hours, each with a written thesis, a stop loss and a take
profit. Trades stack without limit — every candle's signal is its own independent trade.

**Deliverables:**
- `ETH_LINK_SOL_trading_study.xlsx` (~2 MB) — all analysis, live formulas, opens instantly
- `ETH_LINK_SOL_trade_logs.xlsx` (~8.8 MB) — the six full trade logs, 28,497 rows with written
  theses. Split out because ~600 characters of prose per row makes for a file that is slow to
  open and awkward to scroll. Trade IDs match across both.

---

## Headline result

Read this before anything else, because it points the opposite way from most backtest writeups.

| Book | ETH | LINK | SOL |
|---|---|---|---|
| All trades — avg R | −0.071 | −0.094 | −0.037 |
| All trades — **gross** avg R (pre-cost) | **+0.013** | **−0.031** | **+0.043** |
| Selective (conviction ≥ 6) — avg R | +0.084 | +0.042 | −0.007 |
| Buy & hold over window | −29.6% | −40.7% | −52.0% |

Entering on every hourly close has **no edge to erode**. The gross average R — before a
single fee, slippage tick or funding payment — is within 0.04R of zero on all three
symbols across 28,461 closed trades. Costs (8–10% of one R per trade) don't destroy an
edge here; they make the absence of one visible.

---

## Data

- **Source:** Binance spot 1h klines via `data-api.binance.vision`, the public market-data
  mirror. Identical payload to `api.binance.com`, which returns HTTP 451 (geo-blocked)
  from the build environment.
- **Window:** 2025-06-12 22:00 → 2026-08-03 13:00 UTC.
- **Integrity:** 10,000 contiguous candles per symbol, **zero gaps**, identical windows
  across all three. Verified in `fetch_data.py`.
- **Usable bars:** 9,499 per symbol. The first 500 warm up EMA200, ADX and the 500-bar
  volatility percentile; the final bar has no forward bar to resolve against.

## Strategy

Regime-conditional rather than directionally biased. Each close is classified into one of
five states and traded accordingly:

| Setup | Condition | Stop | Target | Time stop | Share of trades |
|---|---|---|---|---|---|
| `TREND_PULLBACK` | EMAs stacked, ADX ≥ 22, price eased into the 21 EMA, RSI reset, 55 EMA intact | 1.6× ATR | 2.5R | 96h | 5.8% |
| `BREAKOUT` | Stacked EMAs, ADX ≥ 25, close takes prior 48h extreme on volume ≥ +0.4σ | 1.5× ATR | 3.0R | 120h | 2.0% |
| `EXHAUSTION` | >3.2 ATR from 21 EMA, RSI extreme, ADX < 30 | 1.1× ATR | 1.5R | 24h | 0.3% |
| `RANGE_FADE` | ADX < 20, price at Donchian-48 edge | 1.3× ATR | 1.3R | 36h | 1.2% |
| `DEFAULT` | No clean setup — weighted composite decides direction | 1.5× ATR | 1.5R | 48h | **90.4%** |

That last row is the study in one number. The mandate forces a fill on every close, and
90% of closes had nothing worth trading.

### Stop placement

ATR multiple by setup, then pushed **beyond the last confirmed swing pivot** plus a 0.25
ATR buffer, so the stop sits past the obvious liquidity pool rather than on top of it.
Clamped to a 0.6×–2.6× ATR band. Result: 522–605 distinct stop distances per symbol,
0.39% to 9.68%; 27% of trades had their stop relocated by real structure rather than the
ATR formula.

**Pivots carry a confirmation lag.** A swing at bar *p* needs 3 bars either side, so it is
only made visible from bar *p+3* — the first moment it could actually have been known.
This is the single easiest place for a backtest to cheat.

### Target placement — and its known weakness

The target is the stop distance × a per-setup constant, so only **four distinct reward
ratios** exist across all 28,497 trades. The target *price* varies only because the stop
underneath it varies. Unlike the stop, it never asks whether a swing high, range boundary
or prior supply sits in the way.

This was tested rather than defended. A structure-aware target (nearest confirmed swing
level within 240 bars, ~280 distinct ratios) was run on identical entries and stops:

| Method | ETH selective win % | ETH selective avg R |
|---|---|---|
| fixed R | 34.1% | **+0.084** |
| structure | 40.5% | +0.048 |
| structure, extend-only | 34.1% | +0.089 |

Aiming at structure makes you **right more often and richer less often**. The nearest level
is usually closer than the fixed multiple (median 1.5R vs 2.5R), so it clips winners while
every loser still costs a full −1R. Using structure only when it *extends* the target is
marginally best on all three symbols — by ~+0.005R, which is noise. The fixed-R target
stays, on evidence rather than preference.

## Fill assumptions (all chosen to err against the strategy)

- Entry at the signal bar's close, plus slippage and taker fee. Exit scanning starts on the
  **next** bar — a signal bar can never resolve the trade it created.
- **Ambiguous bars resolve as losses.** When one bar's range contains both the stop and the
  target, the stop is assumed to have hit first. Hourly bars hide the path, and assuming
  the favourable order is the commonest way a backtest lies.
- Bars that gap beyond a level fill at the open, not the level.
- Costs: 0.045% taker per side, 0.02% slippage per side, 0.01%/8h funding charged as a drag
  on **both** directions (real funding alternates sign; charging it either way is
  conservative).
- 36 trades still open at the data end are marked `OPEN` and excluded from all statistics.
  They are never counted as wins.

## The eight findings

1. **Entering on every close has no edge at all** — not a small edge destroyed by fees.
   Gross avg R is +0.013 / −0.031 / +0.043. That's a coin flip.
2. **The filter carries everything, and it's thin.** Conviction ≥ 6 keeps ~8% of bars and
   is worth ~0.15R per trade. Small enough that a worse fee tier erases it.
3. **The conviction score is miscalibrated at the top end.** Buckets 6–8 are the sweet spot;
   8–10 is worse, and negative on ETH and SOL. The setups that look most obvious are the
   ones most likely to be late.
4. **Almost nothing survives the time split.** Most setup × direction combinations flip sign
   between sample halves. Only `TREND_PULLBACK/SHORT` is positive in 5 of 6 half-samples.
5. **The short bias is the market falling, not an edge.** Every symbol fell 30–52%. The
   sample contains no sustained bull phase, so no directional conclusion here transfers.
6. **The MAE statistic is a trap.** Winners' median MAE is 0.37–0.41R and ~63% never go
   beyond 0.5R against — which looks like an argument for tighter stops. It isn't. Every
   0.70× stop configuration is negative on all three symbols. MAE only measures trades the
   stop didn't kill, so it cannot tell you what a tighter stop would have destroyed.
7. **The real exit is the clock, not the target.** At the sweep optimum only 5–8% of trades
   reach the target while 40–44% exit on the time stop averaging +3.5% to +5.2%. Wide stops
   don't find better targets — they keep the trade alive long enough for the clock to close
   it in profit.
8. **Aiming at structure makes you right more often and richer less often** (see above).

## Out of sample — the test that decides everything

The system was re-run on the **strictly disjoint** 10,000 hours *before* the main window
(2024-04-22 → 2025-06-12), which no part of the derivation ever saw.

| Configuration | MAIN 1h (in-sample) | **PRIOR 1h (out-of-sample)** | 15m |
|---|---|---|---|
| v1 selective (≥6) | +0.040 | **−0.022** | −0.208 |
| drop RANGE_FADE only | +0.045 | **−0.019** | −0.204 |
| v1 6–8 band | +0.177 | **−0.049** | −0.194 |
| v2 (6–8 + no RANGE_FADE) | +0.196 | **−0.045** | −0.185 |
| v2b (+ ×1.6 / 4R) | +0.269 | **−0.178** | −0.069 |

**Nothing is profitable out of sample**, and the ordering is the damning part: the more
heavily a book was tuned on the main window, the *worse* it does outside it. v2b — the best
in-sample book — is the worst out of sample. That is overfitting, measured rather than
suspected.

### Which cuts replicate

| Removed trades | MAIN | **PRIOR** | 15m |
|---|---|---|---|
| conviction 8–10 | −0.124 | **+0.015** | −0.225 |
| RANGE_FADE | −0.092 | **−0.126** | −0.303 |

**Capping conviction at 8 does not replicate.** +0.015 R out of sample against −0.124 in
sample: a within-window artifact. This workbook previously described it as supported. It is
not, and the System v2 tab now says so rather than quietly dropping the claim.

**Deleting `RANGE_FADE` does replicate** — negative in all three datasets. More convincing
than the outcome is the mechanism:

| Dataset | n | Win rate | Breakeven needed | Gap |
|---|---|---|---|---|
| MAIN 1h | 80 | 45.0% | 49.1% | **−4.1** |
| PRIOR 1h | 69 | 42.0% | 47.5% | **−5.4** |
| 15m | 86 | 40.7% | 54.0% | **−13.3** |

Its breakeven win rate exceeds its achieved win rate in every dataset. That's arithmetic,
not a backtest result — which is precisely why it travelled when nothing else did.

### What this means

This system has **no demonstrated edge** on ETH, LINK or SOL, on hourly or 15m candles,
across 20,000 hours of data. One component is provably incapable of paying for itself and
should be deleted. Everything else that looked promising was the sample talking.

The methodological lesson: every improvement made across this study raised the in-sample
point estimate **without narrowing the confidence interval**, and the bootstrap flagged it
each time. The out-of-sample test then confirmed exactly what the bootstrap had been
warning about. The warning was actionable before the extra data arrived.

## System v2 — as originally derived (half of it since falsified)

Both are **subtractive**. Nothing here adds a new edge. Read the out-of-sample section
above first: change 1 did not replicate, and the v2/v2b books are negative outside their
derivation window. This section is kept intact so the falsified claim stays visible.

1. **Cap conviction at 8**, don't just floor it at 6. The 6–8 bucket is positive on all
   three symbols; 8–10 is negative on all three (−0.124 R, PF 0.84).
2. **Delete `RANGE_FADE`.** Both directions need a higher win rate than they achieve
   (48.6% needed vs 43.8% got, long; 49.5% vs 45.8%, short). A 1.3R target cannot pay for
   the losses at any hit rate those setups reach. No other combination has this property.

Optional **v2b** geometry: stop ×1.6, 4R target — the sweep's average-R optimum. Kept
separate because it's a tuning choice fitted on this sample; the cuts are structural.

| Book (hourly, pooled) | n | Win % | BE % | Avg R | PF | 95% CI | P(>0) |
|---|---|---|---|---|---|---|---|
| v1 selective (≥6) | 2,229 | 33.2 | 32.0 | +0.040 | 1.06 | [−0.191, +0.285] | 62.8% |
| v1 6–8 band | 1,217 | 38.0 | 32.6 | +0.177 | 1.26 | [−0.113, +0.491] | 85.7% |
| v2 (no RANGE_FADE) | 1,137 | 37.5 | 31.7 | +0.196 | 1.29 | [−0.124, +0.524] | 87.8% |
| **v2b (+ ×1.6 / 4R)** | 1,137 | 41.7 | 32.8 | **+0.269** | 1.47 | [−0.118, +0.732] | 89.5% |

v2b is better on every dimension measured — and positive in **both** sample halves (+0.142
and +0.379) and on all three symbols. It still does not clear the significance bar.

### The asymmetry that matters most

On 15m data — a different timeframe, mostly different bars — the two things that were **cut**
are *significantly negative*:

| Dropped | Avg R | 95% CI | P(>0) |
|---|---|---|---|
| conviction 8–10 | −0.225 | **[−0.439, −0.035]** | 0.8% |
| RANGE_FADE in 6–8 | −0.303 | **[−0.609, −0.068]** | 0.4% |

Both intervals exclude zero. The thing that was **kept** is not significantly positive
anywhere. Every improvement in this study raised the point estimate without narrowing the
interval, because overlapping trades carry far less information than their count suggests.

**Superseded by the out-of-sample test above.** Of these two changes, only the `RANGE_FADE`
deletion replicated; the conviction cap did not, and v2b — which looked strongest here — is
the worst performer outside this window.

## System v3 — the live configuration

**`RANGE_FADE` is deleted** from the classifier outright (`ENABLE_RANGE_FADE = False`), not
filtered downstream. It is the one change that replicated out of sample. The trade logs in
the workbook are regenerated with the flag forced back **on**, because those logs are the
evidence for the deletion and erasing them would erase the case for it.

Deleting it was not enough. With market entries the out-of-sample book is still −0.013 R.

**Limit entries** are the second change. A pullback or a fade is a bet that price comes
*back* to you, so paying the close is paying up for something the thesis says will be
cheaper shortly. A breakout is the opposite bet. So `TREND_PULLBACK`, `EXHAUSTION` and
`DEFAULT` rest a limit 0.25 ATR better than the close for 6 bars; `BREAKOUT` still crosses
the spread. Parameters were fixed *before* looking at any limit result.

It matters twice: a resting order is a maker order — no slippage, roughly half the fee — and
exits are now costed by how they actually happen. Cost falls from 6.6% of one R to 4.9%.

| Configuration | PRIOR (out-of-sample) | MAIN |
|---|---|---|
| v3 market, conv ≥ 6 | −0.013 | +0.051 |
| **v3 LIMIT, conv ≥ 6** | **+0.010** | **+0.101** |
| v3 LIMIT, conv 6–8 | −0.037 | +0.222 |

Fill rate is ~89%. Note the 6–8 band is *worse* out of sample — the conviction cap stays
falsified.

### The paired test

Comparing two independent averages wastes the information. Running both entry methods over
the **identical** signal list, with unfilled limits scoring zero:

| | Estimate | 95% CI | P(>0) |
|---|---|---|---|
| Does limit beat market? | **+0.030 R** | [−0.008, +0.065] | **93.8%** |
| Is the limit book profitable? | +0.048 R | [−0.092, +0.192] | 74.7% |

Over 20,000 hours and 4,421 signals. The improvement is the strongest result in this study
and *still* misses 95% — but it is the only one with a **mechanical** explanation rather
than a statistical one: maker fees instead of taker, no slippage, better fill price. Every
one of the 12 parameter-grid cells is positive on both windows, so it doesn't depend on the
tuning.

Restricting limits to pullbacks — the a-priori design choice — beat limit-everything out of
sample (+0.022 vs +0.016) even though limit-everything looked better in-sample. The
reasoning held where the fitting didn't.

**Better execution lifted this system to roughly breakeven. It did not find an edge, because
there wasn't one in the entry logic to begin with.**

## Hypothesis H1 — pre-registered, then falsified

See `PREREGISTRATION.md`, committed to git in a separate earlier commit containing no
results.

**The idea:** every setup tested up to this point came from one trend/regime classifier
whose *gross* edge was ~zero. A new hypothesis had to come from a different source. Leveraged
perps produce **forced liquidations** — margin engines emitting market orders regardless of
price into thin books. That spike is arithmetic, not informed repricing, so it should
partially revert. Concretely: fade an hourly bar whose wick is ≥1.0 ATR, is ≥50% of the
bar's range, closes back in the recovering half, on volume ≥1σ.

**Result — NOT SUPPORTED.**

| Dataset | n | Win % | BE % | Gross R | Avg R | 95% CI |
|---|---|---|---|---|---|---|
| **PRIOR (primary)** | 393 | 35.4 | 38.6 | −0.024 | **−0.089** | [−0.284, +0.097] |
| MAIN | 362 | 30.9 | 39.8 | −0.160 | **−0.238** | [−0.366, −0.113] |
| 15m | 387 | 34.4 | 41.5 | +0.008 | **−0.202** | [−0.391, −0.014] |

A real negative result, not an underpowered one — 393 trades clears the pre-registered floor
of 100 comfortably. Worse than merely unsupported: on **both** replication datasets the CI
excludes zero **on the losing side**. Per-symbol signs are inconsistent on the primary window
(ETH −0.063, LINK +0.037, SOL −0.232), so it fails the weaker SUGGESTIVE criterion too.

**The mechanism was wrong, not the execution.** Gross R — before any fee — is −0.024 on PRIOR
and −0.160 on MAIN. Fading an absorbed wick is simply the wrong side of the trade.

That invites testing the **inverse**. It was not run and is not reported, because the
pre-registration forbids presenting a flipped variant as though it were the registered one.
It also isn't inferable from these numbers: reversing direction changes which bars hit the
stop before the target, and the geometry isn't symmetric. It needs its own pre-registration.

## Hypothesis H2 — the inverse, also falsified

See `PREREGISTRATION_H2.md`, committed before the test. H2 trades the **identical** bars
(the identification function is imported from H1, not reimplemented) and inverts only the
direction, moving the stop to the opposite extreme of the signal bar. Because it was chosen
*because* H1 failed, on the same window, it had to clear a **97.5%** interval, not 95%.

| Dataset | n | Win % | BE % | Stop dist | Cost as % of 1R | Gross R | Avg R | 97.5% CI |
|---|---|---|---|---|---|---|---|---|
| **PRIOR (primary)** | 393 | 38.2 | 37.5 | 1.26% | 12.1% | **+0.141** | **+0.019** | [−0.175, +0.213] |
| MAIN | 363 | 35.8 | 38.5 | 1.11% | 14.2% | +0.062 | −0.080 | [−0.292, +0.127] |
| 15m | 387 | 26.9 | 46.8 | 0.37% | **42.0%** | −0.198 | −0.618 | [−0.840, −0.380] |

**NOT SUPPORTED** — indistinguishable from zero on the primary window, inconsistent across
symbols, and negative on both replications.

### But the gross column is the finding

The inversion **flipped the gross signal**. On identical bars, H1's gross R was −0.024 (PRIOR)
and −0.160 (MAIN); H2's is **+0.141** and **+0.062**. The information in this bar shape really
does run in the continuation direction — H1 was on the wrong side, exactly as H2's mechanism
predicted.

It's still not tradeable, and the reason is **geometry, not direction**. H2's structural stop
sits just beyond the opposite extreme of a bar that closed near it, giving stops of 1.1–1.3%
on hourly and 0.37% on 15m. Friction then eats 12–14% of one R on hourly and 42% on 15m. A
gross +0.141 R becomes a net +0.019 R.

**Joint conclusion:** this bar shape carries a small amount of real directional information,
worth less than the cost of the stop its own structure dictates. Not tradeable either way in
these assets.

The obvious next move — keep the direction, widen the stop — is forbidden by the
pre-registration and would be a **third** look at the same 393 bars. At that point the
multiple-comparison problem isn't something a Bonferroni factor patches over. That line needs
different data: other assets, or an earlier window neither hypothesis has touched.

## Hypothesis H3 — the one that didn't fail

See `PREREGISTRATION_H3.md`, committed with the dataset before the test. H3 keeps H2's
continuation direction and replaces its structural stop with one **derived from the cost
model** (0.155% friction ÷ 6% of R ÷ 1.018% median ATR = 2.54 → registered at **2.5 ATR**),
using only already-burned windows. Time stop 48 → 96 bars as a coupled consequence.

Primary test: the **EARLY** window — fresh, and the study's first sustained bull market.

| Dataset | n | Win % | BE % | Stop | Cost/1R | Gross R | Avg R | PF | 95% CI | P(>0) |
|---|---|---|---|---|---|---|---|---|---|---|
| **EARLY (primary)** | 467 | 39.8 | 38.0 | 2.96% | **6.7%** | +0.117 | **+0.050** | 1.08 | [−0.128, +0.231] | 70.0% |
| PRIOR (context) | 393 | 41.0 | 36.9 | 3.79% | 4.7% | +0.159 | +0.112 | 1.19 | [−0.088, +0.311] | 86.2% |
| MAIN (context) | 362 | 38.1 | 37.4 | 3.12% | 5.9% | +0.079 | +0.020 | 1.03 | [−0.160, +0.186] | 57.8% |

**Verdict: SUGGESTIVE.** Positive on all three symbols individually (the pre-registered
guard), positive on all three windows — but the 95% CI includes zero.

**The fix worked as designed.** Friction came out at 6.7% of one R against the 6% the stop
was sized for, down from H2's 12–14%. The mechanism that killed H2 was correctly identified
and correctly repaired — the first time in this study that a diagnosis led to a working fix.

8 of 9 symbol×window cells are positive. That is **descriptive, not a test**: PRIOR and MAIN
were used to select the continuation direction, so they can't independently confirm it. Only
EARLY is clean, and it says 70%.

### What would actually resolve it

At the observed effect size, a 95% interval would need ~3.6× less noise — roughly **6,000
trades against the 467 available**, about 13× the data, or ~15 years of hourly bars across
three symbols. That's the binding constraint, and no amount of cleverness on this sample
substitutes for it. Widening to more assets gets there faster than waiting.

**Standing commitment honoured:** H3 was the last variant of this bar shape. No H4 was run,
and none will be. The idea is now either forward-tested or dropped.

## H3-Multi — the replication that settled it

25 assets never touched by this study, all three windows, **10,486 trades**. Zero parameters
changed (all imported from `hypothesis_h3.py`). Bootstrap resamples calendar-week blocks
across the whole universe — 172 independent blocks, not 10,486 independent trades.

**Verdict: NOT SUPPORTED.**

| | Value |
|---|---|
| Pooled mean | **+0.0070 R** |
| 95% cross-sectional CI | **[−0.0546, +0.0681]** |
| P(>0) | 57.9% |
| Profit factor | 1.011 |
| Assets positive | **12 / 25 (48%)** — binomial p vs coin flip = 1.00 |

| Window | n | Mean R | P(>0) |
|---|---|---|---|
| EARLY | 4,052 | **−0.060** | 10.0% |
| PRIOR | 3,329 | +0.089 | 93.5% |
| MAIN | 3,105 | +0.006 | 54.1% |

**The most damning number is EARLY.** That was H3's clean primary test, +0.050 R on ETH/LINK/
SOL. Same rule, same window, 25 other assets: **−0.060 R over 4,052 trades.** The sign flips.

**Stated precisely, because overclaiming would be its own error:** this does *not* formally
exclude a +0.050 R effect. Cross-sectional SE is 0.0313, so the smallest separable effect is
+0.061 R and the CI upper bound (+0.068) sits above +0.050. What it *does* show is a point
estimate 86% smaller, per-asset signs indistinguishable from random, and a sign reversal in
the window that motivated the hypothesis. A null result, not a refutation of one number — and
decisive enough that no reasonable person would trade it.

The naive per-trade bootstrap would have said [−0.020, +0.034], P(>0) = 69.6%. Tighter, more
encouraging, and wrong. Registering the cross-sectional bootstrap in advance is what stopped
that becoming the headline.

## What I'd actually do with this

- **Stop trading the always-on mandate.** It's a fee-payment machine over no edge. If you
  want exposure every bar, hold spot — it costs nothing and beat the always-on book on all
  three symbols.
- **Trade the filter, not the schedule.** ~8% of closes carried anything worth acting on.
- **Distrust your best-looking setups.** Size flat across qualifying setups rather than
  scaling with confidence.
- **Fix the exit before the entry.** Exit design moved results far more than any entry
  refinement: the sweep spans −0.11% to +1.07% per trade on *identical* entry signals.
- **Re-run over a rising market** before believing any directional conclusion.

## Important caveat on sample size

28,497 overlapping trades are **not** 28,497 independent observations. Many are the same
move sampled hour after hour. The effective sample is far smaller than the trade count, so
every confidence interval here is much wider than *n* suggests.

## Reproducing

```
python3 fetch_data.py        # 10,000 1h candles per symbol -> data/*.csv
python3 run_backtest.py      # trade logs -> data/*_trades.csv
python3 analyze.py           # breakdowns -> data/analysis.json
python3 robustness.py        # time-split + MAE -> data/robustness.json
python3 sweep.py             # 56-config sensitivity -> data/sweep.json
python3 compare_targets.py   # targeting methods -> data/target_comparison.json
python3 bootstrap_combos.py  # per-combo significance
python3 system_v2.py 1h      # System v2 -> data/system_v2_1h.json
python3 system_v2.py 15m     # same rules on 15m candles
python3 fetch_data.py 1h 2025-06-12T22:00:00Z prior   # disjoint earlier window
python3 system_v2.py 1h_prior                          # out-of-sample run
python3 replication.py       # cross-dataset matrix -> data/replication.json
python3 build_workbook.py    # -> ETH_LINK_SOL_hourly_trading_study.xlsx
```

Deterministic given the same data files.

## Workbook tabs

**Study file:** `Read Me` · `Summary` (live formulas) · `Findings` · `Setup Breakdown` ·
`Stop-Target Sweep` · `Target Method` · `System v2` · `Out of Sample` · `Stability` ·
`Equity Curves` · `Trade Stats`

**Logs file:** `<SYM> All Trades` (9,499 rows each) · `<SYM> Selective` (~720–760 rows each)

### A note on formula verification

LibreOffice cannot load a workbook in the environment that built these files — a 100-cell
test file fails identically, so this is not a size problem. The usual
recalculate-and-verify pass was therefore unavailable. Each formula ships with a cached
value computed in Python, and `verify_summary()` cross-checks all 36 of those against
`analyze.py` — an independent implementation over the same logs — and raises rather than
writing the file if any disagree. Excel recalculates everything live on open.

---

*This is a simulation of one rule set over one window, not a forecast, and not advice.*
