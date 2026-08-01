"""Fetch minute OHLCV for the DEX launch cohort, respecting GeckoTerminal rate limits."""
import json, subprocess, time
import pandas as pd

P = pd.read_parquet("fetch_set.parquet")

def get(u, tries=5):
    for k in range(tries):
        o = subprocess.run(["curl","-s","-m","30","-H",
                            "Accept: application/json;version=20230302", u],
                           capture_output=True, text=True)
        try:
            d = json.loads(o.stdout)
        except Exception:
            time.sleep(3); continue
        if isinstance(d, dict) and d.get("status", {}).get("error_code") == 429:
            time.sleep(8 + 4*k); continue
        return d
    return None

rows, no_data = [], 0
for i, r in enumerate(P.itertuples()):
    d = get(f"https://api.geckoterminal.com/api/v2/networks/{r.network}/pools/"
            f"{r.addr}/ohlcv/minute?limit=1000&currency=usd")
    try:
        ol = d["data"]["attributes"]["ohlcv_list"]
    except Exception:
        ol = None
    if ol and len(ol) >= 5:
        df = pd.DataFrame(ol, columns=["ts","o","h","l","c","v"]).sort_values("ts")
        rows.append(dict(addr=r.addr, network=r.network, ts=df.ts.tolist(),
                         c=df.c.tolist(), h=df.h.tolist(), v=df.v.tolist()))
    else:
        no_data += 1
    if i % 25 == 0:
        print(f"  {i}/{len(P)} -> {len(rows)} with data, {no_data} without", flush=True)
        pd.DataFrame(rows).to_parquet("dex_paths.parquet", index=False)
    time.sleep(2.3)

pd.DataFrame(rows).to_parquet("dex_paths.parquet", index=False)
print(f"DONE {len(rows)}/{len(P)} pools have a usable minute path "
      f"({no_data} traded but have no indexed OHLCV)")
