"""Stage K: measure ACTUAL memecoins, not Binance-listed alts.

Honest limitation stated up front: public APIs only index pools that still exist and are
still active. A truly survivorship-free memecoin cohort is not buildable this way. So this
sample is deliberately biased IN FAVOUR of the lottery thesis -- it is the WINNERS: the
top DEX memecoins by current volume, the ones that did not die quietly.

The question this can still answer decisively: among the coins that WON, what did a buyer
who was not first actually get? If the survivors are bad for a normal buyer, the full
population (survivors + the dead ones we cannot see) is worse.
"""
import json, subprocess, time
import numpy as np, pandas as pd

GT = "https://api.geckoterminal.com/api/v2"
STABLE = {"USDC","USDT","SOL","WETH","ETH","WBTC","DAI","USD1","WBNB","BNB","CBBTC","USDS"}

def get(url, tries=4):
    """curl, not urllib -- the environment proxies HTTPS through a CA bundle that
    urllib does not pick up automatically."""
    for k in range(tries):
        try:
            out = subprocess.run(
                ["curl", "-s", "-m", "45", "-H",
                 "Accept: application/json;version=20230302", url],
                capture_output=True, text=True, timeout=60)
            if out.returncode == 0 and out.stdout.strip():
                return json.loads(out.stdout)
        except Exception:
            pass
        time.sleep(2*(k+1))
    return None

def pools(network, pages=10):
    out = []
    for pg in range(1, pages+1):
        d = get(f"{GT}/networks/{network}/pools?page={pg}")
        if not d or "data" not in d: break
        for x in d["data"]:
            a = x["attributes"]
            name = a.get("name","")
            base = name.split("/")[0].strip()
            if base.upper() in STABLE: continue          # not a memecoin
            out.append(dict(network=network, addr=a["address"], name=name, base=base,
                            created=a.get("pool_created_at"),
                            fdv=float(a.get("fdv_usd") or 0),
                            vol=float((a.get("volume_usd") or {}).get("h24") or 0),
                            reserve=float(a.get("reserve_in_usd") or 0)))
        time.sleep(2.2)
    return out

def ohlcv(network, addr, tf="day", limit=1000):
    d = get(f"{GT}/networks/{network}/pools/{addr}/ohlcv/{tf}?limit={limit}&currency=usd")
    if not d: return None
    try:
        rows = d["data"]["attributes"]["ohlcv_list"]
    except Exception:
        return None
    if not rows: return None
    df = pd.DataFrame(rows, columns=["ts","open","high","low","close","volume"])
    return df.sort_values("ts").reset_index(drop=True)

if __name__ == "__main__":
    allp = []
    for net, pg in [("solana", 10), ("base", 6), ("bsc", 4)]:
        got = pools(net, pg); allp += got
        print(f"{net}: {len(got)} memecoin-ish pools")
    P = pd.DataFrame(allp).drop_duplicates("addr")
    P["created"] = pd.to_datetime(P["created"], utc=True, errors="coerce")
    P = P.dropna(subset=["created"])
    print(f"\ntotal {len(P)} pools; median FDV ${P.fdv.median()/1e6:.1f}M, "
          f"median 24h vol ${P.vol.median()/1e3:.0f}k")
    P.to_parquet("meme_pools.parquet")

    recs = []; SERIES = []
    for i, r in enumerate(P.itertuples()):
        df = ohlcv(r.network, r.addr)
        time.sleep(2.2)
        if df is None or len(df) < 10: continue
        c = df["close"].to_numpy(float); h = df["high"].to_numpy(float)
        if not np.isfinite(c).all() or c[0] <= 0: continue
        peak_i = int(np.argmax(h))
        SERIES.append(c.tolist())
        recs.append(dict(name=r.name, network=r.network, bars=len(c),
                         first=c[0], last=c[-1], peak=h.max(),
                         days_to_peak=peak_i,
                         mult_from_first=c[-1]/c[0],
                         peak_from_first=h.max()/c[0],
                         dd_from_peak=c[-1]/h.max()-1,
                         age_days=(pd.Timestamp.utcnow()-r.created).days))
        if i % 25 == 0: print(f"  {i}/{len(P)}", flush=True)
    R = pd.DataFrame(recs)
    R.to_parquet("meme_paths.parquet")
    print(f"\nresolved {len(R)} memecoin price paths\n")

    print("="*96)
    print("K1. THE WINNERS' OWN CHARTS  (top DEX memecoins by current volume)")
    print("="*96)
    print(f"  median age {R.age_days.median():.0f} days, median history {R.bars.median():.0f} daily bars")
    print(f"  median drawdown from their own peak: {R.dd_from_peak.median():.1%}")
    print(f"  share currently >50% below their peak: {(R.dd_from_peak < -0.5).mean():.1%}")
    print(f"  share currently >80% below their peak: {(R.dd_from_peak < -0.8).mean():.1%}")
    print(f"  share currently >90% below their peak: {(R.dd_from_peak < -0.9).mean():.1%}")
    print(f"  median days from start of data to peak: {R.days_to_peak.median():.0f}")

    print("\n" + "="*96)
    print("K2. WHAT A BUYER WHO WAS NOT FIRST ACTUALLY GOT")
    print("="*96)
    print("  buying at the earliest price we can observe and holding to today:")
    print(f"    mean {R.mult_from_first.mean():.2f}x   median {R.mult_from_first.median():.2f}x   "
          f"P(>1x) {(R.mult_from_first>1).mean():.1%}   P(>10x) {(R.mult_from_first>10).mean():.1%}")
    print("\n  NOTE: even this flatters the buyer -- these are the survivors, and the")
    print("  observable window already starts after launch.")

    print("\n" + "="*96)
    print("K3. THE EXIT RULES FROM STAGE H, APPLIED TO REAL MEMECOINS")
    print("="*96)
    from h_lottery import apply_rule
    np.save("meme_closes.npy", np.array(SERIES, dtype=object), allow_pickle=True)
    print(f"{'rule':<34} {'mean':>8} {'median':>8} {'P(>1x)':>8} {'P(>2x)':>8} {'P(>10x)':>9}")
    print("-"*80)
    RULES = [("hold to today","hold",{}), ("take profit 2x","tp",dict(X=2)),
             ("take profit 5x","tp",dict(X=5)),
             ("trailing stop 30% off peak","trail",dict(d=0.30)),
             ("trailing stop 50% off peak","trail",dict(d=0.50)),
             ("trailing stop 70% off peak","trail",dict(d=0.70)),
             ("free ride: bank @2x, trail 50%","free_ride",dict(X=2.0,d=0.50))]
    for lab, rule, kw in RULES:
        ms = []
        for c in SERIES:
            if len(c) < 10 or c[0] <= 0: continue
            mu, _ = apply_rule(np.asarray(c, dtype=float), rule, **kw)
            if np.isfinite(mu) and mu >= 0: ms.append(mu)
        ms = np.array(ms)
        print(f"{lab:<34} {ms.mean():>7.2f}x {np.median(ms):>7.2f}x {(ms>1).mean():>7.1%} "
              f"{(ms>2).mean():>7.1%} {(ms>10).mean():>8.1%}")

    print("\n  Reminder: every number above is measured on SURVIVORS ONLY, with no DEX fee,")
    print("  no slippage, no MEV and no rug losses charged. The true population is worse.")
