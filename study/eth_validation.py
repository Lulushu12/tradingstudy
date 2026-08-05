"""ETH data loader — BINANCE ETHUSDT perpetual 4h klines from data.binance.vision
monthly archives (2021-01 .. latest). Build data/eth_4H.parquet once; the zips are
cached outside the repo. Columns follow the Binance kline format; some months
carry a header row — handled. Times are bar OPEN times in ms (us from 2025-01 on
for some feeds — normalized by magnitude).
"""
import glob, os
import numpy as np
import pandas as pd

COLS = ["open_time", "open", "high", "low", "close", "volume",
        "close_time", "qvol", "trades", "tb_base", "tb_quote", "ignore"]

def load_eth_4h(zip_dir=None):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "eth_4H.parquet")
    if os.path.exists(out):
        return pd.read_parquet(out)
    frames = []
    for f in sorted(glob.glob(os.path.join(zip_dir, "ETHUSDT-4h-*.zip"))):
        d = pd.read_csv(f, header=None, names=COLS)
        if isinstance(d.iloc[0]["open_time"], str) and not str(d.iloc[0]["open_time"]).isdigit():
            d = d.iloc[1:]
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    for c in ["open_time", "open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open_time", "open", "high", "low", "close"])
    # normalize open_time to seconds regardless of ms/us units
    t = df["open_time"].values.astype("int64")
    t = np.where(t > 10**17, t // 10**6, np.where(t > 10**14, t // 10**3, t))  # us/ms
    t = np.where(t > 10**11, t // 10**3, t)                                     # ms leftover
    df["time"] = t
    df = (df.drop_duplicates(subset="time", keep="last")
            .sort_values("time").reset_index(drop=True))
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    r = df[["time", "dt", "open", "high", "low", "close", "volume"]].copy()
    gaps = int((r["time"].diff() > 14400).sum())
    print(f"ETH 4H: {len(r)} bars  {r['dt'].iloc[0]} -> {r['dt'].iloc[-1]}  gaps={gaps}")
    r.to_parquet(out)
    return r

if __name__ == "__main__":
    import sys
    load_eth_4h(sys.argv[1])
