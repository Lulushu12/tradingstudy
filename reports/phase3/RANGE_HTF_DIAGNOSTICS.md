# Diagnostics E004 (range edges) and E005 (HTF entries with LTF structure stops)

Descriptive, declared in LEDGER.md before running. No strategy selected; nothing counted against the budget.

## E004: do range edges hold?

D1 = ranges confirmed in the dev period, their life after confirmation, and the share of time price sits inside a confirmed range. D2 = first touches of an active range edge from inside; from the touch bar's close, does price reach the range midpoint before trading 0.25 ATR beyond the edge (1m path, same minute = fail)? Benchmark = driftless random walk for the same distances. Implied R = fade to mid with the stop 0.25 ATR beyond the edge.

| TF | Ranges | Median life after confirm (h) | Time inside | Touches | Resolved | Mid first | Random-walk benchmark | Difference | Gross R | Fee R | Net R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15m | 2961 | 3.8 | 6.9% | 8451 | 8450 | 18.1% | 20.5% | -2.4 pts | -0.137 | 1.000 | -1.137 |
| 24m | 1894 | 6.0 | 6.7% | 5161 | 5161 | 17.4% | 19.6% | -2.2 pts | -0.116 | 0.740 | -0.856 |
| 1h | 688 | 17.0 | 7.2% | 1998 | 1998 | 17.5% | 19.5% | -2.0 pts | -0.164 | 0.276 | -0.440 |
| 4h | 164 | 72.0 | 6.9% | 472 | 472 | 13.6% | 17.9% | -4.3 pts | -0.392 | 0.134 | -0.527 |

By edge (bottom = long fade, top = short fade):

| TF | Edge | Resolved | Mid first | Benchmark | Net R |
|---|---|---|---|---|---|
| 15m | bottom | 4214 | 17.0% | 20.7% | -1.174 |
| 15m | top | 4236 | 19.3% | 20.3% | -1.101 |
| 24m | bottom | 2607 | 16.8% | 19.4% | -1.029 |
| 24m | top | 2554 | 18.0% | 19.7% | -0.686 |
| 1h | bottom | 983 | 17.7% | 19.9% | -0.467 |
| 1h | top | 1015 | 17.3% | 19.2% | -0.414 |
| 4h | bottom | 246 | 11.0% | 18.0% | -0.761 |
| 4h | top | 226 | 16.4% | 17.7% | -0.256 |

## E005: HTF entries with a 15m structure stop (+1 ATR)

From the HTF signal bar's close, on 1m bars over 24 h (1h signals) or 48 h (4h signals): share of signals touching +x R before -x R (same minute = adverse; neither = excluded). R = distance to the most recent confirmed 15m swing beyond the entry plus 1 x ATR(15m). Walk-forward test period 2023-01-01 to 2025-11-14.

| Signal TF | Entries | Gate | Signals | Median stop (HTF ATR) | +0.5R first | +1R first | +2R first | +3R first | Fee R |
|---|---|---|---|---|---|---|---|---|---|
| 1h | stack A | ungated | 4069 | 2.01 | 51.5% | 49.8% | 47.7% | 43.7% | 0.044 |
| 1h | stack A | Macro View lean | 2014 | 2.05 | 49.6% | 48.6% | 47.1% | 44.6% | 0.044 |
| 1h | WT div | ungated | 10950 | 1.99 | 50.3% | 48.6% | 44.9% | 41.3% | 0.044 |
| 1h | WT div | Macro View lean | 5432 | 2.00 | 49.8% | 48.7% | 44.2% | 41.7% | 0.045 |
| 1h | CONTROL random | ungated | 2207 | 2.10 | 50.9% | 50.5% | 51.4% | 50.3% | 0.047 |
| 4h | stack A | ungated | 1048 | 1.35 | 54.6% | 53.8% | 46.6% | 42.3% | 0.031 |
| 4h | stack A | Macro View lean | 447 | 1.36 | 53.2% | 53.2% | 45.0% | 42.9% | 0.031 |
| 4h | WT div | ungated | 2788 | 1.39 | 53.9% | 53.7% | 49.9% | 46.6% | 0.030 |
| 4h | WT div | Macro View lean | 1247 | 1.40 | 52.2% | 55.0% | 49.6% | 46.4% | 0.031 |
| 4h | CONTROL random | ungated | 2312 | 0.97 | 50.6% | 48.8% | 49.1% | 51.3% | 0.049 |
