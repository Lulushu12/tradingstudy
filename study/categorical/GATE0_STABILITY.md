# Gate 0 stability: per-year split of the trade-shaped tests

Decile edges fixed on the pooled sample, then held constant across years. Costs at 0.08% round trip, no slippage. CIs are moving-block bootstrap on gross expectancy.

## CONSOLIDATION template (fade to range midpoint)


### 15m, ER decile 0

| year | n | win rate | gross R | 95% CI | cost/R | net R |
|---|---|---|---|---|---|---|
| 2021 | 2,460 | 81.7% | +0.1251 | [+0.0954, +0.1554] | 0.0525 | **+0.0725** |
| 2022 | 2,521 | 81.2% | +0.1051 | [+0.0774, +0.1343] | 0.0814 | **+0.0237** |
| 2023 | 2,737 | 80.6% | +0.1080 | [+0.0763, +0.1404] | 0.1255 | **-0.0176** |
| 2024 | 2,563 | 77.5% | +0.0713 | [+0.0410, +0.1036] | 0.0937 | **-0.0224** |
| 2025 | 2,472 | 79.7% | +0.1153 | [+0.0833, +0.1497] | 0.1235 | **-0.0082** |
| 2026 | 1,087 | 82.9% | +0.1496 | [+0.1100, +0.1865] | 0.1059 | **+0.0437** |
| **pooled** | 13,840 | 80.3% | +0.1083 | [+0.0951, +0.1216] | 0.0917 | **+0.0165** |

Net positive in **3 of 6** years. Worst year -0.0224 R, best +0.0725 R.

### 4H, ER decile 0

| year | n | win rate | gross R | 95% CI | cost/R | net R |
|---|---|---|---|---|---|---|
| 2021 | 144 | 81.9% | +0.1368 | [+0.0518, +0.2155] | 0.0118 | **+0.1250** |
| 2022 | 177 | 80.8% | +0.0941 | [-0.0103, +0.2019] | 0.0181 | **+0.0760** |
| 2023 | 135 | 82.2% | +0.1126 | [-0.0122, +0.2544] | 0.0264 | **+0.0861** |
| 2024 | 153 | 82.4% | +0.1312 | [+0.0149, +0.2255] | 0.0205 | **+0.1107** |
| 2025 | 195 | 79.0% | +0.1270 | [+0.0214, +0.2429] | 0.0261 | **+0.1009** |
| 2026 | 98 | 77.6% | +0.1176 | [+0.0093, +0.2919] | 0.0228 | **+0.0949** |
| **pooled** | 902 | 80.7% | +0.1196 | [+0.0864, +0.1631] | 0.0205 | **+0.0991** |

Net positive in **6 of 6** years. Worst year +0.0760 R, best +0.1250 R.

## DIRECTION template (break to new extreme)


### 15m, ER decile 9

| year | n | win rate | gross R | 95% CI | cost/R | net R |
|---|---|---|---|---|---|---|
| 2021 | 2,845 | 65.9% | +0.1937 | [+0.1128, +0.2678] | 0.0533 | **+0.1404** |
| 2022 | 2,890 | 60.4% | +0.1022 | [+0.0220, +0.1860] | 0.0639 | **+0.0382** |
| 2023 | 2,226 | 56.6% | +0.1112 | [+0.0256, +0.2107] | 0.0955 | **+0.0157** |
| 2024 | 2,201 | 60.9% | +0.0686 | [-0.0114, +0.1370] | 0.0702 | **-0.0016** |
| 2025 | 2,578 | 59.9% | -0.0083 | [-0.0810, +0.0784] | 0.0925 | **-0.1007** |
| 2026 | 1,100 | 62.3% | +0.1067 | [+0.0173, +0.2265] | 0.0856 | **+0.0211** |
| **pooled** | 13,840 | 61.0% | +0.0969 | [+0.0629, +0.1317] | 0.0710 | **+0.0259** |

Net positive in **4 of 6** years. Worst year -0.1007 R, best +0.1404 R.

### 4H, ER decile 9

