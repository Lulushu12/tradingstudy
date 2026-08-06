# Prep routine

The system is alert-driven. That only works if the preparation is genuinely done in
advance, because the alternative is drawing levels while price runs at them, which is how
a C grade becomes "basically an A".

---

## Weekly, Sunday, roughly 45 minutes

For each watchlist symbol:

1. Export or refresh the 4H chart. Run the map:

   ```
   python3 levels.py "path/to/SYMBOL, 240.csv" --near 12
   ```

2. Look at the 1D and 4H by eye. Decide, and write down:
   - **Structure quality: A, B or C.** Can you draw clean levels that price has actually
     respected? If not, the symbol sits out this week. A cluttered chart is not a
     tradeable chart.
   - **Trend state** from the tool's EMA200 line. This sets your permitted direction.
   - **Market state**: trending, post-impulse range, or undefined. Undefined means no
     trades on that symbol.
   - If a range: mark its high and low, confirm each was made by several candles rather
     than one wick, and note the golden pocket from the tool output.

3. Take the tool's A and B zones and sanity check each one by eye. The tool counts
   arithmetic agreement; you are checking whether the level was ever actually respected.
   Delete the ones that were not. Keeping a level the market has ignored twice is the
   most common way this system degrades.

4. Set price alerts at every surviving A and B zone. Alerts are the interface to the
   market this week. Not the chart.

5. Write the week's plan in one line per symbol:
   `SYMBOL | trend | state | zones I will trade | direction permitted`

Symbols with C structure quality get no alerts and are not traded, no matter what they do.

---

## Daily, start of session, roughly 10 minutes

1. Re-run `levels.py` for symbols where a new extreme printed. Prior day high/low update
   every day, so this is not optional. For symbols in play, also run the 1h export so the
   lower anchors are prepared in advance rather than discovered live.
2. If a range extended overnight, **re-pull it**. Per lesson 28 the whole updated range is
   now the working range, and the old golden pocket is no longer a level. Delete it.
3. Confirm alerts are still set at the right prices.
4. Check the account state against Layer 0: how many losses this week, how much drawdown
   used, how much risk is currently open.
5. Do not add new analysis. Prep is over when it is over.

---

## When an alert fires

Work down this list, in order. Any "no" ends it.

1. Which symbol, which zone, what grade, **which anchor timeframe**? If C: **stop**.
2. Is the direction permitted by the 4H context gate? Against trend needs grade A and an
   S2 setup. If not: **stop**.
3. Which of S1, S2, S3, S4 is this? If you cannot name it: **stop**.
4. Distance to the next opposing zone from the map. Is it >= 2.0R from a valid stop?
   If not: **stop**.
5. Does the stop clear **both** minimums: fee drag <= 0.20R (>= 0.40% at Breakout's
   fees) and >= 0.75 x ATR14 on the trigger timeframe? If not, widen and re-check step 4,
   or **stop**. You may not use the tighter stop.
6. Wait for the trigger, on the timeframe the anchor dictates (1D->1h, 4H->15m, 1h->5m,
   15m->5m, or 1m for S2 only), on a **closed bar**: MC divergence, money flow turn,
   cooldown of 3+ bars since the opposing dot, two consecutive higher lows or lower highs.
7. **Write the pre-trade journal row.** Setup, grade, confluence families, anchor
   timeframe, planned entry, stop, target, R:R, risk %.
8. Enter, market, after the bar closes.
9. Set the stop immediately. Set the alert for the first partial.

Then leave it alone.

---

## After the trade closes

1. Fill the post-trade fields.
2. Go back to the chart and finish measuring MFE and MAE over the **full window** defined
   in `JOURNAL_SCHEMA.md`, from entry until the original stop was touched or 48 hours
   passed, regardless of when you actually exited. Thirty seconds. Do not skip it; it is
   the entire basis of the exit-policy answer.
3. Mark adherence honestly. A winning trade taken by breaking a rule is `deviated`.
4. Screenshot the entry chart if you can.

---

## Every 40 trades

```
python3 review.py journal.csv
```

Read the whole output. Write a dated block note in the Amendment Log of
`SYSTEM_SPEC_v1.md`. Amendments happen here or nowhere.

If it is not a review point, the rules do not change. Not after a loss, not after a
streak, not because something obvious appeared. Especially then.
