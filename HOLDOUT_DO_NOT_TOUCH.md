# HOLDOUT QUARANTINE

Status: ACTIVE. No script may read, load, plot, print, describe, or compute
anything on this data until the final holdout test, which itself requires the
trader's explicit written go in conversation. Every data-loading script must
check its inputs against this file before loading.

PATH: /home/user/tradingstudy/holdout

SPAN: all BTCUSDT perp data for bars opening at or after
2026-06-21 17:00:00 UTC (unix 1782061200), on any timeframe, from any source.
The quarantine is defined by the SPAN, not just the file: fetching the same
span from another source is equally forbidden. The holdout file currently
contains 1,468 15m bars (through 2026-07-06 23:45 UTC bar open) and may be
extended forward by appending newer bars via audit/fetch_holdout.py, which
never prints row content. Extending is allowed; reading is not.

STUDIED SPAN (allowed): bars opening 2021-01-07 07:00:00 UTC through
2026-06-21 16:45:00 UTC inclusive.

CONTAMINATION NOTE (from the trader, to be confirmed): the trader has traded
live and replay-practiced on recent data. The holdout span overlaps the
trader's lived market experience and is therefore weaker than a true blind
holdout. The final verdict must be weighted accordingly. The trader must
state at Gate 0 sign-off how much of the holdout span they actively traded
or replayed.
