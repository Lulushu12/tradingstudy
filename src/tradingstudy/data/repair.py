"""Repair Binance kline archive defects.

Two defects found in Phase 0 QA:
1. Whole days missing from monthly kline archives (e.g. SOL/XRP 2022-02-26..28). Fix: download the daily kline
   archive for those days (clean.py then merges it, daily overriding monthly).
2. "Frozen" minutes: zero volume with open == high == low == close, while TradingView shows real trading at the same
   time (e.g. BTC 2023-11-10 15:00-16:30 UTC). Fix: rebuild those minutes from the aggTrades daily archive.
   A frozen minute with no trades in aggTrades is dropped and becomes a gap.

Each repaired day is validated: bars rebuilt from aggTrades are compared with the kline archive on that day's
NORMAL (non-frozen) minutes. If they do not match, the rebuild is not trustworthy and the day is left as gaps.

Usage: uv run python -m tradingstudy.data.repair [SYMBOL ...]   (downloads what is needed, then re-run clean)
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from tradingstudy.config import CLEAN, RAW, SYMBOLS, pair

BASE = "https://data.binance.vision/data/futures/um/daily"
AGG_COLS = ["agg_trade_id", "price", "quantity", "first_trade_id", "last_trade_id", "transact_time", "is_buyer_maker"]
VALIDATION_MIN_MATCH = 0.99  # share of normal minutes whose OHLC must agree within VALIDATION_RTOL
VALIDATION_RTOL = 5e-4  # 0.05%. Kline archives include a few trades aggTrades omits, so 1-6 tick differences occur


def frozen_mask(df: pd.DataFrame) -> pd.Series:
    return (df["volume"] == 0) & (df["open"] == df["high"]) & (df["high"] == df["low"]) & (df["low"] == df["close"])


def read_aggtrades(path) -> pd.DataFrame:
    first = pd.read_csv(path, header=None, nrows=1)
    has_header = not str(first.iloc[0, 0]).strip().isdigit()
    df = pd.read_csv(path, header=0 if has_header else None)
    df.columns = AGG_COLS if not has_header else [c.strip() for c in df.columns]
    t = df["transact_time"].astype("int64").to_numpy()
    t = np.where(t > 10**14, t // 1000, t)
    df.index = pd.DatetimeIndex(pd.to_datetime(t, unit="ms", utc=True))
    df["is_buyer_maker"] = df["is_buyer_maker"].astype(str).str.lower().eq("true")
    return df.sort_index(kind="stable")


def bars_from_aggtrades(agg: pd.DataFrame) -> pd.DataFrame:
    minute = agg.index.floor("1min")
    px, qty = agg["price"].astype("float64"), agg["quantity"].astype("float64")
    taker_buy = ~agg["is_buyer_maker"]
    g = pd.DataFrame({
        "price": px.to_numpy(), "qty": qty.to_numpy(), "quote": (px * qty).to_numpy(),
        "n": (agg["last_trade_id"] - agg["first_trade_id"] + 1).to_numpy(),
        "tb_qty": np.where(taker_buy, qty, 0.0), "tb_quote": np.where(taker_buy, px * qty, 0.0),
    }, index=minute).groupby(level=0)
    out = pd.DataFrame({
        "open": g["price"].first(), "high": g["price"].max(), "low": g["price"].min(), "close": g["price"].last(),
        "volume": g["qty"].sum(), "quote_volume": g["quote"].sum(), "count": g["n"].sum().astype("float64"),
        "taker_buy_volume": g["tb_qty"].sum(), "taker_buy_quote_volume": g["tb_quote"].sum(),
    })
    out.index.name = "ts"
    return out


def repair_frozen_minutes(sym: str, raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """raw: deduplicated 1m frame (may contain helper columns). Returns repaired frame and stats."""
    fz = frozen_mask(raw)
    stats = {"frozen_minutes": int(fz.sum()), "frozen_rebuilt": 0, "frozen_dropped_no_trades": 0,
             "frozen_left_unvalidated": 0, "repair_days": []}
    if not fz.any():
        return raw, stats
    raw = raw.copy()
    drop = []
    for day, idx in raw.index[fz].to_series().groupby(raw.index[fz].date):
        path = RAW / "aggtrades" / sym / f"{pair(sym)}-aggTrades-{day}.zip"
        if not path.exists():
            stats["frozen_left_unvalidated"] += len(idx)
            stats["repair_days"].append({"day": str(day), "frozen": len(idx), "status": "no aggTrades file"})
            continue
        rebuilt = bars_from_aggtrades(read_aggtrades(path))
        normal = raw.loc[str(day)].loc[lambda d: ~frozen_mask(d)]
        common = normal.index.intersection(rebuilt.index)
        cols = ["open", "high", "low", "close"]
        a, b = normal.loc[common, cols].to_numpy(), rebuilt.loc[common, cols].to_numpy()
        match = np.isclose(a, b, rtol=VALIDATION_RTOL, atol=0).all(axis=1).mean() if len(common) else np.nan
        exact = np.isclose(a, b, rtol=0, atol=1e-12).all(axis=1).mean() if len(common) else np.nan
        vol_ratio = float((rebuilt.loc[common, "volume"] / normal.loc[common, "volume"]).median()) if len(common) else np.nan
        rec = {"day": str(day), "frozen": len(idx), "validation_minutes": len(common),
               "ohlc_match": None if np.isnan(match) else round(float(match), 4),
               "ohlc_exact": None if np.isnan(exact) else round(float(exact), 4), "volume_ratio_median": vol_ratio}
        if len(common) and match < VALIDATION_MIN_MATCH:
            rec["status"] = "validation failed, frozen minutes dropped"
            drop.extend(idx.index)
            stats["frozen_left_unvalidated"] += len(idx)
            stats["repair_days"].append(rec)
            continue
        have = idx.index.intersection(rebuilt.index)
        missing = idx.index.difference(rebuilt.index)
        for c in rebuilt.columns:
            raw.loc[have, c] = rebuilt.loc[have, c].to_numpy()
        drop.extend(missing)
        stats["frozen_rebuilt"] += len(have)
        stats["frozen_dropped_no_trades"] += len(missing)
        rec.update(status="rebuilt", rebuilt=len(have), dropped_no_trades=len(missing))
        stats["repair_days"].append(rec)
    raw = raw.drop(index=drop)
    return raw, stats


# ---------------- downloading what the repair needs ----------------
def days_needing_repair(sym: str) -> tuple[list, list]:
    m = pd.read_parquet(CLEAN / "1m" / f"{sym}.parquet")
    # whole or partial days missing from the series (between first and last day)
    full = pd.date_range(m.index[0].normalize(), m.index[-1].normalize(), freq="D")
    per_day = m.groupby(m.index.normalize()).size().reindex(full, fill_value=0)
    first_day, last_day = full[0], full[-1]
    gap_days = [d.date() for d, n in per_day.items() if n < 1440 and d not in (first_day, last_day)]
    frozen = m[frozen_mask(m)]
    frozen_days = sorted(set(frozen.index.date))
    return gap_days, frozen_days


def main(symbols: list[str]) -> None:
    from tradingstudy.data.download import fetch

    for sym in symbols:
        p = pair(sym)
        gap_days, frozen_days = days_needing_repair(sym)
        jobs = [(f"{BASE}/klines/{p}/1m/{p}-1m-{d}.zip", RAW / "klines_1m" / sym / f"{p}-1m-{d}.zip") for d in gap_days]
        jobs += [(f"{BASE}/aggTrades/{p}/{p}-aggTrades-{d}.zip", RAW / "aggtrades" / sym / f"{p}-aggTrades-{d}.zip")
                 for d in frozen_days]
        with ThreadPoolExecutor(max_workers=6) as ex:
            res = list(ex.map(lambda j: fetch(*j), jobs))
        print(f"{sym}: gap days={len(gap_days)} frozen days={len(frozen_days)} downloads={pd.Series(res).value_counts().to_dict()}",
              flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or SYMBOLS)
