"""Stage L: the actual memecoin lifecycle, measured minute by minute.

Discovered in Stage K: the ENTIRE top of the DEX volume leaderboard on Solana/Base/BSC is
pools created within the last 24-48 hours. That churn IS the memecoin market. So the honest
way to measure "buy a random new shitcoin and let it run" is to take today's launches and
follow their minute-by-minute path.

Sampling bias, stated: these are the HIGHEST-VOLUME launches of the day -- the ones that got
attention. The launches nobody noticed are not in this sample. Bias runs in favour of the
lottery thesis, so any bad result here is a lower bound on how bad the real thing is.
"""
import json, subprocess, time
import numpy as np, pandas as pd

GT = "https://api.geckoterminal.com/api/v2"

def get(url, tries=3):
    for k in range(tries):
        try:
            o = subprocess.run(["curl","-s","-m","45","-H",
                                "Accept: application/json;version=20230302", url],
                               capture_output=True, text=True, timeout=60)
            if o.returncode == 0 and o.stdout.strip():
                return json.loads(o.stdout)
        except Exception:
            pass
        time.sleep(2*(k+1))
    return None

def minute_path(net, addr):
    d = get(f"{GT}/networks/{net}/pools/{addr}/ohlcv/minute?limit=1000&currency=usd&aggregate=1")
    try:
        rows = d["data"]["attributes"]["ohlcv_list"]
    except Exception:
        return None
    if not rows or len(rows) < 30: return None
    df = pd.DataFrame(rows, columns=["ts","open","high","low","close","volume"])
    return df.sort_values("ts").reset_index(drop=True)

if __name__ == "__main__":
    P = pd.read_parquet("meme_pools.parquet")
    P = P.drop_duplicates("addr")
    print(f"following {len(P)} freshly-launched, high-volume memecoin pools "
          f"(solana/base/bsc), minute bars\n")

    recs = []
    for i, r in enumerate(P.itertuples()):
        df = minute_path(r.network, r.addr)
        time.sleep(2.1)
        if df is None: continue
        c = df["close"].to_numpy(float); h = df["high"].to_numpy(float)
        v = df["volume"].to_numpy(float)
        if not np.isfinite(c).all() or c[0] <= 0: continue
        n = len(c)
        pk = int(np.argmax(h))
        rec = dict(name=r.name, net=r.network, mins=n,
                   peak_mult=h.max()/c[0], final_mult=c[-1]/c[0],
                   mins_to_peak=pk, dd_from_peak=c[-1]/h.max()-1,
                   vol_usd=float(np.nansum(v)))
        # what a buyer entering k minutes in would have made, holding to the end of data
        for k in [5, 15, 30, 60, 180]:
            rec[f"buy_at_{k}m"] = (c[-1]/c[k]) if n > k+5 and c[k] > 0 else np.nan
        # and holding just 1 hour from that entry
        for k in [5, 15, 30, 60]:
            rec[f"hold1h_from_{k}m"] = (c[min(k+60, n-1)]/c[k]) if n > k+5 and c[k] > 0 else np.nan
        recs.append(rec)
        if i % 25 == 0: print(f"  {i}/{len(P)}  ({len(recs)} resolved)", flush=True)

    R = pd.DataFrame(recs)
    R.to_parquet("meme_launch_paths.parquet")
    print(f"\nresolved {len(R)} launch paths "
          f"(median {R.mins.median():.0f} minutes of history)\n")

    print("="*96)
    print("L1. THE SHAPE OF A MEMECOIN LAUNCH")
    print("="*96)
    print(f"  median peak multiple from first observable price : {R.peak_mult.median():.2f}x")
    print(f"  median FINAL multiple                            : {R.final_mult.median():.2f}x")
    print(f"  median minutes from start to peak                : {R.mins_to_peak.median():.0f}")
    print(f"  median drawdown from peak                        : {R.dd_from_peak.median():.1%}")
    print(f"  share already >50% off peak                       : {(R.dd_from_peak<-0.5).mean():.1%}")
    print(f"  share already >80% off peak                       : {(R.dd_from_peak<-0.8).mean():.1%}")
    print(f"  share whose peak came in the first 60 minutes     : {(R.mins_to_peak<60).mean():.1%}")

    print("\n" + "="*96)
    print("L2. WHAT YOU GET IF YOU ARE NOT FIRST  (buy k minutes after launch, hold to now)")
    print("="*96)
    print(f"  {'entry':>10} {'mean':>8} {'median':>8} {'P(>1x)':>8} {'P(>2x)':>8} {'P(>10x)':>9}")
    for k in [5, 15, 30, 60, 180]:
        x = R[f"buy_at_{k}m"].dropna()
        if len(x) < 10: continue
        print(f"  {'+'+str(k)+'m':>10} {x.mean():>7.2f}x {x.median():>7.2f}x {(x>1).mean():>7.1%} "
              f"{(x>2).mean():>7.1%} {(x>10).mean():>8.1%}")

    print("\n  same entries but holding only ONE HOUR (the 'take and run' version):")
    print(f"  {'entry':>10} {'mean':>8} {'median':>8} {'P(>1x)':>8}")
    for k in [5, 15, 30, 60]:
        x = R[f"hold1h_from_{k}m"].dropna()
        if len(x) < 10: continue
        print(f"  {'+'+str(k)+'m':>10} {x.mean():>7.2f}x {x.median():>7.2f}x {(x>1).mean():>7.1%}")

    print("\n" + "="*96)
    print("L3. WITH REALISTIC DEX FRICTION")
    print("="*96)
    print("  A round trip on a fresh Solana memecoin: ~0.6-1% LP fee each way, priority fee,")
    print("  MEV sandwich on entry, and price impact both sides. 5-10% is optimistic.\n")
    base = R["buy_at_30m"].dropna()
    print(f"  {'round-trip cost':>16} {'mean':>8} {'median':>8} {'P(>1x)':>9}")
    for cost in [0.0, 0.02, 0.05, 0.10, 0.15]:
        x = base*(1-cost)
        print(f"  {cost:>15.0%} {x.mean():>7.2f}x {x.median():>7.2f}x {(x>1).mean():>8.1%}")
    print("\n  Reminder: this sample is the day's WINNERS by volume, with no rug losses")
    print("  and no failed launches included. The real distribution is worse than this.")
