"""Stage Q: launch selection signals on REAL DEX launches.

Sample: every new pool appearing on Solana/Base/Ethereum over a multi-hour window, captured
live at creation -- winners AND failures, which is what the ranked GeckoTerminal endpoints
cannot give you. Launch-time attributes were recorded at first sighting.

Causal design, same as Stage N:
  OBSERVE first OBS minutes -> PREDICT the return from OBS to OBS+HORIZON.
The signal never sees the return it is predicting.
"""
import json, subprocess, time, sys
import numpy as np, pandas as pd
from scipy import stats as st

GT = "https://api.geckoterminal.com/api/v2"
OBS = 30          # minutes of observation
HOR = 60          # minutes of forward return

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

def fetch_paths(P, out="dex_paths.parquet"):
    rows = []
    for i, r in enumerate(P.itertuples()):
        d = get(f"{GT}/networks/{r.network}/pools/{r.addr}/ohlcv/minute"
                f"?limit=1000&currency=usd&aggregate=1")
        try:
            ol = d["data"]["attributes"]["ohlcv_list"]
        except Exception:
            ol = None
        if ol and len(ol) >= 5:
            df = pd.DataFrame(ol, columns=["ts","o","h","l","c","v"]).sort_values("ts")
            rows.append(dict(addr=r.addr, network=r.network,
                             ts=df.ts.tolist(), c=df.c.tolist(),
                             h=df.h.tolist(), v=df.v.tolist()))
        if i % 50 == 0:
            print(f"  {i}/{len(P)} ({len(rows)} with data)", flush=True)
        time.sleep(0.4)
    pd.DataFrame(rows).to_parquet(out, index=False)
    return pd.DataFrame(rows)

