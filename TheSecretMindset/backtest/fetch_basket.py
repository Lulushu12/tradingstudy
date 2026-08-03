"""Fetch a basket of Binance USD-M perpetual daily klines from the official public archive.

Basket selection is a pre-committed availability rule, never a performance rule:

  include every USDT-quoted USD-M perpetual whose daily kline archive begins on or before
  2021-01, and keep it whether or not it is still listed today.

Keeping delisted symbols is the point. Selecting the coins that are still around in 2026 would
load the basket with survivors and quietly inflate every long-biased result.
"""
from __future__ import annotations

import io
import os
import re
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

BASE = "https://data.binance.vision/data/futures/um/monthly/klines"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "basket")
CUTOFF = "2021-01"          # archive must start on or before this month
INTERVAL = os.environ.get("INTERVAL", "1d")
SESSION = requests.Session()

COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trades", "taker_base", "taker_quote", "ignore"]


def _list(prefix: str, delimiter: str = "/") -> list[str]:
    out, marker = [], ""
    while True:
        url = f"{S3}?delimiter={delimiter}&prefix={prefix}&marker={marker}"
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        txt = r.text
        keys = re.findall(r"<Prefix>([^<]+)</Prefix>", txt)
        keys = [k for k in keys if k != prefix]
        files = re.findall(r"<Key>([^<]+)</Key>", txt)
        out.extend(keys + files)
        if "<IsTruncated>true</IsTruncated>" not in txt:
            break
        marker = (keys + files)[-1] if (keys or files) else ""
        if not marker:
            break
    return out


def all_symbols() -> list[str]:
    pre = _list("data/futures/um/monthly/klines/")
    syms = [p.rstrip("/").split("/")[-1] for p in pre]
    return [s for s in syms if s.endswith("USDT")]


def months_for(sym: str) -> list[str]:
    keys = _list(f"data/futures/um/monthly/klines/{sym}/{INTERVAL}/", delimiter="")
    return sorted({m for k in keys for m in re.findall(rf"-{INTERVAL}-(\d{{4}}-\d{{2}})\.zip$", k)})


def fetch_month(sym: str, month: str) -> pd.DataFrame | None:
    url = f"{BASE}/{sym}/{INTERVAL}/{sym}-{INTERVAL}-{month}.zip"
    for attempt in range(4):
        try:
            r = SESSION.get(url, timeout=90)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                name = z.namelist()[0]
                df = pd.read_csv(z.open(name), header=None, names=COLS)
            # newer archive files carry a header row; drop it if present
            df = df[pd.to_numeric(df["open_time"], errors="coerce").notna()]
            return df
        except Exception:
            if attempt == 3:
                return None
            time.sleep(2 ** attempt)
    return None


def build(sym: str, months: list[str]) -> tuple[str, int]:
    parts = []
    for m in months:
        d = fetch_month(sym, m)
        if d is not None and len(d):
            parts.append(d)
    if not parts:
        return sym, 0
    df = pd.concat(parts, ignore_index=True)
    for c in ["open_time", "open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open_time", "open", "high", "low", "close"])
    # archive timestamps are ms; some newer files use us
    ot = df["open_time"].astype("int64")
    unit = "us" if ot.max() > 10**15 else "ms"
    df["time"] = (ot // (10**6 if unit == "us" else 10**3)).astype("int64")
    df = df.drop_duplicates(subset="time").sort_values("time")
    out = df[["time", "open", "high", "low", "close", "volume"]]
    os.makedirs(OUT, exist_ok=True)
    out.to_csv(os.path.join(OUT, f"{sym}_{INTERVAL}.csv"), index=False)
    return sym, len(out)


def main():
    print("listing symbols ...", flush=True)
    syms = all_symbols()
    print(f"  {len(syms)} USDT-quoted UM perpetuals in the archive", flush=True)

    print(f"finding first available month per symbol (rule: <= {CUTOFF}) ...", flush=True)
    chosen: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(months_for, s): s for s in syms}
        for i, fu in enumerate(as_completed(futs), 1):
            s = futs[fu]
            try:
                ms = fu.result()
            except Exception:
                ms = []
            if ms and ms[0] <= CUTOFF:
                chosen[s] = ms
            if i % 100 == 0:
                print(f"  scanned {i}/{len(syms)}", flush=True)

    print(f"\nbasket: {len(chosen)} symbols meet the pre-committed availability rule")
    for s in sorted(chosen):
        print(f"  {s:16s} {chosen[s][0]} .. {chosen[s][-1]}  ({len(chosen[s])} months)")

    print("\ndownloading ...", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(build, s, m): s for s, m in chosen.items()}
        for fu in as_completed(futs):
            s, n = fu.result()
            done += 1
            print(f"  [{done}/{len(chosen)}] {s:16s} {n} bars", flush=True)


if __name__ == "__main__":
    sys.exit(main())
