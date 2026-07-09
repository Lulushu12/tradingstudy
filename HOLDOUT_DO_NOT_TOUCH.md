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

SCOPE EXTENSION (2026-07-08, research cycle 1): the quarantine covers ALL
BTCUSDT market data after the cutoff, explicitly including funding rates,
open interest metrics, premium index, and SPOT klines (spot prices proxy
perp prices). Research downloads must not fetch past 2026-06-21.

BREACH RECORD (2026-07-08): the trader uploaded a fresh TradingView export
for port validation which, unnoticed by both parties until read, covered
2026-07-05 16:15 through 2026-07-08 19:00 UTC bar opens, inside the holdout
span. That window is BURNED: it has been seen and used for port validation
(audit/burned/validation_export_BURNED_holdout_span.csv) and is EXCLUDED
from the final holdout verdict. Quarantine remains fully in force for the
unseen spans: 2026-06-21 17:00 through 2026-07-05 16:00 UTC bar opens, and
everything after 2026-07-08 19:00 UTC.

CONTAMINATION NOTE (from the trader, to be confirmed): the trader has traded
live and replay-practiced on recent data. The holdout span overlaps the
trader's lived market experience and is therefore weaker than a true blind
holdout. The final verdict must be weighted accordingly. The trader must
state at Gate 0 sign-off how much of the holdout span they actively traded
or replayed.
