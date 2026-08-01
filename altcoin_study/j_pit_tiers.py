"""Stage J: tier the lottery by liquidity KNOWN AT PURCHASE TIME.

Stage I ranked coins by full-history volume, which is circular -- "ended up with $200M/day"
is a label for "won". Here the tier is the coin's median daily quote volume over its FIRST
30 DAYS, which is information you actually have when you buy the ticket.
"""
import numpy as np, pandas as pd
from h_lottery import apply_rule, btc_ret

p = pd.read_parquet("panel_4h.parquet")
paths, meta = {}, []
for s, g in p.groupby("symbol"):
    g = g.sort_values("dt")
    px = g["close"].to_numpy(float); dts = g["dt"].to_numpy()
    qv = g["quote_volume"].to_numpy(float)
    if len(px) < 30: continue
    paths[s] = (px, dts)
    first30 = qv[:min(180, len(qv))]          # 180 4h bars = 30 days
    meta.append((s, np.median(first30)*6, pd.Timestamp(dts[0]).year, len(px)))
M = pd.DataFrame(meta, columns=["sym","adv0","year","bars"]).set_index("sym")

RULE, KW = "trail", dict(d=0.70)

def basket(syms):
    mults, exc = [], []
    for s in syms:
        if s not in paths or s == "BTCUSDT": continue
        px, dts = paths[s]
        mu, held = apply_rule(px, RULE, **KW)
        if not np.isfinite(mu) or mu <= 0: continue
        mults.append(mu)
        j = min(held, len(dts)-1)
        b = btc_ret(pd.Timestamp(dts[0]), pd.Timestamp(dts[j]))
        if np.isfinite(b): exc.append(mu - (1+b))
    return np.array(mults), np.array(exc)

print("="*104)
print("J1. LOTTERY BY LIQUIDITY AT PURCHASE TIME (first-30-day volume) -- no look-ahead")
print("="*104)
print(f"{'first-30d daily volume':<26} {'n':>5} {'mean':>8} {'median':>8} {'P(>1x)':>8} {'P(>5x)':>8} "
      f"{'P(>10x)':>8} {'vs BTC':>9}")
print("-"*104)
bins = [0, 5e6, 2e7, 5e7, 2e8, 1e12]
labs = ["<$5M", "$5-20M", "$20-50M", "$50-200M", ">$200M"]
M["tier0"] = pd.cut(M.adv0, bins, labels=labs)
for lab in labs:
    syms = M[M.tier0 == lab].index.tolist()
    m, e = basket(syms)
    if len(m) < 10: continue
    print(f"{lab:<26} {len(m):>5} {m.mean():>7.2f}x {np.median(m):>7.2f}x {(m>1).mean():>7.1%} "
          f"{(m>5).mean():>7.1%} {(m>10).mean():>7.1%} {e.mean():>+8.2f}")

print("\n" + "="*104)
print("J2. SAME, BUT EXCLUDING THE 2020-2021 BULL (is the lottery still alive?)")
print("="*104)
print(f"{'first-30d daily volume':<26} {'n':>5} {'mean':>8} {'median':>8} {'P(>1x)':>8} {'P(>5x)':>8} "
      f"{'vs BTC':>9}")
print("-"*104)
for lab in labs:
    syms = M[(M.tier0 == lab) & (M.year >= 2022)].index.tolist()
    m, e = basket(syms)
    if len(m) < 10: continue
    print(f"{lab:<26} {len(m):>5} {m.mean():>7.2f}x {np.median(m):>7.2f}x {(m>1).mean():>7.1%} "
          f"{(m>5).mean():>7.1%} {e.mean():>+8.2f}")

print("\n" + "="*104)
print("J3. LISTING COHORT -- when did the shitcoin lottery actually pay?")
print("="*104)
print(f"{'cohort':<10} {'n':>5} {'mean':>8} {'median':>8} {'P(>5x)':>8} {'P(>10x)':>8} {'vs BTC':>9} "
      f"{'beat BTC':>10}")
print("-"*104)
for y in sorted(M.year.unique()):
    syms = M[M.year == y].index.tolist()
    m, e = basket(syms)
    if len(m) < 20: continue
    print(f"{int(y):<10} {len(m):>5} {m.mean():>7.2f}x {np.median(m):>7.2f}x {(m>5).mean():>7.1%} "
          f"{(m>10).mean():>7.1%} {e.mean():>+8.2f} {(e>0).mean():>9.1%}")

print("\n" + "="*104)
print("J4. THE HONEST BOTTOM LINE FOR A SMALL-CAP-ONLY BASKET")
print("="*104)
small = M[(M.adv0 < 2e7)].index.tolist()
small_recent = M[(M.adv0 < 2e7) & (M.year >= 2022)].index.tolist()
for lab, syms in [("all small listings (<$20M/d at listing)", small),
                  ("small listings, 2022 onward", small_recent)]:
    m, e = basket(syms)
    rng = np.random.default_rng(4)
    print(f"\n{lab}  (n={len(m)})")
    print(f"  mean {m.mean():.2f}x   median {np.median(m):.2f}x   "
          f"P(>1x) {(m>1).mean():.1%}   P(>10x) {(m>10).mean():.1%}   vs BTC {e.mean():+.2f}")
    for N in [10, 25, 50, 100]:
        d = rng.choice(m, size=(20000, N), replace=True).mean(axis=1)
        print(f"    {N:>3} tickets: median {np.median(d):.2f}x  P(lose money) {(d<1).mean():.1%}  "
              f"P(>2x) {(d>2).mean():.1%}")
