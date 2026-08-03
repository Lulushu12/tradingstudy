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
