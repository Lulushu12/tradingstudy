"""Stage F: resolve every trade on the TRUE 15-minute price path.

Removes the last big modelling assumption. For each 4h signal we now walk the 15m bars:
  - stop and target checked in true chronological order (no same-bar ambiguity)
  - stop fills at the WORSE of the stop price and the 15m bar's close (residual squeeze cost)
This is the same standard study/STRATEGY_FINDINGS.md used for BTC.
"""
import glob, io, os, re, zipfile
import numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor

COLS = ["open_time","open","high","low","close","volume","close_time",
        "quote_volume","count","taker_buy_volume","taker_buy_quote_volume","ignore"]

def load15(sym):
    fs = sorted(glob.glob(f"m15/{sym}-15m-*.zip"))
    out = []
    for path in fs:
        try:
            z = zipfile.ZipFile(path); raw = z.read(z.namelist()[0]).decode()
        except Exception:
            continue
        if not raw.strip(): continue
        hdr = 0 if raw.split("\n",1)[0].startswith("open_time") else None
        try:
            df = pd.read_csv(io.StringIO(raw), header=hdr, names=None if hdr==0 else COLS,
                             usecols=[0,1,2,3,4])
        except Exception:
            continue
        df.columns = ["open_time","open","high","low","close"]
        out.append(df)
    if not out: return None
    d = pd.concat(out, ignore_index=True)
    for c in d.columns: d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna()
    ot = d["open_time"].astype("int64")
    d["open_time"] = np.where(ot > 5_000_000_000_000, ot//1000, ot)
    return d.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)

def resolve_symbol(args):
    sym, trades = args
    d = load15(sym)
    if d is None or len(d) == 0:
        return []
    ts = d["open_time"].to_numpy()
    h = d["high"].to_numpy(); l = d["low"].to_numpy(); c = d["close"].to_numpy()
    o = d["open"].to_numpy()
    res = []
    for tr in trades:
        # entry at the 15m bar whose open_time == the 4h entry bar open_time
        i0 = np.searchsorted(ts, tr["entry_ms"])
        if i0 >= len(ts) or ts[i0] != tr["entry_ms"]:
            continue
        s = tr["side"]
        entry = o[i0] * (1 + s*tr["slip"])
        rdist = tr["rdist"]
        sdf = rdist/entry
        if sdf < 0.002: continue
        stop = entry - s*rdist; tgt = entry + s*2.0*rdist
        end = min(i0 + 500*16, len(ts))
        R = None
        for j in range(i0, end):
            hs = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            ht = (h[j] >= tgt) if s > 0 else (l[j] <= tgt)
            if hs and ht:                       # same 15m bar: assume stop first
                fill = min(stop, c[j]) if s > 0 else max(stop, c[j])
                R = s*(fill-entry)/rdist; xi = j; break
            if hs:
                fill = min(stop, c[j]) if s > 0 else max(stop, c[j])
                R = s*(fill-entry)/rdist; xi = j; break
            if ht:
                R = 2.0; xi = j; break
        if R is None:
            xi = end-1; R = s*(c[xi]-entry)/rdist
        res.append(dict(symbol=sym, side=s, gross_R=R, sdf=sdf,
                        entry_ms=tr["entry_ms"], exit_ms=int(ts[xi])))
    return res

if __name__ == "__main__":
    t = pd.read_parquet("trades_pessimistic.parquet")
    t["entry_ms"] = ((t.entry_dt - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1ms")).astype("int64")
    t["rdist"] = t.sdf * 1.0   # placeholder, recomputed below
    # recover rdist in price terms: sdf = rdist/entry, and we need entry -> use 4h open
    p = pd.read_parquet("panel_4h.parquet")[["symbol","open_time","open"]]
    t = t.merge(p, left_on=["symbol","entry_ms"], right_on=["symbol","open_time"], how="left")
    t = t.dropna(subset=["open"])
    SLIP = 0.0005
    t["rdist"] = t.sdf * t["open"] * (1 + t.side*SLIP)

    jobs = []
    for sym, g in t.groupby("symbol"):
        jobs.append((sym, [dict(entry_ms=int(r.entry_ms), side=int(r.side),
                                rdist=float(r.rdist), slip=SLIP) for r in g.itertuples()]))
    print(f"resolving {len(t)} trades across {len(jobs)} symbols on the 15m path...")
    rows = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for i, r in enumerate(ex.map(resolve_symbol, jobs, chunksize=4)):
            rows += r
            if i % 100 == 0: print(" ", i, flush=True)
    r = pd.DataFrame(rows)
    r["entry_dt"] = pd.to_datetime(r.entry_ms, unit="ms", utc=True)
    r["exit_dt"] = pd.to_datetime(r.exit_ms, unit="ms", utc=True)
    r["fee_R"] = (0.0010 + 2*SLIP)/r.sdf
    fund = pd.read_parquet("funding.parquet")
    fmap = {s: g.set_index("dt")["rate"] for s, g in fund.groupby("symbol")}
    fr = []
    for _, x in r.iterrows():
        ser = fmap.get(x.symbol)
        if ser is None: fr.append(0.0); continue
        seg = ser.loc[(ser.index > x.entry_dt) & (ser.index <= x.exit_dt)]
        fr.append(seg.sum()*x.side/x.sdf)
    r["funding_R"] = fr
    r["netR"] = r.gross_R - r.fee_R - r.funding_R
    r.to_parquet("trades_15m_truth.parquet")
    print(r.shape)
