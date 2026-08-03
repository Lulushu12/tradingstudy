"""Fetch 4H OHLCV for non-BTC perps from OKX, for cross-asset replication.

Why OKX and not Binance: the Binance and Bybit REST endpoints are geo-blocked from
this environment. OKX is a different venue from the Binance data the strategy was
developed on, which is a feed difference to state, not hide. Prices differ slightly,
volume definitions differ, and listing dates differ per instrument.

Writes data/alt_<SYM>.parquet with the same schema as data/4H.parquet so
indicators.enrich and the frozen backtest run unmodified.
"""
import os, sys, time, json, urllib.request
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BAR = "4H"
BAR_SEC = 14400
SYMBOLS = ["ETH-USDT-SWAP", "SOL-USDT-SWAP", "XRP-USDT-SWAP", "DOGE-USDT-SWAP",
           "BNB-USDT-SWAP", "LTC-USDT-SWAP", "ADA-USDT-SWAP", "LINK-USDT-SWAP"]
START_MS = 1609459200000        # 2021-01-01, same start as the BTC study
BASE = "https://www.okx.com/api/v5/market/history-candles"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def fetch(inst):
    """Page backwards from now using `after` (returns candles older than the cursor)."""
    rows, cursor = [], None
    while True:
        url = f"{BASE}?instId={inst}&bar={BAR}&limit=100"
        if cursor is not None:
            url += f"&after={cursor}"
        d = get(url)
        if d.get("code") != "0":
            print(f"  {inst}: api error {d.get('code')} {d.get('msg')}")
            break
        batch = d.get("data", [])
        if not batch:
            break
        rows += batch
        cursor = int(batch[-1][0])
        if cursor <= START_MS:
            break
        time.sleep(0.15)
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close",
                                     "vol", "volCcy", "volQuote", "confirm"])
    df = df[df["confirm"] == "1"]                    # closed bars only
    df["time"] = (df["ts"].astype("int64") // 1000).astype("Int64")
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    df["volume"] = df["vol"].astype(float)
    df = df[["time", "open", "high", "low", "close", "volume"]]
    df = df[df["time"] >= START_MS // 1000]
    df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True).astype("datetime64[ms, UTC]")
    return df


def main():
    os.makedirs(OUT, exist_ok=True)
    syms = sys.argv[1:] or SYMBOLS
    for inst in syms:
        sym = inst.split("-")[0]
        df = fetch(inst)
        if df is None or len(df) < 500:
            print(f"  {sym}: insufficient data, skipped")
            continue
        gaps = (df["time"].diff().dropna() != BAR_SEC).sum()
        df.to_parquet(f"{OUT}/alt_{sym}.parquet", index=False)
        print(f"  {sym}: {len(df)} bars  {df['dt'].iloc[0].date()}..{df['dt'].iloc[-1].date()}"
              f"  gaps={gaps}")


if __name__ == "__main__":
    main()
