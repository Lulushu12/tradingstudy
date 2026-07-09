# RESEARCH PROTOCOL, CYCLE 1

Frozen 2026-07-08, before any external data was downloaded and before any
candidate was tested. Rules below are complete; changing any rule after its
first sandbox run kills the candidate (a rewrite costs one of the five
slots). Every executed test is logged in audit/research/TEST_LEDGER.md.

## Data segments

- SANDBOX: 2021-01-07 through 2023-12-31 (C2: from 2021-12-01, where the
  public OI metrics series begins; a data constraint, not a choice).
- VALIDATION: 2024-01-01 through 2026-06-21. Touched exactly once per
  candidate, only after its sandbox verdict, only with the trader's go.
- HOLDOUT: everything after 2026-06-21 16:45 bar opens stays quarantined,
  now explicitly including funding, open interest, premium index, and spot
  series, not just perp OHLCV.

## Cost model and mechanics (identical to AUDIT_COMMITMENTS.md)

Commission 0.08% of notional per round trip, slippage 0.01% per fill, swap
0.0055% per 4h UTC boundary held. Entries at the next 15m open after a
closed-bar signal. Market orders only. Risk 0.5% of equity per trade; skip
if stop distance < 1.0% of entry (cost floor guard for this cycle). All
percentile windows are trailing and causal. Time exits fill at the exit
bar's 15m close. Same-bar stop+target ambiguity resolved as stop.

## Pass bars (frozen)

- Sandbox: net expectancy >= +0.15R, and more than half of half-year
  windows with nonnegative expectancy. Fail either -> candidate dead.
- Validation (survivors only): net expectancy >= +0.10R with >= 100 trades
  (>= 50 for C4 and C5, the low-frequency candidates), majority of windows
  nonnegative. A survivor's t-stat must also clear a Bonferroni factor of 5
  (selection across candidates).
- Any final survivor must pass the venue survivability bootstrap (K5 form).
- Expected outcome, stated in advance: all five die.

## Candidates (all parameters fixed here, chosen from mechanism scale, not
## from data)

C1 FUNDING EXTREME FADE. Series: 8h funding rate. At a funding timestamp,
compute its percentile within the trailing 90 days of funding prints. If
>= 98th percentile: SHORT. If <= 2nd: LONG. Enter at next 15m open. Exit:
24h time limit or 3% adverse stop, whichever first. Cooldown: no new entry
in the same direction within 24h of the last entry.

C2 OI FLUSH REVERSION. Series: sumOpenInterest (5m metrics) resampled to
15m closes. Signal at bar t close: OI down >= 5% over the last 8 bars AND
|price return| >= 2% over the same 8 bars. Direction: fade the price move.
Stop: the price extreme of those 8 bars (skip if < 1% away). Exit: 24h time
limit or stop. Cooldown 24h per direction.

C3 PREMIUM EXTREME FADE. Series: premium index 15m closes. Signal: close
>= 99.5th percentile of the trailing 30 days -> SHORT; <= 0.5th -> LONG.
Exit: 24h time limit or 3% stop. Cooldown 24h per direction.

C4 WEEKEND MOVE FADE. Signal at Sunday 20:00 UTC bar close: weekend return
r = close(Sun 20:00) / close(Fri 20:00) - 1. If |r| >= 1.5%: fade it.
Exit: Monday 20:00 UTC close or 3% stop.

C5 VOLATILITY COMPRESSION BREAKOUT. Daily UTC bars from 15m. Compression:
(10d highest high - 10d lowest low) / close at or below its 10th percentile
over the trailing 365 days. While compressed, arm the levels: 10d high and
10d low. Trigger: first 15m CLOSE beyond a level within the next 5 days ->
enter next open in breakout direction. Stop: the opposite level. Exit: 5
days after entry or stop. One trade per compression episode.

## Honesty clauses

- These five rules were written from mechanism priors before downloading
  the external series. The perp OHLCV itself was studied extensively in
  prior phases; nothing here was derived from those results except the
  cost-floor shape (wide stops, slow holds), which is arithmetic.
- Percentile thresholds (98/2, 99.5/0.5, 5%/2%, 1.5%, 10th) were fixed by
  judgment ex ante. No grid exists. If a threshold turns out to produce
  zero or degenerate trade counts, the candidate reports that and dies; it
  does not get re-thresholded.
- If all five die, the cycle ends with "no system" and that verdict stands.
