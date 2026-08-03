"""Data loading and integrity auditing for the crypto OHLCV in this repo.

TradingView exports carry indicator columns alongside OHLCV. Only time/OHLCV is used;
every indicator column in the file is ignored and recomputed from scratch, so a stale
or misconfigured TradingView study cannot leak into a backtest.
"""
from __future__ import annotations

import glob
import os

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Multi-file exports are chunks of one continuous series and get concatenated.
SOURCES = {
    "BTCUSDT_1D": ["BINANCE_BTCUSDT.P, 1D.csv"],
    "BTCUSDT_1W": ["BINANCE_BTCUSDT.P, 1W.csv"],
    "BTCUSDT_4h": ["BINANCE_BTCUSDT.P, 240.csv"],
    "BTCUSDT_15m": ["15/*.csv", "New export/15m/*.csv"],
    "BTCUSDT_1h": ["1h/*.csv"],
    "BTCUSDT_5m": ["BINANCE_BTCUSDT.P, 5.csv", "5m/**/*.csv", "New export/5m/**/*.csv"],
    "XRPUSDT_15m": ["HA SHA MFI/*.csv"],
}

BAR_SECONDS = {"1W": 604800, "1D": 86400, "4h": 14400, "1h": 3600, "15m": 900, "5m": 300}


def _read_one(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=lambda c: c.strip().lower() in
                     ("time", "open", "high", "low", "close", "volume"))
    df.columns = [c.strip().lower() for c in df.columns]
    if "volume" not in df.columns:
        df["volume"] = float("nan")
    return df[["time", "open", "high", "low", "close", "volume"]]


def load(key: str) -> pd.DataFrame:
    """Concatenate every chunk for `key`, drop duplicate timestamps, sort ascending."""
    paths: list[str] = []
    for pat in SOURCES[key]:
        paths.extend(sorted(glob.glob(os.path.join(REPO, pat), recursive=True)))
    if not paths:
        raise FileNotFoundError(f"no files matched for {key}")
    df = pd.concat([_read_one(p) for p in paths], ignore_index=True)
    df = df.dropna(subset=["time", "open", "high", "low", "close"])
    df["time"] = df["time"].astype("int64")
    df = df.drop_duplicates(subset="time", keep="first").sort_values("time")
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.reset_index(drop=True)


def audit(key: str) -> dict:
    """Integrity report. Numbers only, no interpretation."""
    paths: list[str] = []
    for pat in SOURCES[key]:
        paths.extend(sorted(glob.glob(os.path.join(REPO, pat), recursive=True)))
    raw = pd.concat([_read_one(p) for p in paths], ignore_index=True)
    df = load(key)
    tf = key.split("_")[1]
    step = BAR_SECONDS[tf]

    d = df["time"].diff().dropna()
    gaps = d[d != step]
    expected = (df["time"].iloc[-1] - df["time"].iloc[0]) // step + 1

    bad_hl = int((df["high"] < df["low"]).sum())
    bad_oc = int(((df["open"] > df["high"]) | (df["open"] < df["low"]) |
                  (df["close"] > df["high"]) | (df["close"] < df["low"])).sum())
    return {
        "key": key,
        "files": len(paths),
        "rows_raw": len(raw),
        "rows_dedup": len(df),
        "duplicate_ts_dropped": len(raw) - len(df),
        "start": str(df["dt"].iloc[0]),
        "end": str(df["dt"].iloc[-1]),
        "expected_bars": int(expected),
        "missing_bars": int(expected - len(df)),
        "coverage_pct": round(100 * len(df) / expected, 3),
        "irregular_steps": int(len(gaps)),
        "largest_gap_bars": int(gaps.max() // step) if len(gaps) else 0,
        "bars_high_lt_low": bad_hl,
        "bars_oc_outside_hl": bad_oc,
        "zero_volume_bars": int((df["volume"] == 0).sum()),
        "nan_volume_bars": int(df["volume"].isna().sum()),
    }


if __name__ == "__main__":
    rows = []
    for k in SOURCES:
        try:
            rows.append(audit(k))
        except Exception as e:  # a missing/broken source is reported, not hidden
            rows.append({"key": k, "error": str(e)})
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 250, "display.max_columns", 50)
    print(out.to_string(index=False))
