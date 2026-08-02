"""Fetch the non-OHLCV data: funding rate and the open-interest metrics series.

Everything tested so far is derived from open/high/low/close/volume, and every
edge found landed in a +3 to +6 winrate point band. If that band is a ceiling on
what an OHLCV bar knows about a liquid perp, then breaking it needs information
that is not in the bar. Funding, open interest, and the taker/top-trader
long-short ratios are the cheapest such information available.

  fundingRate: monthly archives, 8-hourly settlements. Cheap, all symbols.
  metrics:     daily archives only, 5-minute granularity, carries
               sum_open_interest, top-trader long/short ratios, and the taker
               long/short volume ratio. Expensive (about 1900 files per symbol),
               so restricted to a few instruments as a probe.

Writes study/lowrr/flow/<SYM>_funding.parquet and <SYM>_metrics.parquet
"""
import os, sys, io, zipfile, time
import urllib.request
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "flow")
os.makedirs(OUT, exist_ok=True)

BASE = "https://data.binance.vision/data/futures/um"
ALL = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT",
       "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "BCHUSDT"]
METRIC_SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

def grab(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            return pd.read_csv(z.open(z.namelist()[0]))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if k == tries - 1:
                return None
            time.sleep(1.5 * (k + 1))
        except Exception:
            if k == tries - 1:
                return None
            time.sleep(1.5 * (k + 1))

def funding(sym, start="2021-01", end="2026-07"):
    frames = []
    for d in pd.date_range(start, end, freq="MS"):
        ym = d.strftime("%Y-%m")
        x = grab(f"{BASE}/monthly/fundingRate/{sym}/{sym}-fundingRate-{ym}.zip")
        if x is not None and len(x):
            frames.append(x)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["time"] = pd.to_numeric(df["calc_time"], errors="coerce") // 1000
    df["funding"] = pd.to_numeric(df["last_funding_rate"], errors="coerce")
    df = df.dropna(subset=["time", "funding"]).drop_duplicates("time")
    df = df.sort_values("time").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df[["time", "dt", "funding"]]

def metrics(sym, start="2021-01-01", end="2026-07-31"):
    frames = []
    n_miss = 0
    for d in pd.date_range(start, end, freq="D"):
        ds = d.strftime("%Y-%m-%d")
        x = grab(f"{BASE}/daily/metrics/{sym}/{sym}-metrics-{ds}.zip")
        if x is None or len(x) == 0:
            n_miss += 1
            continue
        frames.append(x)
    if not frames:
        return None, n_miss
    df = pd.concat(frames, ignore_index=True)
    df["dt"] = pd.to_datetime(df["create_time"], utc=True, errors="coerce")
    df["time"] = df["dt"].astype("int64") // 10**9
    for c in ["sum_open_interest", "sum_open_interest_value",
              "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
              "count_long_short_ratio", "sum_taker_long_short_vol_ratio"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["time"]).drop_duplicates("time")
    df = df.sort_values("time").reset_index(drop=True)
    keep = ["time", "dt", "sum_open_interest", "sum_open_interest_value",
            "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
            "count_long_short_ratio", "sum_taker_long_short_vol_ratio"]
    return df[keep], n_miss

def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "funding"
    if what == "funding":
        for s in ALL:
            p = os.path.join(OUT, f"{s}_funding.parquet")
            if os.path.exists(p):
                print("skip", s, flush=True); continue
            t0 = time.time()
            df = funding(s)
            if df is None:
                print(f"FAIL {s}", flush=True); continue
            df.to_parquet(p)
            print(f"{s:>10} funding {len(df):>7} rows "
                  f"{df['dt'].iloc[0].date()} -> {df['dt'].iloc[-1].date()} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    else:
        for s in METRIC_SYMS:
            p = os.path.join(OUT, f"{s}_metrics.parquet")
            if os.path.exists(p):
                print("skip", s, flush=True); continue
            t0 = time.time()
            df, miss = metrics(s)
            if df is None:
                print(f"FAIL {s}", flush=True); continue
            df.to_parquet(p)
            print(f"{s:>10} metrics {len(df):>8} rows "
                  f"{df['dt'].iloc[0].date()} -> {df['dt'].iloc[-1].date()} "
                  f"missing_days={miss} ({time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
