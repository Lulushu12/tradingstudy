"""Project-wide constants. Split dates here are PROVISIONAL until PROTOCOL.md is frozen at Gate 1."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
CLEAN = DATA / "clean"
REPORTS = ROOT / "reports"

SYMBOLS = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE", "SUI", "LINK", "AVAX"]


def pair(sym: str) -> str:
    return f"{sym}USDT"


# Timeframes built from 1m. Value = bar length in minutes (1W handled as 10080, anchored Monday 00:00 UTC).
TIMEFRAMES = {
    "6m": 6,
    "15m": 15,
    "24m": 24,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1D": 1440,
    "1W": 10080,
}

# Download snapshot: last complete UTC day available in the archives at download time.
DOWNLOAD_DATE = pd.Timestamp("2026-11-15", tz="UTC")

# Splits, FROZEN in PROTOCOL.md at Gate 1 (2026-11-15).
SECONDARY_HOLDOUT_END = pd.Timestamp("2022-01-01", tz="UTC")  # everything before this is locked
PRIMARY_HOLDOUT_START = pd.Timestamp("2025-11-15", tz="UTC")  # most recent 12 months, locked
DEV_START = SECONDARY_HOLDOUT_END
DEV_END = PRIMARY_HOLDOUT_START  # exclusive

# Warm-up (PROTOCOL section 1, approved): bars up to this many days before a split's first evaluated bar may be used
# to compute indicators and structure only. Never for labels, trades or statistics.
WARMUP_DAYS = 400
