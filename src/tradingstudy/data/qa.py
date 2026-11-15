"""Phase 0 data QA. Writes reports/phase0/QA_REPORT.md plus CSVs of gaps and suspicious prints.

Holdout discipline: this module uses the "qa" scope (full history) but emits ONLY data-quality facts
(counts, timestamps, gap lengths, spike ratios). It never writes prices, returns or indicator values.
The TradingView cross-check compares prices and therefore runs on the dev scope only.

Usage: uv run python -m tradingstudy.data.qa
"""
from __future__ import annotations

import glob
import json

import numpy as np
import pandas as pd

from tradingstudy.config import CLEAN, DEV_END, DEV_START, REPORTS, ROOT, SYMBOLS, TIMEFRAMES
from tradingstudy.data.guard import clip_scope, load_bars, load_funding
from tradingstudy.data.resample import resample_1m

OUT = REPORTS / "phase0"
SPIKE_RATIO = 25.0  # wick excursion beyond both neighbouring closes, in units of the trailing 1-day median 1m range
SPIKE_MIN_PCT = 0.5  # and at least this % of price (filters normal wicks in very quiet markets)
PERIODS = {
    "secondary_holdout": (None, DEV_START),
    "dev": (DEV_START, DEV_END),
    "primary_holdout": (DEV_END, None),
}


def period_of(ts: pd.DatetimeIndex) -> np.ndarray:
    return np.where(ts < DEV_START, "secondary_holdout", np.where(ts < DEV_END, "dev", "primary_holdout"))


def slice_period(df: pd.DataFrame, name: str) -> pd.DataFrame:
    a, b = PERIODS[name]
    m = np.ones(len(df), bool)
    if a is not None:
        m &= df.index >= a
    if b is not None:
        m &= df.index < b
    return df.loc[m]


def gaps_1m(df: pd.DataFrame) -> pd.DataFrame:
    d = df.index.to_series().diff()
    g = d[d > pd.Timedelta(minutes=1)]
    out = pd.DataFrame({
        "gap_start": g.index - g + pd.Timedelta(minutes=1),
        "gap_end": g.index - pd.Timedelta(minutes=1),
        "missing_minutes": (g / pd.Timedelta(minutes=1)).astype(int) - 1,
    }).reset_index(drop=True)
    out["period"] = period_of(pd.DatetimeIndex(out["gap_start"]))
    return out


def spikes_1m(df: pd.DataFrame) -> pd.DataFrame:
    rng = df["high"] - df["low"]
    med = rng.rolling(1440, min_periods=60).median()
    pc, nc = df["close"].shift(1), df["close"].shift(-1)
    up = df["high"] - np.maximum(pc, nc)
    dn = np.minimum(pc, nc) - df["low"]
    exc = np.maximum(up, dn)
    ratio = (exc / med).replace([np.inf, -np.inf], np.nan)
    pct = exc / df["close"] * 100
    flag = (ratio > SPIKE_RATIO) & (pct > SPIKE_MIN_PCT)
    out = pd.DataFrame({"ts": ratio.index[flag], "excursion_x_median_range": ratio[flag].round(1).to_numpy(),
                        "excursion_pct_of_price": pct[flag].round(2).to_numpy()})
    out["period"] = period_of(pd.DatetimeIndex(out["ts"]))
    return out


def qa_symbol(sym: str) -> dict:
    m1 = load_bars(sym, "1m", "qa")
    stats = json.loads((CLEAN / "1m" / f"{sym}_stats.json").read_text())
    gaps = gaps_1m(m1)
    spikes = spikes_1m(m1)
    gaps.to_csv(OUT / "gaps" / f"{sym}_1m_gaps.csv", index=False)
    spikes.to_csv(OUT / "spikes" / f"{sym}_1m_spikes.csv", index=False)

    res = {"symbol": sym, "clean": stats, "periods": {}, "tf": {}}
    for p in PERIODS:
        d = slice_period(m1, p)
        if d.empty:
            res["periods"][p] = None
            continue
        g = gaps[gaps.period == p]
        expected = int((d.index[-1] - d.index[0]) / pd.Timedelta(minutes=1)) + 1
        res["periods"][p] = {
            "first": str(d.index[0]), "last": str(d.index[-1]), "bars": len(d), "expected": expected,
            "missing_minutes": int(g.missing_minutes.sum()), "gap_count": len(g),
            "gaps_over_60m": int((g.missing_minutes > 60).sum()),
            "longest_gap_min": int(g.missing_minutes.max()) if len(g) else 0,
            "longest_gap_start": str(g.loc[g.missing_minutes.idxmax(), "gap_start"]) if len(g) else "",
            "zero_volume_bars": int((d["volume"] == 0).sum()),
            "spikes": int((spikes.period == p).sum()),
        }
    for tf in TIMEFRAMES:
        b = load_bars(sym, tf, "qa")
        res["tf"][tf] = {}
        for p in PERIODS:
            d = slice_period(b, p)
            res["tf"][tf][p] = {"bars": len(d), "incomplete": int((~d["complete"]).sum()),
                                "zero_volume": int((d["volume"] == 0).sum())}
    f = load_funding(sym, "qa")
    fr = {}
    for p in PERIODS:
        d = slice_period(f, p)
        if d.empty:
            fr[p] = None
            continue
        step_h = d.index.to_series().diff().dt.total_seconds() / 3600
        late = step_h > d["interval_hours"].shift(1) * 1.5
        fr[p] = {"count": len(d), "first": str(d.index[0]), "last": str(d.index[-1]),
                 "intervals_h": {str(int(k)): int(v) for k, v in d["interval_hours"].value_counts().items()},
                 "missed_prints": int(late.sum()),
                 "abs_rate_over_0.3pct": int((d["funding_rate"].abs() > 0.003).sum())}
    res["funding"] = fr
    return res


