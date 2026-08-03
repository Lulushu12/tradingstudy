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

## System v2 — the changes the evidence supports

Both are **subtractive**. Nothing here adds a new edge.

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

**This study can tell you what to stop doing with real confidence. It cannot yet tell you
what to start doing.** Cutting the 8–10 bucket and deleting `RANGE_FADE` are supported.
Treating v2b's +0.269 R as an expected return is not.

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
python3 build_workbook.py    # -> ETH_LINK_SOL_hourly_trading_study.xlsx
```

Deterministic given the same data files.

## Workbook tabs

**Study file:** `Read Me` · `Summary` (live formulas) · `Findings` · `Setup Breakdown` ·
`Stop-Target Sweep` · `Target Method` · `System v2` · `Stability` · `Equity Curves` · `Trade Stats`

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
