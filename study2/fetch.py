"""Download historical UM-futures data from data.binance.vision.

Sources (all public archive, no API key, not geo-blocked):
  - monthly klines  {sym}/{ival}: OHLCV + quote_vol + count + taker_buy_vol
  - monthly fundingRate
  - monthly premiumIndexKlines 1h  (perp premium vs index = basis proxy)
  - daily   metrics (open interest, long/short ratios, taker vol ratio; ~2021-12 onward)

Raw zips land in RAW (scratchpad, disposable). Idempotent: skips files already
present. 404 = file doesn't exist for that period (pre-listing) -> recorded, skipped.
"""
import os, sys, calendar, concurrent.futures as cf, urllib.request, urllib.error, ssl, time

RAW = os.environ.get("RAW_DIR", "/tmp/claude-0/-home-user-tradingstudy/c58a4def-5f69-52ae-b6f0-034e819fb5d1/scratchpad/raw")
BASE = "https://data.binance.vision/data/futures/um"
SYMS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "LINKUSDT", "DOTUSDT"]
KLINE_IVALS = ["5m", "15m", "1h", "4h"]
MONTHS = [f"{y}-{m:02d}" for y in range(2020, 2027) for m in range(1, 13)
          if (y, m) <= (2026, 7)]
METRIC_DAYS = []
for y in range(2022, 2027):
    for m in range(1, 13):
        if (y, m) > (2026, 8):
            break
        for d in range(1, calendar.monthrange(y, m)[1] + 1):
            if (y, m, d) <= (2026, 8, 14):
                METRIC_DAYS.append(f"{y}-{m:02d}-{d:02d}")

ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")

def urls():
    for s in SYMS:
        for iv in KLINE_IVALS:
            for mo in MONTHS:
                yield (f"{BASE}/monthly/klines/{s}/{iv}/{s}-{iv}-{mo}.zip",
                       f"klines/{s}/{iv}/{s}-{iv}-{mo}.zip")
        for mo in MONTHS:
            yield (f"{BASE}/monthly/fundingRate/{s}/{s}-fundingRate-{mo}.zip",
                   f"fundingRate/{s}/{s}-fundingRate-{mo}.zip")
            yield (f"{BASE}/monthly/premiumIndexKlines/{s}/1h/{s}-1h-{mo}.zip",
                   f"premiumIndexKlines/{s}/{s}-1h-{mo}.zip")
        for day in METRIC_DAYS:
            yield (f"{BASE}/daily/metrics/{s}/{s}-metrics-{day}.zip",
                   f"metrics/{s}/{s}-metrics-{day}.zip")

def fetch(job):
    url, rel = job
    dest = os.path.join(RAW, rel)
    miss = dest + ".404"
    if os.path.exists(dest) or os.path.exists(miss):
        return "skip"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, context=ctx, timeout=60) as r:
                data = r.read()
            with open(dest + ".part", "wb") as f:
                f.write(data)
            os.rename(dest + ".part", dest)
            return "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                open(miss, "w").close()
                return "404"
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return "fail:" + url

def main():
    jobs = list(urls())
    print(f"{len(jobs)} candidate files", flush=True)
    counts = {}
    fails = []
    with cf.ThreadPoolExecutor(max_workers=24) as ex:
        for i, res in enumerate(ex.map(fetch, jobs)):
            key = res if not res.startswith("fail") else "fail"
            counts[key] = counts.get(key, 0) + 1
            if key == "fail":
                fails.append(res)
            if (i + 1) % 1000 == 0:
                print(f"  {i+1}/{len(jobs)} {counts}", flush=True)
    print("DONE", counts, flush=True)
    for f in fails[:20]:
        print(f, flush=True)

if __name__ == "__main__":
    main()
