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
```

## Before the first live trade

Four items are still open and are listed at the bottom of `SYSTEM_SPEC_v1.md`:

1. Breakout's exact daily loss limit, drawdown rule and profit target. Every risk number
   in Layer 5 is provisional until this is filled in.
2. Whether Breakout's ATR indicator matches ATR14 with Wilder smoothing. Carried over
   unverified from `FROZEN_SPEC.md`; it affects the S4 stop on every trade.
3. The final watchlist of 8-10 symbols.
4. The actual fee schedule. The 0.08% round trip was assumed and never verified.

## Pre-committed kill rule

After 100 logged trades, if pooled S1+S2+S3 expectancy is <= 0 **and** A-grade does not
beat B-grade by 0.10R **and** clean trades do not beat deviated ones, the discretionary
premise is falsified and the system reverts to trading S4 mechanically. Written before any
results exist so it cannot be renegotiated afterward.