# ---------------- TradingView cross-check (dev scope only) ----------------
TV_SOURCES = {
    ("BTC", "5m", 5): ["5m/New Folder/*.csv", "New export/5m/**/*.csv"],
    ("BTC", "15m", 15): ["15/*.csv", "New export/15m/*.csv"],
    ("BTC", "1h", 60): ["1h/*.csv"],
    ("BTC", "4h", 240): ["BINANCE_BTCUSDT.P, 240.csv"],
    ("BTC", "1D", 1440): ["BINANCE_BTCUSDT.P, 1D.csv"],
    ("BTC", "1W", 10080): ["BINANCE_BTCUSDT.P, 1W.csv"],
    ("XRP", "15m", 15): ["HA SHA MFI/*.csv"],
}


def load_tv(patterns: list[str]) -> pd.DataFrame:
    files = [f for p in patterns for f in glob.glob(str(ROOT / p), recursive=True)]
    cols = lambda c: c in {"time", "open", "high", "low", "close", "Volume"}
    df = pd.concat([pd.read_csv(f, usecols=cols) for f in files], ignore_index=True)
    df = df.drop_duplicates("time", keep="last")
    df.index = pd.to_datetime(df.pop("time").astype("int64"), unit="s", utc=True)
    return df.sort_index().rename(columns={"Volume": "volume"})


def tv_crosscheck() -> list[dict]:
    rows = []
    for (sym, tf, minutes), pats in TV_SOURCES.items():
        tv = clip_scope(load_tv(pats), tf, "dev")
        if tf in TIMEFRAMES:
            bn = load_bars(sym, tf, "dev")
        else:
            bn = clip_scope(resample_1m(load_bars(sym, "1m", "dev"), minutes), tf, "dev")
        bn = bn[bn["complete"]]
        j = tv.merge(bn, how="inner", left_index=True, right_index=True, suffixes=("_tv", "_bn"))
        r = {"symbol": sym, "tf": tf, "tv_bars_dev": len(tv), "matched": len(j),
             "tv_bars_without_complete_binance_bar": len(tv) - len(j),
             "tv_first": str(tv.index.min()), "tv_last": str(tv.index.max())}
        for c in ["open", "high", "low", "close"]:
            rel = (j[f"{c}_tv"] - j[f"{c}_bn"]).abs() / j[f"{c}_bn"]
            r[f"{c}_exact_pct"] = round(100 * (rel < 1e-9).mean(), 3)
            r[f"{c}_max_rel_diff"] = float(rel.max())
        if "volume_tv" in j:
            vr = j["volume_tv"] / j["volume_bn"]
            r["volume_within_0.1pct"] = round(100 * ((vr - 1).abs() < 1e-3).mean(), 2)
            r["volume_ratio_median"] = round(float(vr.median()), 4)
        rows.append(r)
    return rows