| year | n | win rate | gross R | 95% CI | cost/R | net R |
|---|---|---|---|---|---|---|
| 2021 | 73 | 52.1% | -0.1122 | [-0.3602, +0.4126] | 0.0140 | **-0.1262** |
| 2022 | 189 | 69.3% | +0.1774 | [-0.0276, +0.3618] | 0.0147 | **+0.1627** |
| 2023 | 229 | 63.8% | +0.3107 | [-0.0496, +0.6984] | 0.0246 | **+0.2861** |
| 2024 | 179 | 69.8% | +0.1802 | [+0.0169, +0.4462] | 0.0210 | **+0.1592** |
| 2025 | 158 | 68.4% | +0.1274 | [-0.0685, +0.4323] | 0.0246 | **+0.1028** |
| 2026 | 74 | 75.7% | +0.3097 | [-0.0328, +0.6085] | 0.0226 | **+0.2871** |
| **pooled** | 902 | 67.0% | +0.1904 | [+0.0736, +0.3235] | 0.0203 | **+0.1701** |

Net positive in **5 of 6** years. Worst year -0.1262 R, best +0.2871 R.

## Robustness of the fade result

| TF | median hold (bars) | p90 | mean concurrent positions | both-hit % | net R if all both-hits are losses |
|---|---|---|---|---|---|
| 15m | 1 | 12 | 0.34 | 0.38% | +0.0123 |
| 4H | 1 | 12 | 0.33 | 0.33% | +0.0954 |

### Pessimistic fill: target must be penetrated by pen x ATR to count as filled

| TF | pen 0.00 | pen 0.05 | pen 0.10 | pen 0.25 |
|---|---|---|---|---|
| 15m | +0.0165 | +0.0020 | -0.0111 | -0.0455 |
| 4H | +0.0991 | +0.0935 | +0.0838 | +0.0711 |

---

## Conclusion of the stability test

The kill test did not kill it.

**4H consolidation template survives everything thrown at it.** Net positive in 6 of 6 years
(worst +0.0760 R, best +0.1250 R), pooled +0.0991 R with a bootstrap CI on gross expectancy of
[+0.0899, +0.1655] excluding zero. The 2021 bull market is not carrying it: 2024 is +0.1107 and
2025 is +0.1009. It survives counting every ambiguous both-hit bar as a full loss (+0.0954 R) and
survives requiring the target to be penetrated by a quarter of an ATR before it counts as filled
(+0.0711 R).

**15m does not survive.** Pooled net is +0.0165 R, which is inside the execution-assumption noise.
Requiring 0.10 ATR of target penetration turns it negative (-0.0111 R). It is net positive in only
3 of 6 years. The 15m edge is real gross and is consumed by friction, exactly as the cost table in
GATE0_VERDICT.md section 3 predicted for everything below 1h.

**The direction template is the noisier twin.** 4H is net positive in 5 of 6 years at +0.1701 R
pooled, but 2021 is -0.1262 R and only one of six per-year CIs excludes zero. Higher headline
expectancy, much wider dispersion, driven by a 67% win rate at high R:R rather than an 81% win
rate at low R:R. It is a real candidate but a weaker one than the fade, and it should not be
carried forward on the strength of its pooled number alone.

### What is still not established

1. **Per-year sample sizes on 4H are 98 to 195 trades.** Only 2021, 2024, 2025 and 2026 have
   per-year CIs excluding zero for the fade. The pooled result carries the significance; the
   per-year table establishes consistency of sign, not six independent confirmations.
2. **Slippage is still not modelled**, only the 0.08% commission. On 4H the risk distance is 3.9%
   of price so 0.05% of slippage costs 0.013 R and changes nothing. On 15m the same slippage costs
   0.057 R and would flip it negative on its own. This asymmetry is the whole story of this study.
3. **The 0.08% figure is the repo's standing assumption and remains unverified** against an actual
   venue schedule.
4. **This is one asset.** BTCUSDT.P only. A regime effect that appears on one instrument over five
   years is a hypothesis, not a finding.
5. **Decile 0 is a selected cell.** Deciles 1 and 2 were also net positive on 4H in the pooled
   run, which is reassuring, but the reported number is the best one.
6. **No holdout.** Every number here is on data the repo already contains. Under the operating
   principles in CLAUDE_CODE_PROMPT.md this can only falsify, never confirm.
7. **Median hold is 1 bar with a p90 of 12.** On 4H that is a 4-hour to 2-day hold, which is
   nothing like the scalping in the source video. Whatever this is, it is not the strategy the
   video teaches. It shares a classifier and nothing else.

Gate 0 is complete. Nothing proceeds without an explicit go.
