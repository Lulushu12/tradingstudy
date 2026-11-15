"""Download Binance USDT-M perpetual 1m klines and funding rates from data.binance.vision.

Raw zips are stored untouched under data/raw and verified against Binance's published SHA256 CHECKSUM files.
Re-running skips files that already exist and verify. Missing months (before listing) return 404 and are skipped.

Usage: uv run python -m tradingstudy.data.download [SYMBOL ...]
"""
from __future__ import annotations

import hashlib
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from tradingstudy.config import DOWNLOAD_DATE, RAW, SYMBOLS, pair

BASE = "https://data.binance.vision/data/futures/um"
FIRST_MONTH = pd.Timestamp("2019-09-01")


def _get(url: str, retries: int = 4) -> bytes | None:
    """GET url. Returns None on 404. Retries other errors with backoff."""
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            err = e
        time.sleep(2**attempt)
    raise RuntimeError(f"failed after {retries} retries: {url}: {err}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str, dest: Path) -> str:
    """Download url to dest with checksum verification. Returns 'ok', 'cached', 'missing'."""
    ck_path = dest.with_suffix(dest.suffix + ".CHECKSUM")
    if dest.exists() and ck_path.exists():
        if ck_path.read_text().split()[0] == _sha256(dest):
            return "cached"
    ck = _get(url + ".CHECKSUM")
    if ck is None:
        return "missing"
    body = _get(url)
    if body is None:
        return "missing"
    expected = ck.decode().split()[0]
    got = hashlib.sha256(body).hexdigest()
    if got != expected:
        raise RuntimeError(f"checksum mismatch for {url}: {got} != {expected}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    ck_path.write_bytes(ck)
    return "ok"


def jobs_for(sym: str) -> list[tuple[str, Path]]:
    p = pair(sym)
    last_full_month = (DOWNLOAD_DATE.tz_localize(None).to_period("M") - 1).to_timestamp()
    months = pd.date_range(FIRST_MONTH, last_full_month, freq="MS")
    days = pd.date_range(last_full_month + pd.offsets.MonthBegin(1), DOWNLOAD_DATE.tz_localize(None) - pd.Timedelta(days=1), freq="D")
    jobs = []
    for m in months:
        tag = m.strftime("%Y-%m")
        jobs.append((f"{BASE}/monthly/klines/{p}/1m/{p}-1m-{tag}.zip", RAW / "klines_1m" / sym / f"{p}-1m-{tag}.zip"))
        jobs.append((f"{BASE}/monthly/fundingRate/{p}/{p}-fundingRate-{tag}.zip", RAW / "funding" / sym / f"{p}-fundingRate-{tag}.zip"))
    for d in days:
        tag = d.strftime("%Y-%m-%d")
        jobs.append((f"{BASE}/daily/klines/{p}/1m/{p}-1m-{tag}.zip", RAW / "klines_1m" / sym / f"{p}-1m-{tag}.zip"))
    return jobs


def main(symbols: list[str]) -> None:
    for sym in symbols:
        jobs = jobs_for(sym)
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda j: fetch(*j), jobs))
        counts = pd.Series(results).value_counts().to_dict()
        print(f"{sym}: {counts}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or SYMBOLS)
