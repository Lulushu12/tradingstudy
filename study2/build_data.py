"""Parse raw data.binance.vision zips -> clean parquet per symbol.

Outputs in study2/data/:
  klines_{SYM}_{IVAL}.parquet : dt(utc), open, high, low, close, volume,
                                quote_vol, count, taker_buy_vol, taker_buy_quote_vol
  funding_{SYM}.parquet       : dt, funding_rate
  premium_{SYM}.parquet       : dt, p_open, p_high, p_low, p_close   (premium index, 1h)
  metrics_{SYM}.parquet       : dt, oi, oi_value, top_lsr_acct, top_lsr_pos,
                                glob_lsr, taker_vol_ratio             (5-min grid)

Robust to: header vs no-header CSVs, ms vs us timestamps, duplicate rows.
"""
import os, glob, io, zipfile, sys
import pandas as pd
import numpy as np

RAW = os.environ.get("RAW_DIR", "/tmp/claude-0/-home-user-tradingstudy/c58a4def-5f69-52ae-b6f0-034e819fb5d1/scratchpad/raw")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)
SYMS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "LINKUSDT", "DOTUSDT"]

def read_zip_csv(path, names):
    """Read the single CSV inside a zip; drop a header row if present."""
    try:
        with zipfile.ZipFile(path) as z:
            with z.open(z.namelist()[0]) as f:
                raw = f.read()
    except Exception as e:
        print("  bad zip", path, e)
        return None
    df = pd.read_csv(io.BytesIO(raw), header=None, names=names, low_memory=False)
    # header row detection: first cell non-numeric
    if len(df) and not str(df.iloc[0, 0]).replace(".", "").replace("-", "").isdigit():
        df = df.iloc[1:]
    return df

def to_dt(ts):
    """Timestamps arrive in ms (~1.6e12) or us (~1.6e15). Normalize to utc dt."""
    ts = pd.to_numeric(ts, errors="coerce")
    us = ts > 1e14
    out = pd.Series(pd.NaT, index=ts.index, dtype="datetime64[ns, UTC]")
    out[us] = pd.to_datetime(ts[us], unit="us", utc=True)
    out[~us] = pd.to_datetime(ts[~us], unit="ms", utc=True)
    return out

KCOLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
         "quote_vol", "count", "taker_buy_vol", "taker_buy_quote_vol", "ignore"]

def build_klines(sym, ival):
    files = sorted(glob.glob(f"{RAW}/klines/{sym}/{ival}/*.zip"))
    if not files:
        print(f"klines {sym} {ival}: no files"); return
    parts = []
    for f in files:
        df = read_zip_csv(f, KCOLS)
        if df is not None:
            parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    df["dt"] = to_dt(df["open_time"])
    for c in ["open", "high", "low", "close", "volume", "quote_vol", "count",
              "taker_buy_vol", "taker_buy_quote_vol"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = (df.dropna(subset=["dt", "open", "high", "low", "close"])
            .drop_duplicates("dt").sort_values("dt").reset_index(drop=True))
    keep = ["dt", "open", "high", "low", "close", "volume", "quote_vol", "count",
            "taker_buy_vol", "taker_buy_quote_vol"]
    df[keep].to_parquet(f"{OUT}/klines_{sym}_{ival}.parquet")
    print(f"klines {sym} {ival}: {len(df)} bars {df.dt.iloc[0].date()} -> {df.dt.iloc[-1].date()}")

def build_funding(sym):
    files = sorted(glob.glob(f"{RAW}/fundingRate/{sym}/*.zip"))
    if not files:
        print(f"funding {sym}: no files"); return
    parts = []
    for f in files:
        df = read_zip_csv(f, ["calc_time", "funding_interval_hours", "funding_rate"])
        if df is not None:
            parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    df["dt"] = to_dt(df["calc_time"])
    df["funding_rate"] = pd.to_numeric(df["funding_rate"], errors="coerce")
    df = (df.dropna(subset=["dt", "funding_rate"]).drop_duplicates("dt")
            .sort_values("dt").reset_index(drop=True))
    df[["dt", "funding_rate"]].to_parquet(f"{OUT}/funding_{sym}.parquet")
    print(f"funding {sym}: {len(df)} rows {df.dt.iloc[0].date()} -> {df.dt.iloc[-1].date()}")

def build_premium(sym):
    files = sorted(glob.glob(f"{RAW}/premiumIndexKlines/{sym}/*.zip"))
    if not files:
        print(f"premium {sym}: no files"); return
    parts = []
    for f in files:
        df = read_zip_csv(f, KCOLS)
        if df is not None:
            parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    df["dt"] = to_dt(df["open_time"])
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = (df.dropna(subset=["dt"]).drop_duplicates("dt")
            .sort_values("dt").reset_index(drop=True))
    df = df.rename(columns={"open": "p_open", "high": "p_high",
                            "low": "p_low", "close": "p_close"})
    df[["dt", "p_open", "p_high", "p_low", "p_close"]].to_parquet(f"{OUT}/premium_{sym}.parquet")
    print(f"premium {sym}: {len(df)} bars {df.dt.iloc[0].date()} -> {df.dt.iloc[-1].date()}")

MCOLS = ["create_time", "symbol", "oi", "oi_value", "top_lsr_acct",
         "top_lsr_pos", "glob_lsr", "taker_vol_ratio"]

def build_metrics(sym):
    files = sorted(glob.glob(f"{RAW}/metrics/{sym}/*.zip"))
    if not files:
        print(f"metrics {sym}: no files"); return
    parts = []
    for f in files:
        df = read_zip_csv(f, MCOLS)
        if df is not None:
            parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    # create_time in these files is a datetime string, not epoch
    df["dt"] = pd.to_datetime(df["create_time"], errors="coerce", utc=True, format="mixed")
    for c in ["oi", "oi_value", "top_lsr_acct", "top_lsr_pos", "glob_lsr", "taker_vol_ratio"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = (df.dropna(subset=["dt"]).drop_duplicates("dt")
            .sort_values("dt").reset_index(drop=True))
    df[["dt", "oi", "oi_value", "top_lsr_acct", "top_lsr_pos", "glob_lsr",
        "taker_vol_ratio"]].to_parquet(f"{OUT}/metrics_{sym}.parquet")
    print(f"metrics {sym}: {len(df)} rows {df.dt.iloc[0].date()} -> {df.dt.iloc[-1].date()}")

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for sym in SYMS:
        if only and only != sym:
            continue
        for ival in ["5m", "15m", "1h", "4h"]:
            build_klines(sym, ival)
        build_funding(sym)
        build_premium(sym)
        build_metrics(sym)
