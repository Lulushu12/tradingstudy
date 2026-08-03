# Pre-registration — Entry Hypothesis H4 (deleveraging reversion)

**Committed before the test was run.** No strategy code has been executed against the
open-interest data at the time of writing.

---

## Why this hypothesis exists

H1 proposed that violent moves in leveraged crypto are partly **forced flow** — liquidation
engines emitting market orders regardless of price — and that such moves should partly
revert once the forced supply is exhausted.

H1 could not test that directly. No liquidation or positioning data was available, so the
mechanism was **proxied by the shape of a candle**: a large wick that closed back inside its
range. That proxy failed, and failed *gross*, on 25 assets.

But a failed proxy is not a failed mechanism. The wick was always a guess about what was
happening to positioning; it never measured it. Open interest measures it directly.

**H4 is H1's mechanism with the real variable substituted for the proxy.** That makes it a
well-posed question rather than another pattern: did H1 fail because the idea was wrong, or
because the measurement was?

## The mechanism

Open interest is the number of contracts outstanding. It tells you whether a price move is
accompanied by positions **opening** or **closing**:

| Price | Open interest | Interpretation |
|---|---|---|
| down | **down** | longs being closed out — liquidation / capitulation |
| up | **down** | shorts being covered — a squeeze, not accumulation |
| down | up | new shorts entering — fresh conviction |
| up | up | new longs entering — fresh conviction |

The first two rows are position *closure*. The participants driving them are exiting, not
expressing a view, and when the exiting finishes there is no reason for price to hold. The
last two rows are new money taking a side, which carries information.

> **H4:** a large price move accompanied by a sharp FALL in open interest is deleveraging
> rather than repricing, and partially reverts.

## Design — a treatment arm and a control arm, registered together

A single test cannot show that open interest is doing any work. So both arms are registered
now, and the mechanism predicts they behave **differently**:

- **Treatment (traded):** large move + OI in the bottom decile of its trailing distribution
  → **fade** the move.
- **Control (measured, not traded):** large move + OI in the **top** decile → the same fade,
  which the mechanism predicts should be **worse**, because that move is new conviction.

If treatment and control perform the same, open interest carries no information here and H4
fails regardless of the treatment arm's sign.

### Entry conditions, at the close of hour *i*

| # | Condition | Value |
|---|---|---|
| 1 | Absolute bar return | ≥ **1.0 × ATR(14)** |
| 2 | ΔOI over the bar, as a percentile of its trailing 500-bar distribution | **≤ 10th** (treatment) / **≥ 90th** (control) |

Direction is **opposite the sign of the bar's return**, in both arms.

A percentile is used rather than a fixed percentage deliberately: it self-calibrates across
assets and volatility regimes, and avoids inventing a magic number.

Funding rate and taker-flow imbalance are **not** entry conditions. They are recorded and
reported as descriptive splits only. Adding them would enlarge the search surface, and the
point here is to test one mechanism cleanly.

### Levels — identical to H3, so only the entry differs

- **Stop:** 2.5 × ATR(14) — the cost-derived value from `PREREGISTRATION_H3.md`, unchanged.
- **Target:** 2.0R.
- **Time stop:** 96 bars.
- **Entry:** market at the close of the signal bar. Perp klines and perp costs.

Nothing about the exit is re-tuned. H4 versus H3 is therefore a clean comparison of entry
logic on identical geometry.

## Data

Binance USD-M perpetual archive: 1h perp klines and 5-minute metrics aggregated to hourly by
taking the **last** observation inside each hour, which is the only value a decision at that
close could have used. Open-interest history begins around 2022, giving roughly 3.5 years per
symbol across ~15 liquid perpetuals.

This data has **never been used** anywhere in this study, so the whole span is fresh.

## Success criteria — fixed in advance

- **SUPPORTED:** treatment pooled mean R > 0, the **95%** cross-sectional weekly block
  bootstrap CI excludes zero, **≥ 60%** of assets positive, **and** treatment mean exceeds
  control mean.
- **SUGGESTIVE:** treatment mean > 0, ≥ 60% of assets positive, and treatment beats control,
  but the CI includes zero.
- **NOT SUPPORTED:** anything else — including the case where treatment is positive but does
  **not** beat control, since that would show the open-interest condition is inert.
- **UNDERPOWERED:** pooled treatment n < 1,500.

## Not allowed after seeing results

- Changing the ATR threshold, the decile cut, the stop, the target or the time stop.
- Adding funding or taker-flow conditions to the entry.
- Swapping the direction to continuation and reporting that instead — that would be H2's
  error repeated with better data, and it needs its own registration.
- Reporting the control arm as the finding if the treatment arm fails.

## Limitations acknowledged in advance

- Open interest is aggregate; it does not identify *whose* positions closed, nor separate
  forced liquidation from voluntary exit.
- The metrics archive starts in 2022, so this cannot see 2021 or earlier.
- Binance is one venue. Positioning elsewhere is invisible.
- Hourly OI is a snapshot at the bar close, not a flow measurement within the bar.
- Funding is modelled as a constant drag rather than using the real settled rate, for
  consistency with every other test in this study. The real rate is available and could be
  used later, but changing the cost model here would break comparability with H3.
