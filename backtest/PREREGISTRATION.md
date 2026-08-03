# Pre-registration — Entry Hypothesis H1

**Committed before the test was run.** The commit that adds this file contains no results.
Whatever the numbers say, they are reported as they come out.

---

## Why a new entry hypothesis at all

Everything tested so far shares one origin: a trend/regime classifier reading EMAs, ADX and
RSI on hourly closes. Its **gross** average R — before a single fee — was within 0.04R of
zero on all three symbols across 28,461 trades, and it was negative out of sample. That is
not a cost problem or an exit problem. Trend continuation measured on hourly closes in ETH,
LINK and SOL is a coin flip, and every subsequent refinement was reducing the cost of
trading a coin flip.

So the new hypothesis must come from a **different source of edge**, not a better filter on
the same one.

## The reasoning

If a signal is a coin flip, it is usually because the counterparty is at least as informed
as you are. The way out is to find trades where the counterparty is **not choosing to
trade at all**.

Leveraged crypto perpetuals have exactly that: forced liquidations. When price moves against
crowded leverage, exchange liquidation engines emit market orders regardless of price, into
whatever book depth exists. The resulting spike is not an informed repricing — it is a
mechanical consequence of margin arithmetic. Once the forced flow is exhausted, there is no
reason for price to stay there.

This is structurally specific to leveraged crypto, it is not a trend statement, and it is
not something any setup tested so far looks at. The existing `EXHAUSTION` setup keys off
distance from the 21 EMA and RSI — a *slow* stretch measured over many bars. H1 keys off the
**shape of a single bar**: a violent excursion that was absorbed within the hour.

## H1 — Liquidation-wick reversion

> An hourly bar containing an outsized wick that dominates its own range, on abnormal
> volume, marks forced flow being absorbed rather than informed repricing, and price
> partially reverts away from the wick extreme.

### Entry conditions (long; short is the exact mirror)

At the close of bar *i*, using only data through bar *i*:

| # | Condition | Value |
|---|---|---|
| 1 | Lower wick size: `min(open, close) − low` | ≥ **1.0 × ATR(14)** |
| 2 | Wick dominates the bar: `wick / (high − low)` | ≥ **0.50** |
| 3 | Close recovered: `(close − low) / (high − low)` | ≥ **0.50** |
| 4 | Abnormal participation: volume z-score over 100 bars | ≥ **1.0** |

No trend, ADX or EMA condition. The mechanism is regime-agnostic by construction, and
adding a regime filter would smuggle the old hypothesis back in.

### Levels

- **Stop:** `low − 0.25 × ATR` (below the cascade extreme). Capped at 2.5 ATR, floored at
  0.6 ATR. If price revisits the wick low, the absorption thesis is simply wrong.
- **Target:** **2.0R**.
- **Time stop:** **48 bars**. Absorption should resolve quickly; if it hasn't in two days,
  the premise has lapsed.

### Execution

- **Primary:** market entry at the close of the signal bar.
- **Secondary:** the v3 resting limit (0.25 ATR better, 6-bar expiry), reported alongside.

Both use the v3 cost model — maker on resting entries and target exits, taker plus slippage
on market entries, stops and time exits.

## Success criteria — fixed in advance

Tested on the **PRIOR window (2024-04-22 → 2025-06-12)**, which no design decision in this
study has ever been fitted to.

- **Supported:** mean R > 0 **and** the 95% block-bootstrap CI excludes zero.
- **Suggestive:** mean R > 0, CI includes zero, but the sign is consistent across all three
  symbols *and* replicates on the MAIN and 15m datasets.
- **Not supported:** anything else.

If pooled n < 100, the test is underpowered and will be reported as inconclusive rather
than as a result, regardless of the point estimate.

## What is NOT allowed after seeing results

- Changing any of the four thresholds, the stop rule, the target, or the time stop.
- Adding a regime, session or symbol filter.
- Reporting the best of several variants as though it were the pre-registered one.

Any of those turns this into the same exercise that already failed twice in this study. If
H1 fails, it gets reported as a failure and the next hypothesis needs its own
pre-registration.

## Known limitations, acknowledged in advance

- Hourly bars hide the intrabar path. A large wick tells us price went there and came back;
  it does not prove liquidations caused it. Without liquidation-feed data this is a proxy.
- Wick size and volume z-score are correlated with volatility regime, so H1 will naturally
  fire more in high-vol periods. This is not corrected for.
- Three symbols over two windows is not many independent regimes.
