# Results: four TheSecretMindset strategies on BTCUSDT.P

Run per `FROZEN_SPEC_TSM.md`, no parameter tuned after the fact. Full console output in
`results/full_run.txt`, per-trade logs in `results/trades_*.csv`.

Studied span: 2019-09-08 to 2024-12-31 daily (1942 bars), 2021-01-01 to 2024-12-31 4h (8766 bars).
Holdout from 2025-01-01 was never loaded. Costs 0.05% per side, 0.10% round trip.

## Verdict

**Nothing here is a demonstrated edge.** One run clears every pre-committed bar, and it clears
the last one by a margin small enough that it should not be treated as a finding.

The single most important number in this file is the control:

| | Return | Max drawdown |
|---|---|---|
| **Buy and hold BTCUSDT, same span, same cost** | **+799.33%** | **-76.67%** |

Any long-biased strategy run on BTC across 2019-2024 starts with a large tailwind. Returns
have to be read against that line, not against zero.

## Table

| run | trades | mean R | 95% CI | Bonferroni CI | PF | return | max DD | time in mkt |
|---|---|---|---|---|---|---|---|---|
| s1_flat | 64 | +0.046 | +0.009 to +0.087 | **includes 0** | 1.90 | +791.6% | -51.4% | 47.0% |
| s1_flip | 129 | +0.017 | includes 0 | includes 0 | 1.16 | +171.5% | -58.9% | 91.6% |
| s1_flat_4h | 343 | +0.001 | includes 0 | includes 0 | 0.98 | -16.8% | -74.1% | 46.3% |
| s1_flip_4h | 686 | -0.001 | includes 0 | includes 0 | 0.79 | -85.4% | -91.0% | 92.4% |
| s2_mid | 54 | +0.980 | +0.142 to +2.175 | +0.014 to +2.550 | 3.33 | +62.6% | -12.3% | 65.4% |
| s2_band | 187 | +0.165 | +0.033 to +0.295 | **includes 0** | 1.48 | +33.4% | -5.8% | 52.4% |
| s3_atr | 40 | +2.085 | **includes 0** | includes 0 | 7.85 | +100.9% | -12.6% | 44.8% |
| s3_nostop | 40 | +0.119 | +0.001 to +0.296 | **includes 0** | 3.80 | +1180.5% | -38.1% | 51.6% |
| s4 | 4 | +0.134 | too few to bootstrap | | 1.25 | +0.5% | -4.0% | 0.3% |

Bootstrap is 10,000 resamples of the trade list. The Bonferroni column is the 98.75% interval,
the correct threshold for having tested four independent strategy families. Reading the 95%
column alone would have produced four "significant" results out of nine runs, which is roughly
what testing nine things and keeping the winners always produces.

Confidence intervals only describe sampling noise in this one sample. They say nothing about
whether the next five years look like the last five.

## What each strategy actually did

**S1 MACD crossover.** On daily, long/flat returned +791.6% against buy-and-hold's +799.3%.
It did not beat holding. It roughly matched it while in the market only 47% of the time and
with a drawdown 25 points shallower. That is a real risk property and it is not the same claim
as "the MACD crossover makes money". Mean R per trade loses significance under correction.
On 4h both variants are dead, and the cost sweep shows long/flat 4h crosses into negative
expectancy somewhere below 0.05% per side, so it never had headroom to begin with.
Shorting BTC on the reverse cross was badly punished in both timeframes.

**S2 Donchian breakout.** The only family where anything survives correction, and only the
midpoint-exit variant. Its per-year record is the problem: of about 52.8R total, 27.0R came
from 2021 alone. The opposite-band variant trades 3x more often, is positive in every full
year, and has the shallowest drawdown of any run at -5.8%, but its mean R is small enough
that correction wipes out its significance.

Note the exit choice was mine. The video offers two exits and mandates neither. The two
readings differ by a factor of about six in mean R, which is a fair measure of how much of
this result belongs to me rather than to the channel.

**S3 MFI(50) with 200 EMA filter.** The gaudiest numbers here and the emptiest. Profit factor
7.85 comes from 40 trades where the average win is nearly nine times the average loss, and
the 95% interval on mean R already includes zero before any correction. The per-year table
explains it: 52.9R in 2021 and 29.7R in 2024 out of 83.5R total. Two years, a handful of
trend trades. The no-stop variant's +1180% does beat buy-and-hold on both return and
drawdown, on 40 trades, with a corrected interval that includes zero.

The speaker's own words on this one, quoted from the transcript at 09:30, are that a 50-level
crossover system "traded by itself is not reliable in the long run". The data does not
contradict him.

**S4 Daily outside bar.** Produced 4 signals in 1942 daily bars and 4 completed trades.
(Corrected: this originally read "2 completed trades, both losers", which was an engine bug
that discarded any trade scaling out at 1R. See BASKET_RESULTS.md.) Undecidable, and not because the invented parameters were too strict. The filter
census shows 87 outside bars in total, 118 bars that pass both the trend and zone gates, and
4 where all three coincide. This setup is meant to be run as a scan across dozens of
instruments, which is exactly how the video presents it. One symbol cannot generate a
testable sample, and no amount of loosening my slope threshold would change that by an order
of magnitude. Testing it properly needs a basket, not a longer history.

## Guards that were actually implemented

- Look-ahead self-test: every indicator is recomputed on a truncated frame and its last value
  must match the untruncated value. Run before results are reported; a failure aborts the run.
- Causality self-test: no exit index precedes its entry, no fill price falls outside its bar.
- Fills at the next bar's open, except S4 where the author explicitly specifies the signal
  bar's close.
- When a bar contains both the stop and a profit level, the stop fills first. Always.
- Trailing levels update only on confirmed closes and only ever tighten.
- Costs charged on every fill including partial exits.
- Donchian channels exclude the current bar.
- Fractal pivots are published only after their confirmation bar.

## Bugs found and fixed during the run

The first pass implemented S2's "exit on a touch of the 50-channel midpoint" as a profit
target. For a long breakout the midpoint sits below the entry, so the rule is a give-back
exit, not a target. As written it produced a profit factor of 0.17 and a DEAD verdict. Fixed
to a trailing level, the same run scores 3.33 and survives. The verdict on this strategy was
entirely an artefact of my error, in the direction of a false kill. Recorded because a bug
that flips a verdict once can flip one again in the other direction.

## What would have to happen next for any of this to mean something

1. A basket, not one symbol. Every result here is one instrument over one span containing a
   single enormous bull market. S4 cannot be tested at all without this.
2. The holdout, run once, on whichever candidate is chosen in advance rather than after
   reading this file.
3. Sensitivity to my invented parameters. If S2's result moves by 6x between two exits the
   video treats as interchangeable, the other invented values deserve the same check.

All three were subsequently done except the holdout. See **BASKET_RESULTS.md** for the
87-symbol basket run, which is the result that supersedes this file: across the basket,
nothing survives once outliers are capped.

Nothing in this file has been validated out of sample.
