"""Stage M (collector): snapshot the FULL DEX launch cohort as it happens.

Why this design: GeckoTerminal's ranked endpoints (top pools / trending) only show winners,
and new_pools is capped at 10 pages (~7 minutes of launches). So instead of trying to reach
back in time, we stand at the firehose and record EVERY new pool as it appears -- winners
and failures alike -- together with its launch-time attributes.

Those attributes ARE the candidate selection signals, observed at t~0:
  initial liquidity (reserve_in_usd), FDV, market cap, early buy/sell counts, early unique
  buyers vs sellers, early volume.
Forward returns get measured later from minute OHLCV, so the test is strictly causal.
"""
import json, subprocess, time, os
import pandas as pd

GT = "https://api.geckoterminal.com/api/v2"
NETS = ["solana", "base", "bsc", "eth"]
OUT = "launch_cohort.parquet"

def get(u, tries=3):
    for k in range(tries):
        try:
            o = subprocess.run(["curl","-s","-m","30","-H",
                                "Accept: application/json;version=20230302", u],
                               capture_output=True, text=True, timeout=40)
            if o.returncode == 0 and o.stdout.strip():
                return json.loads(o.stdout)
        except Exception:
            pass
        time.sleep(1.5*(k+1))
    return None

def flat(net, x, snap_ts):
    a = x["attributes"]
    tx = a.get("transactions") or {}
    def g(win, key):
        return float((tx.get(win) or {}).get(key) or 0)
    vol = a.get("volume_usd") or {}
    pc = a.get("price_change_percentage") or {}
    return dict(
        network=net, addr=a["address"], name=a.get("name",""),
        created=a.get("pool_created_at"), snap=snap_ts,
        fdv=float(a.get("fdv_usd") or 0),
        mcap=float(a.get("market_cap_usd") or 0),
        reserve=float(a.get("reserve_in_usd") or 0),
        price_usd=float(a.get("base_token_price_usd") or 0),
        vol_m5=float(vol.get("m5") or 0), vol_h1=float(vol.get("h1") or 0),
        vol_h24=float(vol.get("h24") or 0),
        buys_m5=g("m5","buys"), sells_m5=g("m5","sells"),
        buyers_m5=g("m5","buyers"), sellers_m5=g("m5","sellers"),
        buys_h1=g("h1","buys"), sells_h1=g("h1","sells"),
        buyers_h1=g("h1","buyers"), sellers_h1=g("h1","sellers"),
        pc_m5=float(pc.get("m5") or 0), pc_h1=float(pc.get("h1") or 0),
    )

if __name__ == "__main__":
    import sys
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
    seen = {}
    if os.path.exists(OUT):
        old = pd.read_parquet(OUT)
        for r in old.to_dict("records"):
            seen[r["addr"]] = r
        print(f"resuming with {len(seen)} pools already recorded")
    t_end = time.time() + minutes*60
    rounds = 0
    while time.time() < t_end:
        snap_ts = pd.Timestamp.now(tz="UTC").isoformat()
        new_this_round = 0
        for net in NETS:
            for pg in range(1, 11):
                d = get(f"{GT}/networks/{net}/new_pools?page={pg}")
                if not d or not d.get("data"):
                    break
                for x in d["data"]:
                    rec = flat(net, x, snap_ts)
                    if rec["addr"] not in seen:          # keep FIRST sighting only
                        seen[rec["addr"]] = rec
                        new_this_round += 1
                time.sleep(0.35)
        rounds += 1
        pd.DataFrame(list(seen.values())).to_parquet(OUT, index=False)
        print(f"round {rounds}: +{new_this_round} new, {len(seen)} total, "
              f"{(t_end-time.time())/60:.1f} min left", flush=True)
        time.sleep(20)
    df = pd.DataFrame(list(seen.values()))
    df.to_parquet(OUT, index=False)
    print(f"\nDONE: {len(df)} pools captured at launch")
    print(df.network.value_counts().to_dict())
