# Verification brief

A first-pass extraction rated a set of strategies "FULL mechanizability", meaning every rule
is supposedly computable from OHLCV with only parameters the speaker actually stated.
That rating was applied loosely. Your job is to audit it strictly and, in most cases, knock it down.

## Your posture

Be a skeptic. Assume the FULL rating is wrong until the rules prove otherwise. The cost of a
false FULL is high: it sends a strategy into a backtest whose numbers will silently depend on
parameters somebody invented. The cost of a false PARTIAL is nearly zero.

## The test you apply

For each candidate, ask: could a competent programmer write a backtest of this from the note
alone, without ever choosing a number or a definition the speaker did not give?

Common things that DISQUALIFY a FULL rating:
- The strategy needs support/resistance levels, supply/demand zones, or "key levels" that a
  human draws by eye. Swing-high/swing-low detection needs a stated lookback; if none is
  stated, that is an invented parameter.
- It relies on a proprietary or custom indicator (a bespoke TradingView script, a colour-coded
  VSA panel, "RSI bars") whose formula is not given.
- Stops or targets are "below the candle", "a few pips", "at the recent low" without a rule.
- Thresholds like "high volume", "strong momentum", "clean slope", "tangled" are used as
  conditions but never quantified.
- The entry depends on something visible only on the chart in the video.
- Trend/consolidation is judged rather than computed.

Note that a strategy can still be worth testing with a handful of declared assumptions. That is
what the WITH_ASSUMPTIONS verdict is for. Just never pretend the assumption came from the video.

## Output

Append one block per candidate to your output file, in this exact format:

```
### <strategy name> (<video_id>)
- verdict: TESTABLE_AS_IS | TESTABLE_WITH_ASSUMPTIONS | NOT_TESTABLE
- assumption_count: <integer, 0 for TESTABLE_AS_IS>
- assumptions_required:
  1. <the specific missing number or definition, and what a coder would have to invent>
  2. ...
- blocking_issues: <only for NOT_TESTABLE: what makes it uncodeable at all>
- instrument: <what the speaker said, or NOT STATED>
- timeframe: <what the speaker said, or NOT STATED>
- needs_data_beyond_OHLCV: <yes/no, e.g. tick volume, order flow, session times, a second symbol>
- one_line_summary: <the strategy in one sentence>
```

Be precise about assumption_count. It is the number the reader will use to decide what to test
first. Do not pad it and do not shrink it.
