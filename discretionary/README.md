# Discretionary trading system

Replaces the mechanical MCB divergence-stack attempt in `../FROZEN_SPEC.md`. Built on top
of the empirical results in `../study/STRATEGY_FINDINGS.md` and the method in
`../JaysonCasper/`.

## Why this exists

The mechanical work did not fail to find an edge. It found two things:

1. A real, out-of-sample-stable edge (4H volume-spike trend continuation, **+0.21R** net
   per trade, positive in every year 2021-2026), which fell far short of the 10%/month at
   6% drawdown target because that target implies a Calmar near 35 and does not exist.
2. Several **higher-quality** conditions (short into held 4H swing resistance in a
   downtrend: 61%/64% at 1:1; short into held prior-week high: 52%/68%) that were rejected
   **for frequency alone**, at 1.5 to 3 trades a month on a single symbol.

A mechanical system needs frequency to compound. A patient human does not, in the same
way. The edge thrown away for being too rare is the edge this system is designed to
harvest, applied across a watchlist rather than one symbol so the trade count works.

On timeframes: the study's rejection of 15m and 1h is stated at **1:1**, where fee drag
puts the breakeven winrate at 54-56%. This system has a hard 2.0R floor, where the same
fee drag puts it at **36-40%**. That is a different bar entirely, so 1D, 4H, 1h and 15m
anchors are all permitted and the question of which ones pay is settled by the
per-anchor rule in Layer 7, on data, rather than by assumption in either direction.

The other thing the mechanical port lost is that it encoded the wrong half of the method.
Jayson's process is level-quality judgment, range re-drawing, SFP reading and multi-
timeframe momentum timing. `FROZEN_SPEC.md` reduced all of it to "WT divergence + MFI
divergence within 11 bars", which was never the point. This system puts the judgment back
in Layers 1 and 2, and keeps everything below that mechanical, because sizing, stops and
"just this once" are where discretion destroys traders.

## The honest risk

Discretionary systems fail silently. There is no backtest, so without a measurement layer
you end up six months from now saying "it did not work" with no data about why. Layer 7
exists specifically to prevent that, and **S4 is in the system as a control group**: a
fully mechanical setup with known expectancy. At every review the question is not "did I
make money" but "did my judgment beat the rule I could have automated". If it did not,
the answer is to trade the rule.

## Files

| File | What it is |
|---|---|
| `SYSTEM_SPEC_v1.md` | The system. Eight layers, mandate through measurement. Read first. |
| `PLAYBOOK.md` | The four setups, desk-usable. Keep open while trading. |
| `PREP_ROUTINE.md` | Weekly and daily prep, the alert-fires checklist, post-trade routine. |
| `JOURNAL_SCHEMA.md` | Field definitions, and how to measure MFE/MAE so exits are testable. |
| `journal_template.csv` | Copy to `journal.csv` and start logging. |
| `skips_template.csv` | Optional log of setups you passed on. |
| `levels.py` | Builds the graded confluence level map from a TradingView CSV. |
| `review.py` | The falsification engine. Run every 40 trades. |
| `prop_math.py` | Monte Carlo of the Breakout evaluation. Sets risk per trade. |

Both scripts are stdlib-only Python 3, no install step. The older `../study/` code needs
pandas via `../study/run.sh`; this folder deliberately does not.

## Quick start

```bash
# 1. Build a level map for a symbol
python3 levels.py "../BINANCE_BTCUSDT.P, 240.csv" --near 12

# 2. Start a journal
cp journal_template.csv journal.csv

# 3. Verify the review engine works before you trust it with real trades
python3 review.py --self-test

# 4. At every 40-trade review
python3 review.py journal.csv

# 5. Re-derive risk per trade if the prop rules turn out different
python3 prop_math.py --target 10 --dd 6 --daily 3
```

## Breakout constraints and sizing

1-Step Classic: **10% profit target, 6% static max drawdown, 3% daily loss** (reset 00:30
UTC, on equity including floating PnL), **0.04% per side / 0.08% round trip**, leverage
5:1 on BTC/ETH and 2:1 on altcoins, no consistency rules or minimum days.

Confirmed by the trader against the live dashboard on 2026-08-06: 6% and 3% are correct.

`prop_math.py` simulates reaching +10% before touching the static floor. At the study's
measured 41.7% winrate, 0.40% risk passes 95.4% of the time in a median of 96 trades. The
finding that changed the design: **winrate uncertainty dominates the sizing decision, not
the drawdown rule.** A four-point winrate drop costs more pass probability than doubling
risk does, which is why frequency is only worth chasing at constant setup quality.

Risk per trade: **0.40% evaluation, 0.30% funded, 1.0% personal.**

## Status

**Live-ready as of 2026-08-06.** All pre-trade items are closed: Breakout rules confirmed
(6% static / 3% daily), ATR matches ATR14, fees confirmed at 0.08% round trip, and the
watchlist is set: BTC, ETH, LINK, AVAX, SOL, SUI, DOGE, XRP perps. The 2:1 altcoin
leverage cap never binds because the 0.40% minimum stop keeps any position's notional at
or below 1x equity.

Next step: Sunday prep per `PREP_ROUTINE.md`, then the first pre-trade row in
`journal.csv`.

## Pre-committed kill rule

After 100 logged trades, if pooled S1+S2+S3 expectancy is <= 0 **and** A-grade does not
beat B-grade by 0.10R **and** clean trades do not beat deviated ones, the discretionary
premise is falsified and the system reverts to trading S4 mechanically. Written before any
results exist so it cannot be renegotiated afterward.
