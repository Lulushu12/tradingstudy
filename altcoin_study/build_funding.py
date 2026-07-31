import glob, io, os, re, zipfile
import numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor

PAT = re.compile(r"^(.*)-fundingRate-(\d{4})-(\d{2})\.zip$")

def one(path):
    sym = PAT.match(os.path.basename(path)).group(1)
    try:
        z = zipfile.ZipFile(path); raw = z.read(z.namelist()[0]).decode()
    except Exception:
        return None
    if not raw.strip():
        return None
    first = raw.split("\n", 1)[0]
    hdr = 0 if not first[:1].isdigit() else None
    try:
        df = pd.read_csv(io.StringIO(raw), header=hdr,
                         names=None if hdr == 0 else ["calc_time","funding_interval_hours","last_funding_rate"])
    except Exception:
        return None
    df.columns = [c.strip().lower() for c in df.columns]
    tcol = [c for c in df.columns if "time" in c][0]
    rcol = [c for c in df.columns if "rate" in c][0]
    out = pd.DataFrame({"open_time": pd.to_numeric(df[tcol], errors="coerce"),
                        "rate": pd.to_numeric(df[rcol], errors="coerce")}).dropna()
    ot = out["open_time"].astype("int64")
    out["open_time"] = np.where(ot > 5_000_000_000_000, ot // 1000, ot)
    out["symbol"] = sym
    return out

if __name__ == "__main__":
    files = sorted(glob.glob("fzips/*.zip"))
    out = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for r in ex.map(one, files, chunksize=64):
            if r is not None: out.append(r)
    f = pd.concat(out, ignore_index=True).drop_duplicates(["symbol","open_time"])
    f["dt"] = pd.to_datetime(f["open_time"], unit="ms", utc=True)
    f = f.sort_values(["symbol","dt"])
    f.to_parquet("funding.parquet", index=False)
    print(f.shape, f.symbol.nunique(), f.dt.min(), f.dt.max())
    # sanity: annualised funding, cross-sectional
    ann = f.groupby("symbol")["rate"].mean() * 3 * 365
    print("median annualised funding across symbols: %.2f%%" % (ann.median()*100))
    print("share of symbols with POSITIVE mean funding (longs pay shorts): %.1f%%"
          % ((ann > 0).mean()*100))
