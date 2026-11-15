"""The ONLY sanctioned way to load bars. Enforces the holdout quarantine.

Scopes:
- "dev":               bars fully inside [DEV_START, DEV_END). A bar is included only if it opens at or after
                       DEV_START and CLOSES at or before DEV_END, so no bar straddles into the primary holdout.
- "qa":                full history. Reserved for data-quality checks (counts, gaps, duplicates). Must never be used
                       to compute prices, returns, indicators or anything outcome-related on holdout spans.
- "holdout_primary":   [PRIMARY_HOLDOUT_START, end). Phase 4 only.
- "holdout_secondary": [start, SECONDARY_HOLDOUT_END). Phase 4 only.

Holdout scopes require holdout_unlock.json in the repo root listing the scope, created only after explicit
approval at Gate 3. That file is gitignored so it can never be committed by accident.
"""
from __future__ import annotations

import json

import pandas as pd

from tradingstudy.config import CLEAN, DEV_END, DEV_START, PRIMARY_HOLDOUT_START, ROOT, SECONDARY_HOLDOUT_END, TIMEFRAMES

UNLOCK_FILE = ROOT / "holdout_unlock.json"
SCOPES = ("dev", "qa", "holdout_primary", "holdout_secondary")


class HoldoutLocked(PermissionError):
    pass


def _check_unlock(scope: str) -> None:
    if not UNLOCK_FILE.exists():
        raise HoldoutLocked(f"scope '{scope}' is locked: holdouts open only in Phase 4 after Gate 3 approval")
    allowed = json.loads(UNLOCK_FILE.read_text()).get("unlocked_scopes", [])
    if scope not in allowed:
        raise HoldoutLocked(f"scope '{scope}' not listed in {UNLOCK_FILE.name}")


def bar_minutes(tf: str) -> int:
    if tf in TIMEFRAMES:
        return TIMEFRAMES[tf]
    n, unit = int(tf[:-1]), tf[-1]
    return n * {"m": 1, "h": 60, "D": 1440, "W": 10080}[unit]


def clip_scope(df: pd.DataFrame, tf: str, scope: str) -> pd.DataFrame:
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope}")
    if scope in ("holdout_primary", "holdout_secondary"):
        _check_unlock(scope)
    if scope == "qa":
        return df
    close_t = df.index + pd.Timedelta(minutes=bar_minutes(tf))
    if scope == "dev":
        m = (df.index >= DEV_START) & (close_t <= DEV_END)
    elif scope == "holdout_primary":
        m = df.index >= PRIMARY_HOLDOUT_START
    else:
        m = close_t <= SECONDARY_HOLDOUT_END
    return df.loc[m]


def load_bars(sym: str, tf: str, scope: str = "dev") -> pd.DataFrame:
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope}")
    if scope in ("holdout_primary", "holdout_secondary"):
        _check_unlock(scope)
    df = pd.read_parquet(CLEAN / tf / f"{sym}.parquet")
    return clip_scope(df, tf, scope)


def load_funding(sym: str, scope: str = "dev") -> pd.DataFrame:
    if scope in ("holdout_primary", "holdout_secondary"):
        _check_unlock(scope)
    df = pd.read_parquet(CLEAN / "funding" / f"{sym}.parquet")
    if scope == "dev":
        return df.loc[(df.index >= DEV_START) & (df.index < DEV_END)]
    if scope == "holdout_primary":
        return df.loc[df.index >= PRIMARY_HOLDOUT_START]
    if scope == "holdout_secondary":
        return df.loc[df.index < SECONDARY_HOLDOUT_END]
    return df
