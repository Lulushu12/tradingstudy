"""Signal generators for the Phase 2 baselines (PROTOCOL section 5) and label targets (section 4).

A signal is stamped on the execution bar whose close makes it known; the limit entry is that bar's close.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

META = ["close", "atr14", "upleg_a", "upleg_b", "downleg_a", "downleg_b", "next_level_above", "next_level_below",
        "r1_trend", "r2_trend", "session", "hour_utc"]


def _recent(x: np.ndarray, window: int) -> np.ndarray:
    return pd.Series(x.astype(float)).rolling(window + 1, min_periods=1).max().to_numpy() > 0


def stack_mask(df: pd.DataFrame, side: str, variant: str, window: int = 11) -> np.ndarray:
    """Baseline 1: WT regular dot divergence + MF regular divergence, same direction, later within `window` bars.
    Variant A both confirmed; B one confirmed and the other front-run."""
    wa = df[f"wtdiv_{side}_reg"].to_numpy(bool); ma = df[f"mfdiv_{side}_reg"].to_numpy(bool)
    if variant == "A":
        return (wa & _recent(ma, window)) | (ma & _recent(wa, window))
    wb = df[f"wtdiv_fr_{side}"].to_numpy(bool); mb = df[f"mfdiv_fr_{side}"].to_numpy(bool)
    return (wb & _recent(ma, window)) | (mb & _recent(wa, window))


def to_signals(df: pd.DataFrame, bull: np.ndarray, bear: np.ndarray) -> pd.DataFrame:
    both = bull & bear  # conflicting directions on one bar: skip
    d = np.where(bull & ~both, 1, np.where(bear & ~both, -1, 0))
    sig = df.loc[d != 0, META].copy()
    sig["direction"] = d[d != 0]
    return sig


def stack_signals(df: pd.DataFrame, variant: str, htf_filter: str | None = None) -> pd.DataFrame:
    bull, bear = stack_mask(df, "bull", variant), stack_mask(df, "bear", variant)
    if htf_filter == "near_cross":
        bull &= df["htf_near_cross_bull"].to_numpy(bool)
        bear &= df["htf_near_cross_bear"].to_numpy(bool)
    elif htf_filter == "mf_dir":
        rising = df["htf_mf_rising"].to_numpy(bool)
        bull &= rising
        bear &= ~rising
    return to_signals(df, bull, bear)


def flip_signals(df: pd.DataFrame, events: pd.DataFrame, tf: str, variant: str) -> pd.DataFrame:
    """Baseline 2: range flips detected on the execution TF itself."""
    v = 0 if variant == "A" else 1
    e = events[(events["tf"] == tf) & (events["variant"] == v)]
    bull = np.zeros(len(df), bool); bear = np.zeros(len(df), bool)
    pos = df.index.get_indexer(e["exec_time"])
    ok = pos >= 0
    bull[pos[ok & (e["direction"].to_numpy() == 1)]] = True
    bear[pos[ok & (e["direction"].to_numpy() == -1)]] = True
    return to_signals(df, bull, bear)


TARGETS = ["1R", "1.5R", "2R", "3R", "fib1.272", "fib1.618", "next_level"]


def target_prices(sig: pd.DataFrame, stop_dist: np.ndarray, spec: str) -> np.ndarray:
    """Fixed target per signal; NaN means the trade is skipped (level target under 1R or on the wrong side)."""
    e = sig["close"].to_numpy(); d = sig["direction"].to_numpy()
    if spec.endswith("R"):
        return e + d * float(spec[:-1]) * stop_dist
    if spec.startswith("fib"):
        x = float(spec[3:])
        a = np.where(d == 1, sig["upleg_a"], sig["downleg_a"]); b = np.where(d == 1, sig["upleg_b"], sig["downleg_b"])
        t = a + x * (b - a)
    else:
        t = np.where(d == 1, sig["next_level_above"], sig["next_level_below"]).astype(float)
    ok = (d * (t - e)) >= stop_dist
    return np.where(ok, t, np.nan)
