"""Fetch daily OHLCV for a NASDAQ-100 universe, plus NQ futures intraday.

SURVIVORSHIP BIAS WARNING, stated up front because it governs how the results
must be read: this uses the CURRENT Nasdaq-100 membership over history. Names
that were in the index and later failed or were removed are absent. For a
long-only test that bias is fatal. For a cross-sectional LONG/SHORT test it is
much weaker - you rank within whatever universe exists each day and trade the
spread - but it is not zero, because surviving names had systematically better
outcomes. Treated as an upper bound throughout, never as a clean result.
"""
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "equity")

# Current Nasdaq-100 membership (2026). See bias warning above.
NDX = """AAPL MSFT NVDA AMZN META GOOGL GOOG AVGO TSLA COST NFLX AMD PEP ADBE
CSCO TMUS INTC CMCSA TXN QCOM AMGN HON INTU AMAT BKNG ISRG SBUX ADI GILD ADP
VRTX REGN MDLZ PYPL LRCX MU PANW SNPS CDNS MELI KLAC MAR ORLY CSX ABNB FTNT
NXPI ADSK CHTR MNST PCAR PAYX AEP KDP ROST ODFL EXC CTAS MCHP IDXX FAST BIIB
DXCM EA VRSK CTSH CSGP GEHC ANSS ZS DDOG TEAM ON CDW WBD TTD ILMN WDAY MRNA
LULU BKR FANG CCEP ROP AZN LIN PDD ARM SMCI GFS CEG TTWO MDB CRWD DASH ALGN
SIRI JD ATVI SGEN""".split()

YF = "https://query1.finance.yahoo.com/v8/finance/chart/{}"


def _get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(1.5 * (i + 1))
    return None


def fetch(symbol, interval="1d", period1=0, period2=None, rng=None):
    period2 = period2 or int(time.time())
    q = (f"?period1={period1}&period2={period2}&interval={interval}"
         if rng is None else f"?range={rng}&interval={interval}")
    raw = _get(YF.format(symbol.replace("=", "%3D")) + q)
    if raw is None:
        return None
    try:
        d = json.loads(raw)["chart"]["result"][0]
    except Exception:
        return None
    ts = d.get("timestamp")
    if not ts:
        return None
    q0 = d["indicators"]["quote"][0]
    df = pd.DataFrame({
        "dt": pd.to_datetime(ts, unit="s", utc=True),
        "open": q0.get("open"), "high": q0.get("high"), "low": q0.get("low"),
        "close": q0.get("close"), "volume": q0.get("volume"),
    })
    adj = d["indicators"].get("adjclose")
    df["adjclose"] = adj[0]["adjclose"] if adj else df["close"]
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    df["symbol"] = symbol
    return df


def build_universe(symbols=None, out_name="ndx_daily.parquet", workers=6):
    symbols = symbols or NDX
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        parts = list(ex.map(lambda s: fetch(s, "1d"), symbols))
    got = [p for p in parts if p is not None and len(p) > 250]
    missing = [s for s, p in zip(symbols, parts) if p is None or len(p) < 250]
    df = pd.concat(got, ignore_index=True).sort_values(["dt", "symbol"])
    path = os.path.join(OUT, out_name)
    df.to_parquet(path, index=False, compression="zstd")
    print(f"universe: {df.symbol.nunique()} symbols, {len(df):,} rows, "
          f"{df.dt.min().date()} -> {df.dt.max().date()}")
    if missing:
        print(f"  missing/short: {missing}")
    return df


def build_futures(out_name="nq_1h.parquet"):
    os.makedirs(OUT, exist_ok=True)
    df = fetch("NQ=F", "1h", rng="730d")
    if df is None:
        print("NQ 1h fetch failed")
        return None
    df = df[df["volume"].fillna(0) > 0].reset_index(drop=True)
    path = os.path.join(OUT, out_name)
    df.to_parquet(path, index=False, compression="zstd")
    print(f"NQ=F 1h: {len(df):,} bars {df.dt.min()} -> {df.dt.max()}")
    return df


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "eq"):
        build_universe()
    if what in ("all", "fut"):
        build_futures()
