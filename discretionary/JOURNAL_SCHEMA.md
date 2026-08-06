# Journal schema

One row per trade. `journal.csv` is the live file; `journal_template.csv` is the empty
header you copy once. `review.py` reads `journal.csv`.

The split matters: **pre-trade fields are typed before the entry order goes in**,
post-trade fields after the exit. `review.py` flags any row where a pre-trade field is
missing and counts it as a process failure, because a plan written after the fact is not a
plan.

## Pre-trade fields (write these BEFORE entering)

| Field | Type | Values / notes |
|---|---|---|
| `trade_id` | int | Sequential, never reused |
| `date_utc` | ISO8601 | `2026-08-06T14:15:00Z`, the trigger bar close |
| `symbol` | string | e.g. `BTCUSDT.P` |
| `setup` | enum | `S1` `S2` `S3` `S4` |
| `direction` | enum | `long` `short` |
| `grade` | enum | `A` `B` `C`. C only ever appears on a deviated row |
| `confluence` | string | Pipe-separated families that agreed, e.g. `htf\|fib\|vp`. Allowed: `htf` `fib` `vp` `period` `ma`. For S4 write `n/a` |
| `htf_trend` | enum | `with` `against`, relative to 4H EMA200 |
| `anchor_tf` | enum | `1D` `4H` `1h` `15m`. The timeframe the LEVEL was drawn on, not the trigger |
| `trigger_tf` | string | Fixed by the anchor per Layer 4: 1D->1h, 4H->15m, 1h->5m, 15m->5m (1m for S2). S4 is always `4H` |
| `planned_entry` | float | |
| `planned_stop` | float | |
| `planned_target` | float | Next opposing level, or the 2R level for S4 |
| `planned_rr` | float | `abs(target-entry) / abs(entry-stop)`. Must be >= 2.0 except S4 |
| `risk_pct` | float | Account % risked, after the grade multiplier. e.g. `0.5` for 0.5% |

## Post-trade fields (write these after the exit)

| Field | Type | Values / notes |
|---|---|---|
| `actual_entry` | float | Real fill, including slippage |
| `actual_exit` | float | Final fill. For a partialled trade, the blended average |
| `exit_reason` | enum | `target` `stop` `breakeven` `partial_then_target` `partial_then_be` `manual` `time` |
| `r_realized` | float | Net R after fees. Losses negative. This is the number that counts |
| `mfe_r` | float | **Max favourable excursion in R.** See the measurement window below. Always >= 0 |
| `mae_r` | float | **Max adverse excursion in R.** How far against you, positive number. A trade that touched the original stop has `mae_r >= 1.0` |
| `exit_policy` | enum | The policy you actually traded: `full_2R` `partial_be` `partial_be_early` `manual` |
| `adherence` | enum | `clean` or `deviated` |
| `deviation_reason` | string | Required if `deviated`. Be specific: `entered intrabar`, `chased after level broke`, `moved stop`, `C grade`, `oversized`, `traded after 2 daily losses` |
| `notes` | string | Free text. What you saw, what you would do again |
| `chart` | string | Path or link to a screenshot at entry. Optional but strongly recommended |

## Why MFE_R and MAE_R carry so much weight

They are what lets `review.py` reconstruct **every** exit policy on **every** trade instead
of splitting your sample. A trade with `mfe_r = 1.4` and `mae_r = 0.6` tells you: `full_2R`
would have lost 1R, `partial_be` would have banked 0.4R on the partial and stopped the rest
at breakeven for +0.4R, `partial_be_early` likewise. That is a complete answer to "which
exit style suits my trading" from a single logged trade.

### The measurement window (this detail decides whether the comparison works at all)

Measure MFE and MAE off the trigger-timeframe candles, from `actual_entry`, with 1R
defined as `abs(actual_entry - actual_stop)` using the **original** stop.

**Window: from entry until the original stop price is touched, or 48 hours pass, whichever
comes first. Regardless of when you actually exited.**

That last clause is the important one. If you exit at 2R and stop measuring there, every
trade caps at `mfe_r = 2.0`, and then no policy with a target beyond 2R can ever be
evaluated. You would have permanently blinded yourself to the question "should I be
holding for more". So after the trade is closed, go back to the chart and finish measuring
the window. It takes about thirty seconds per trade and it is the difference between
having an answer about exits and guessing forever. `review.py` prints a warning if it
detects that MFE looks truncated at your live target.

Approximate to one decimal place. Do not round in your own favour, and record both fields
on losers too; losers are where the exit policy question is actually decided.

## Adherence: what counts as deviated

Mark `deviated` for any of these, **even if the trade won**:

- Entered before the trigger bar closed (front-running)
- Chased an entry after price left the zone
- Traded a C-grade level
- Traded against the 4H trend on anything other than an A-grade S2
- Took a setup with planned R:R below 2.0
- Used a stop tighter than the 0.20R fee-drag cap or the 0.75 x ATR noise floor
- Triggered on a finer timeframe than the anchor allows
- Moved a stop away from entry
- Sized above the stage's `risk_pct`, or above the grade multiplier
- Traded after hitting the 2-loss daily limit or 4-loss weekly limit
- Traded a setup that is not S1-S4
- Skipped an S4 signal (log this as a separate skipped-trade note; it corrupts the control)

The point of the flag is not self-flagellation. It is that after 40 trades you get a
number for what deviation actually costs you, and a number beats willpower.

## Skips

Optional but useful: keep `skips.csv` with `date_utc, symbol, setup, grade, reason,
outcome_if_taken`. If your skips would mostly have won, your filter is too tight. If they
would mostly have lost, your filter is working and that is worth knowing on the days when
skipping feels like missing out.