def build(P, X):
    M = P.set_index("addr")
    recs = []
    for r in X.itertuples():
        ts = np.array(r.ts); c = np.array(r.c, dtype=float)
        h = np.array(r.h, dtype=float); v = np.array(r.v, dtype=float)
        if len(c) < OBS + 20 or not np.isfinite(c).all() or (c <= 0).any():
            continue
        # minute grid may have gaps; index by position (bars traded), which is itself
        # a signal (a pool with no trades has no bars)
        obs_c = c[:OBS]; obs_v = v[:OBS]
        i0 = OBS - 1
        j = min(i0 + HOR, len(c) - 1)
        if j <= i0: continue
        fwd = c[j]/c[i0]
        # trailing-stop version of the same forward window
        seg = c[i0:j+1]/c[i0]
        pk = np.maximum.accumulate(seg); stp = pk*0.30
        hit = np.argmax(seg <= stp) if (seg <= stp).any() else -1
        fwd_trail = stp[hit] if hit > 0 else seg[-1]

        a = M.loc[r.addr] if r.addr in M.index else None
        rets = np.diff(np.log(obs_c))
        rec = dict(addr=r.addr, network=r.network, fwd=fwd, fwd_trail=fwd_trail,
                   obs_ret=obs_c[-1]/obs_c[0], obs_peak=h[:OBS].max()/obs_c[0],
                   obs_dd=obs_c[-1]/h[:OBS].max(),
                   obs_vol=float(np.nansum(obs_v)),
                   obs_sigma=float(rets.std()) if len(rets) > 3 else np.nan,
                   bars_traded=int(np.isfinite(obs_v).sum()),
                   vol_accel=(obs_v[OBS//2:].sum()+1)/(obs_v[:OBS//2].sum()+1))
        if a is not None:
            rec.update(reserve=float(a.reserve), fdv=float(a.fdv),
                       buys_m5=float(a.buys_m5), sells_m5=float(a.sells_m5),
                       buyers_m5=float(a.buyers_m5), sellers_m5=float(a.sellers_m5),
                       buyers_h1=float(a.buyers_h1), sellers_h1=float(a.sellers_h1))
            rec["buy_ratio"] = (rec["buys_m5"]+1)/(rec["sells_m5"]+1)
            rec["breadth"] = (rec["buyers_m5"]+1)/(rec["buys_m5"]+1)   # buyers per buy: low = few wallets spamming
            rec["net_buyers"] = (rec["buyers_h1"]+1)/(rec["sellers_h1"]+1)
        recs.append(rec)
    return pd.DataFrame(recs)

if __name__ == "__main__":
    P = pd.read_parquet("launch_cohort.parquet")
    print(f"launch cohort: {len(P)} pools captured live at creation")
    try:
        X = pd.read_parquet("dex_paths.parquet")
        print(f"reusing {len(X)} cached price paths")
    except Exception:
        print("fetching minute paths...")
        X = fetch_paths(P)
    D = build(P, X)
    print(f"\nusable launches (>= {OBS}+20 minutes of trading): {len(D)}")
    if len(D) < 40:
        print("SAMPLE TOO SMALL for signal testing. Reporting descriptive stats only.")
    D.to_parquet("dex_signals.parquet", index=False)

    print(f"\nforward outcome over {HOR} min after the first {OBS} min:")
    print(f"  mean {D.fwd.mean():.2f}x  median {D.fwd.median():.2f}x  "
          f"P(>1x) {(D.fwd>1).mean():.1%}  P(>2x) {(D.fwd>2).mean():.1%}  "
          f"P(>10x) {(D.fwd>10).mean():.1%}")

    SIGS = [("reserve","initial liquidity $"), ("fdv","FDV at launch $"),
            ("obs_vol",f"volume in first {OBS}m"), ("obs_ret",f"return over first {OBS}m"),
            ("obs_peak",f"peak gain in first {OBS}m"), ("obs_dd","give-back from that peak"),
            ("obs_sigma","minute volatility"), ("bars_traded","minutes with any trade"),
            ("vol_accel","volume acceleration"), ("buy_ratio","buys / sells (first 5m)"),
            ("breadth","unique buyers per buy"), ("net_buyers","buyers / sellers (1h)")]

    print("\n" + "="*96)
    print(f"Q1. DO LAUNCH SIGNALS PREDICT THE NEXT {HOR} MINUTES?")
    print("="*96)
    print(f"{'signal':<30} {'n':>5} {'Spearman IC':>12} {'p':>8} {'Q5 med':>9} {'Q1 med':>9} {'Q5 P(>2x)':>11}")
    print("-"*96)
    keep = []
    for k, lab in SIGS:
        if k not in D.columns: continue
        x = D[[k,"fwd"]].dropna()
        if len(x) < 40 or x[k].nunique() < 10: continue
        ic, pv = st.spearmanr(x[k], x["fwd"])
        q = pd.qcut(x[k].rank(method="first"), 5, labels=False, duplicates="drop")
        if q.nunique() < 5: continue
        hi, lo = x[q==4].fwd, x[q==0].fwd
        star = " *" if pv < 0.05 else ""
        print(f"{lab:<30} {len(x):>5} {ic:>+11.3f} {pv:>8.3f} {hi.median():>8.2f}x "
              f"{lo.median():>8.2f}x {(hi>2).mean():>10.1%}{star}")
        if pv < 0.05: keep.append((k, lab, ic))

    print(f"\n  n={len(D)}: |IC| below ~{2/np.sqrt(max(len(D),2)):.2f} is indistinguishable from noise.")
    if keep:
        print("\n  signals with p<0.05:")
        for k, lab, ic in keep:
            print(f"    {lab}: IC {ic:+.3f}")
    else:
        print("\n  No signal reached p<0.05.")

    print("\n" + "="*96)
    print("Q2. WHAT THE LAUNCH FIREHOSE ACTUALLY LOOKS LIKE")
    print("="*96)
    print(f"  pools captured at creation: {len(P)}")
    print(f"  still trading {OBS}+{20} minutes later: {len(D)} ({len(D)/len(P):.1%})")
    print(f"  median initial liquidity: ${P.reserve.median():,.0f}")
    print(f"  median FDV at launch:     ${P.fdv.median():,.0f}")
    for thr in [1e3, 1e4, 1e5]:
        print(f"  pools with initial liquidity > ${thr:,.0f}: {(P.reserve>thr).mean():.1%}")