# ---------------- report ----------------
def fmt_period_table(results: list[dict]) -> str:
    lines = ["| Coin | Period | First | Last | Bars | Missing min | Gaps | Gaps >60m | Longest gap (min, start) | Zero-vol bars | Spikes |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        for p, s in r["periods"].items():
            if s is None:
                lines.append(f"| {r['symbol']} | {p} | no data | | | | | | | | |")
                continue
            lines.append(f"| {r['symbol']} | {p} | {s['first'][:16]} | {s['last'][:16]} | {s['bars']:,} | {s['missing_minutes']:,} "
                         f"| {s['gap_count']} | {s['gaps_over_60m']} | {s['longest_gap_min']:,} ({s['longest_gap_start'][:16]}) "
                         f"| {s['zero_volume_bars']:,} | {s['spikes']} |")
    return "\n".join(lines)


def build_report(results: list[dict], tv: list[dict]) -> str:
    md = ["# Phase 0 Data QA Report", "",
          "Generated by `uv run python -m tradingstudy.data.qa`. Source: data.binance.vision USDT-M perpetual 1m klines "
          "and funding rate archives. All other timeframes are resampled from 1m (UTC-midnight anchored, weeks start Monday).",
          "", f"Provisional periods: secondary holdout before {DEV_START.date()}, dev {DEV_START.date()} to {DEV_END.date()} "
          "(exclusive), primary holdout from that date. Holdout rows show data-quality facts only, no prices.", "",
          "## 1m coverage and quality", "", fmt_period_table(results), "",
          "## Cleaning actions (whole history)", "",
          "| Coin | Raw files | Raw rows | Duplicate timestamps | Conflicting duplicates | OHLC fixed | Rows dropped (price <= 0) |",
          "|---|---|---|---|---|---|---|"]
    for r in results:
        c = r["clean"]
        md.append(f"| {r['symbol']} | {c['raw_files']} | {c['raw_rows']:,} | {c['dup_timestamps']} | {c['dup_conflicting_timestamps']} "
                  f"| {c['fixed_ohlc_inconsistent']} | {c['dropped_nonpositive_price']} |")
    md += ["", "## Frozen-minute repair (Binance kline archive defect, rebuilt from aggTrades)", "",
           "| Coin | Frozen minutes found | Rebuilt from trades | Dropped (no trades) | Left unrepaired | Days | Worst validation OHLC match | Median volume ratio |",
           "|---|---|---|---|---|---|---|---|"]
    for r in results:
        c = r["clean"]
        days = c.get("repair_days", [])
        matches = [d["ohlc_match"] for d in days if d.get("ohlc_match") is not None]
        vols = [d["volume_ratio_median"] for d in days if d.get("volume_ratio_median") == d.get("volume_ratio_median") and d.get("volume_ratio_median") is not None]
        md.append(f"| {r['symbol']} | {c.get('frozen_minutes', 0):,} | {c.get('frozen_rebuilt', 0):,} | {c.get('frozen_dropped_no_trades', 0):,} "
                  f"| {c.get('frozen_left_unvalidated', 0):,} | {len(days)} | {min(matches) if matches else 'n/a'} "
                  f"| {round(float(np.median(vols)), 4) if vols else 'n/a'} |")
    md += ["", "## Resampled timeframes: incomplete bars (bars with at least one missing 1m bar)", "",
           "| Coin | TF | " + " | ".join(f"{p} bars / incomplete" for p in PERIODS) + " |",
           "|---|---|" + "---|" * len(PERIODS)]
    for r in results:
        for tf, per in r["tf"].items():
            cells = [f"{v['bars']:,} / {v['incomplete']}" for v in per.values()]
            md.append(f"| {r['symbol']} | {tf} | " + " | ".join(cells) + " |")
    md += ["", "## Funding rates", "",
           "| Coin | Period | Prints | First | Last | Interval hours (count) | Missed prints | abs(rate) > 0.3% |",
           "|---|---|---|---|---|---|---|---|"]
    for r in results:
        for p, s in r["funding"].items():
            if s is None:
                md.append(f"| {r['symbol']} | {p} | 0 | | | | | |")
                continue
            md.append(f"| {r['symbol']} | {p} | {s['count']:,} | {s['first'][:16]} | {s['last'][:16]} | {s['intervals_h']} "
                      f"| {s['missed_prints']} | {s['abs_rate_over_0.3pct']} |")
    md += ["", "## TradingView export vs Binance (dev period only, complete Binance bars)", "",
           "| Coin | TF | TV bars in dev | Matched | Open exact % | High exact % | Low exact % | Close exact % | Max rel diff (close) | Volume within 0.1% | Volume ratio median |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in tv:
        md.append(f"| {t['symbol']} | {t['tf']} | {t['tv_bars_dev']:,} | {t['matched']:,} | {t['open_exact_pct']} | {t['high_exact_pct']} "
                  f"| {t['low_exact_pct']} | {t['close_exact_pct']} | {t['close_max_rel_diff']:.2e} | {t.get('volume_within_0.1pct', 'n/a')} "
                  f"| {t.get('volume_ratio_median', 'n/a')} |")
    md += ["", f"Spike definition: 1m wick excursion beyond both neighbouring closes greater than {SPIKE_RATIO:g}x the trailing "
           f"1-day median 1m range AND greater than {SPIKE_MIN_PCT:g}% of price. Spikes are listed for review, not removed (real liquidation wicks are real fills). "
           "Per-coin lists: `reports/phase0/spikes/`. Gap lists: `reports/phase0/gaps/`."]
    return "\n".join(md) + "\n"


def main() -> None:
    (OUT / "gaps").mkdir(parents=True, exist_ok=True)
    (OUT / "spikes").mkdir(parents=True, exist_ok=True)
    results = []
    for sym in SYMBOLS:
        results.append(qa_symbol(sym))
        print(f"QA {sym} done", flush=True)
    tv = tv_crosscheck()
    (OUT / "qa_results.json").write_text(json.dumps({"symbols": results, "tv": tv}, indent=2, default=str))
    (OUT / "QA_REPORT.md").write_text(build_report(results, tv))
    print("wrote", OUT / "QA_REPORT.md")


if __name__ == "__main__":
    main()
