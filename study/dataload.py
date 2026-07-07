"""Load and clean OHLCV per timeframe from the chunked TradingView CSVs.

We recompute ALL indicators ourselves (causally), so we only trust the raw
OHLCV+volume columns from the exports. Exported indicator columns are ignored.
"""
import glob, os, sys
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # "Trading Study"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)

# timeframe -> (glob patterns, expected bar seconds)
SOURCES = {
    "1D":  (["BINANCE_BTCUSDT.P, 1D.csv"], 86400),
    "4H":  (["BINANCE_BTCUSDT.P, 240.csv"], 14400),
    "1h":  (["1h/*.csv"], 3600),
    "15m": (["15/*.csv", "New export/15m/*.csv"], 900),
    "5m":  (["5m/New Folder/*.csv", "New export/5m/**/*.csv"], 300),
    "1m":  (["New export/1m/*.csv"], 60),
}

USE = ["time", "open", "high", "low", "close", "Volume"]

def load_tf(patterns, bar_sec):
    frames = []
    files = []
    for p in patterns:
        files += glob.glob(os.path.join(BASE, p), recursive=True)
    for f in files:
        try:
            df = pd.read_csv(f, usecols=lambda c: c in USE)
        except Exception as e:
            print("  skip", f, e); continue
        frames.append(df)
    if not frames:
        return None, files
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={"Volume": "volume"})
    if "volume" not in df.columns:
        df["volume"] = np.nan
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["time"] = pd.to_numeric(df["time"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["time", "open", "high", "low", "close"])
    df = df.drop_duplicates(subset="time", keep="last").sort_values("time").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df, files

def gap_report(df, bar_sec):
    d = df["time"].diff().dropna()
    n_gap = int((d > bar_sec).sum())
    # largest gaps
    big = d[d > bar_sec].sort_values(ascending=False).head(5)
    return n_gap, big

def main():
    summary = []
    for tf, (patterns, bar_sec) in SOURCES.items():
        df, files = load_tf(patterns, bar_sec)
        if df is None:
            print(f"{tf}: NO DATA"); continue
        n_gap, big = gap_report(df, bar_sec)
        out = os.path.join(OUT, f"{tf}.parquet")
        df.to_parquet(out)
        print(f"{tf}: {len(df):>7} bars  {df['dt'].iloc[0]} -> {df['dt'].iloc[-1]}  "
              f"files={len(files)}  gaps>{bar_sec}s={n_gap}")
        summary.append((tf, len(df)))
    print("\nSaved parquet to", OUT)

if __name__ == "__main__":
    main()
