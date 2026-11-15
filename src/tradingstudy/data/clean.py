"""Build cleaned 1m bars and funding series from the untouched raw zips.

Raw files are never modified. Output: data/clean/1m/{SYM}.parquet, data/clean/funding/{SYM}.parquet,
plus data/clean/1m/{SYM}_stats.json describing what cleaning did.

Cleaning rules (logged, never silent):
- Duplicate timestamps: keep the row from the later file (daily overrides monthly); count exact vs conflicting dupes.
- Non-positive prices: row dropped.
- OHLC inconsistency (high below open/close, low above open/close): high/low widened to contain open and close.
- Frozen minutes (zero volume, flat OHLC) are archive defects: Binance's kline archive lost real trading and wrote
  flat placeholders. They are rebuilt from the aggTrades archive when it is present (see repair.py); minutes with
  no trades in aggTrades either are dropped and become gaps.
- Gaps are NOT filled. Missing minutes stay missing; downstream code sees them via n_1m in resampled bars.

Usage: uv run python -m tradingstudy.data.clean [SYMBOL ...]
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from tradingstudy.config import CLEAN, RAW, SYMBOLS
from tradingstudy.data.repair import repair_frozen_minutes

KLINE_COLS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]
KEEP = ["open", "high", "low", "close", "volume", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume"]


def _read_zip(path) -> pd.DataFrame:
    first = pd.read_csv(path, header=None, nrows=1)
    has_header = not str(first.iloc[0, 0]).strip().lstrip("-").isdigit()
    df = pd.read_csv(path, header=0 if has_header else None)
    if has_header:
        df.columns = [c.strip() for c in df.columns]
    else:
        df.columns = KLINE_COLS[: df.shape[1]]
    return df


def _to_utc(ms: pd.Series) -> pd.DatetimeIndex:
    v = ms.astype("int64").to_numpy()
    # Binance moved some archives to microseconds; detect per value.
    v = np.where(v > 10**14, v // 1000, v)
    return pd.DatetimeIndex(pd.to_datetime(v, unit="ms", utc=True))


def clean_klines(sym: str) -> dict:
    # monthly first, then daily, so a daily file overrides a monthly one for the same minute
    files = sorted((RAW / "klines_1m" / sym).glob("*.zip"), key=lambda f: (f.stem.count("-") > 3, f.name))
    if not files:
        raise FileNotFoundError(f"no raw klines for {sym}")
    parts = []
    for i, f in enumerate(files):
        d = _read_zip(f)
        d["_file"] = i
        parts.append(d)
    raw = pd.concat(parts, ignore_index=True)
    raw.index = _to_utc(raw["open_time"])
    raw.index.name = "ts"
    raw = raw[KEEP + ["_file"]].astype({c: "float64" for c in KEEP})

    stats: dict = {"symbol": sym, "raw_files": len(files), "raw_rows": int(len(raw))}

    dup_mask = raw.index.duplicated(keep=False)
    stats["dup_rows"] = int(dup_mask.sum())
    stats["dup_timestamps"] = int(raw.index[dup_mask].nunique())
    if dup_mask.any():
        dups = raw[dup_mask]
        n_conflict = dups.groupby(level=0)[KEEP].nunique().gt(1).any(axis=1).sum()
        stats["dup_conflicting_timestamps"] = int(n_conflict)
    else:
        stats["dup_conflicting_timestamps"] = 0
    raw = raw.sort_values("_file", kind="stable")
    raw = raw[~raw.index.duplicated(keep="last")].sort_index()

    raw, repair_stats = repair_frozen_minutes(sym, raw)
    stats.update(repair_stats)

    bad_price = (raw[["open", "high", "low", "close"]] <= 0).any(axis=1)
    stats["dropped_nonpositive_price"] = int(bad_price.sum())
    stats["dropped_nonpositive_price_ts"] = [str(t) for t in raw.index[bad_price][:50]]
    raw = raw[~bad_price]

    hi = raw[["open", "close"]].max(axis=1)
    lo = raw[["open", "close"]].min(axis=1)
    bad_hl = (raw["high"] < hi) | (raw["low"] > lo) | (raw["high"] < raw["low"])
    stats["fixed_ohlc_inconsistent"] = int(bad_hl.sum())
    stats["fixed_ohlc_inconsistent_ts"] = [str(t) for t in raw.index[bad_hl][:50]]
    raw["high"] = np.maximum(raw["high"], hi)
    raw["low"] = np.minimum(raw["low"], lo)

    out = raw[KEEP]
    stats["clean_rows"] = int(len(out))
    stats["first"] = str(out.index[0])
    stats["last"] = str(out.index[-1])

    (CLEAN / "1m").mkdir(parents=True, exist_ok=True)
    out.to_parquet(CLEAN / "1m" / f"{sym}.parquet")
    (CLEAN / "1m" / f"{sym}_stats.json").write_text(json.dumps(stats, indent=2))
    return stats


def clean_funding(sym: str) -> dict:
    files = sorted((RAW / "funding" / sym).glob("*.zip"))
    parts = [pd.read_csv(f) for f in files]
    df = pd.concat(parts, ignore_index=True)
    df.columns = [c.strip() for c in df.columns]
    df.index = _to_utc(df["calc_time"])
    df.index.name = "ts"
    n_raw = len(df)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    out = pd.DataFrame(
        {"funding_rate": df["last_funding_rate"].astype("float64"),
         "interval_hours": df["funding_interval_hours"].astype("float64")},
        index=df.index,
    )
    (CLEAN / "funding").mkdir(parents=True, exist_ok=True)
    out.to_parquet(CLEAN / "funding" / f"{sym}.parquet")
    return {"symbol": sym, "raw_files": len(files), "raw_rows": n_raw, "clean_rows": len(out)}


def main(symbols: list[str]) -> None:
    for sym in symbols:
        s = clean_klines(sym)
        f = clean_funding(sym)
        print(f"{sym}: klines rows={s['clean_rows']} dups={s['dup_timestamps']} "
              f"conflicting={s['dup_conflicting_timestamps']} fixed_ohlc={s['fixed_ohlc_inconsistent']} "
              f"dropped={s['dropped_nonpositive_price']} | funding rows={f['clean_rows']}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or SYMBOLS)
