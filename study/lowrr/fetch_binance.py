"""Bulk-fetch Binance USDT-M perp klines from data.binance.vision.

The REST API returns 451 from this environment but the static monthly archive
does not. This is the same venue the existing BTC study data came from, so the
multi-asset extension stays on one consistent feed.

Writes study/lowrr/bn/<SYM>_<interval>.parquet
"""
import os, sys, io, zipfile, time
import urllib.request
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bn")
os.makedirs(OUT, exist_ok=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT",
           "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "BCHUSDT"]

BASE = "https://data.binance.vision/data/futures/um/monthly/klines"
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
        "qav", "trades", "tbb", "tbq", "ignore"]

def month_list(start, end):
    return [d.strftime("%Y-%m") for d in pd.date_range(start, end, freq="MS")]

def get_month(sym, interval, ym, tries=3):
    url = f"{BASE}/{sym}/{interval}/{sym}-{interval}-{ym}.zip"
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                buf = io.BytesIO(r.read())
            z = zipfile.ZipFile(buf)
            name = z.namelist()[0]
            df = pd.read_csv(z.open(name), header=None, names=COLS)
            # some months ship a header row
            if str(df["open_time"].iloc[0]).lower().startswith("open"):
                df = df.iloc[1:]
            return df
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))

def fetch(sym, interval, start="2021-01", end="2026-07"):
    frames = []
    for ym in month_list(start, end):
        d = get_month(sym, interval, ym)
        if d is not None:
            frames.append(d)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    for c in ["open_time", "open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open_time", "open", "high", "low", "close"])
    # binance switched open_time from ms to us in some 2025+ archives
    ot = df["open_time"].astype("int64")
    ot = ot.where(ot < 1e14, ot // 1000)
    df["time"] = (ot // 1000).astype("int64")
    df = df[["time", "open", "high", "low", "close", "volume"]]
    df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df

def main():
    intervals = sys.argv[1].split(",") if len(sys.argv) > 1 else ["4h", "15m"]
    syms = sys.argv[2].split(",") if len(sys.argv) > 2 else SYMBOLS
    for sym in syms:
        for iv in intervals:
            p = os.path.join(OUT, f"{sym}_{iv}.parquet")
            if os.path.exists(p):
                print("skip", p, flush=True); continue
            t0 = time.time()
            try:
                df = fetch(sym, iv)
            except Exception as e:
                print(f"FAIL {sym} {iv}: {e}", flush=True); continue
            if df is None or len(df) == 0:
                print(f"empty {sym} {iv}", flush=True); continue
            df.to_parquet(p)
            print(f"{sym:>10} {iv:>4} {len(df):>8} bars "
                  f"{df['dt'].iloc[0].date()} -> {df['dt'].iloc[-1].date()} "
                  f"({time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
