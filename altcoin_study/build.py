"""Consolidate Binance UM-futures 4h monthly kline zips into one panel parquet."""
import glob, io, os, re, zipfile
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

COLS = ["open_time","open","high","low","close","volume","close_time",
        "quote_volume","count","taker_buy_volume","taker_buy_quote_volume","ignore"]
PAT = re.compile(r"^(.*)-4h-(\d{4})-(\d{2})\.zip$")

def one(path):
    m = PAT.match(os.path.basename(path))
    sym = m.group(1)
    try:
        z = zipfile.ZipFile(path)
        raw = z.read(z.namelist()[0]).decode()
    except Exception:
        return None
    if not raw.strip():
        return None
    # some months carry a header row, some don't
    first = raw.split("\n", 1)[0]
    hdr = 0 if first.startswith("open_time") else None
    try:
        df = pd.read_csv(io.StringIO(raw), header=hdr, names=None if hdr == 0 else COLS)
    except Exception:
        return None
    df = df[["open_time","open","high","low","close","volume","quote_volume","count"]].copy()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open_time","close"])
    # open_time is ms for most, us for the newest months
    ot = df["open_time"].astype("int64")
    ot = np.where(ot > 5_000_000_000_000, ot // 1000, ot)
    df["open_time"] = ot
    df["symbol"] = sym
    return df

if __name__ == "__main__":
    files = sorted(glob.glob("zips/*.zip"))
    print("files:", len(files))
    out = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for i, r in enumerate(ex.map(one, files, chunksize=64)):
            if r is not None:
                out.append(r)
            if i % 4000 == 0:
                print(" ", i, flush=True)
    panel = pd.concat(out, ignore_index=True)
    panel = panel.drop_duplicates(subset=["symbol","open_time"]).sort_values(["symbol","open_time"])
    panel["dt"] = pd.to_datetime(panel["open_time"], unit="ms", utc=True)
    panel = panel[panel["dt"] >= "2019-09-01"]
    panel.to_parquet("panel_4h.parquet", index=False)
    print(panel.shape, panel["symbol"].nunique(),
          panel["dt"].min(), panel["dt"].max())
