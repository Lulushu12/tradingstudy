"""Fetch OKX USDT-perp OHLCV so the frequency question can be answered honestly.

A high timeframe caps how many signals ONE instrument can produce. The only
legitimate way to raise frequency without dropping to a lower timeframe is to run
the same rule across more instruments. Breakout lists 100+ perps, so this is
available in practice.

OKX is used because Binance returns 451 from this environment. OKX perp history
starts around 2021-2022 for majors, which is enough overlap with the BTC study.

Writes study/lowrr/okx/<SYM>_<bar>.parquet
"""
import os, sys, time, json
import urllib.request
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "okx")
os.makedirs(OUT, exist_ok=True)

SYMBOLS = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP", "XRP-USDT-SWAP",
           "DOGE-USDT-SWAP", "BNB-USDT-SWAP", "ADA-USDT-SWAP", "LINK-USDT-SWAP",
           "AVAX-USDT-SWAP", "LTC-USDT-SWAP", "DOT-USDT-SWAP", "BCH-USDT-SWAP"]

BASE = "https://www.okx.com/api/v5/market/history-candles"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126 Safari/537.36")

def get(url, tries=5):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(1.5 * (k + 1))

def fetch(inst, bar, start_ms, limit=100, sleep=0.12):
    """Page backwards from now to start_ms using the `after` cursor."""
    rows = []
    after = None
    while True:
        url = f"{BASE}?instId={inst}&bar={bar}&limit={limit}"
        if after is not None:
            url += f"&after={after}"
        d = get(url)
        data = d.get("data", [])
        if not data:
            break
        rows.extend(data)
        oldest = int(data[-1][0])
        after = oldest
        if oldest <= start_ms:
            break
        time.sleep(sleep)
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=["ts", "o", "h", "l", "c", "vol", "volCcy",
                                     "volCcyQuote", "confirm"])
    df = df[df["confirm"] == "1"]
    df["time"] = (df["ts"].astype("int64") // 1000)
    for a, b in [("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"),
                 ("volCcy", "volume")]:
        df[b] = pd.to_numeric(df[a], errors="coerce")
    df = df[["time", "open", "high", "low", "close", "volume"]]
    df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df = df[df["time"] >= start_ms // 1000].reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df

def main():
    bars = sys.argv[1].split(",") if len(sys.argv) > 1 else ["4H", "15m"]
    start_ms = int(pd.Timestamp("2021-05-24", tz="UTC").timestamp() * 1000)
    for sym in SYMBOLS:
        for bar in bars:
            path = os.path.join(OUT, f"{sym.split('-')[0]}_{bar}.parquet")
            if os.path.exists(path):
                print("skip", path); continue
            t0 = time.time()
            try:
                df = fetch(sym, bar, start_ms)
            except Exception as e:
                print(f"FAIL {sym} {bar}: {e}"); continue
            if df is None or len(df) == 0:
                print(f"empty {sym} {bar}"); continue
            df.to_parquet(path)
            print(f"{sym:>16} {bar:>4} {len(df):>7} bars "
                  f"{df['dt'].iloc[0].date()} -> {df['dt'].iloc[-1].date()} "
                  f"({time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
