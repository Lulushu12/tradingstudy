"""Stage A: survivorship-free base rates for the Binance USDT-perp alt universe."""
import numpy as np, pandas as pd

p = pd.read_parquet("panel_4h.parquet")
LAST = p["dt"].max()

g = p.groupby("symbol")
u = pd.DataFrame({
    "first": g["dt"].min(), "last": g["dt"].max(), "bars": g.size(),
    "px_first": g["close"].first(), "px_last": g["close"].last(),
    "px_max": g["high"].max(), "px_min": g["low"].min(),
    "adv_usd": g["quote_volume"].median() * 6,      # median 4h quote vol -> daily
})
u["alive"] = u["last"] >= LAST - pd.Timedelta(days=7)
u["age_days"] = (u["last"] - u["first"]).dt.days
u["ret_listing"] = u["px_last"] / u["px_first"] - 1
u["mfe"] = u["px_max"] / u["px_first"] - 1        # best case from listing
u["dd_from_peak"] = u["px_last"] / u["px_max"] - 1

# BTC as the benchmark the trader already knows
btc = p[p.symbol == "BTCUSDT"].set_index("dt")["close"]

print("=" * 74)
print("A1. UNIVERSE COMPOSITION  (Binance USDT perps, 4h, 2020-01..2026-06)")
print("=" * 74)
print(f"symbols ever listed : {len(u)}")
print(f"still alive         : {u.alive.sum()}   ({u.alive.mean():.1%})")
print(f"delisted / dead     : {(~u.alive).sum()}   ({1-u.alive.mean():.1%})")
print(f"median age (days)   : {u.age_days.median():.0f}   | dead only: {u.loc[~u.alive,'age_days'].median():.0f}")

# listings per year and their fate
u["list_year"] = u["first"].dt.year
print("\nlistings per year and death rate:")
t = u.groupby("list_year").agg(listed=("alive","size"), dead=("alive", lambda s: (~s).sum()))
t["death_rate"] = t.dead / t.listed
print(t.to_string())

print("\n" + "=" * 74)
print("A2. WHAT HAPPENS IF YOU JUST BUY AND HOLD A RANDOM PERP FROM LISTING")
print("=" * 74)
for lab, sub in [("ALL", u), ("alive only (survivorship-biased view)", u[u.alive]),
                 ("listed 2024+", u[u.list_year >= 2024])]:
    r = sub["ret_listing"]
    print(f"\n{lab}  (n={len(sub)})")
    print(f"  mean {r.mean():+.1%} | median {r.median():+.1%} | "
          f"share positive {(r > 0).mean():.1%}")
    print("  pct: " + "  ".join(f"p{q}={np.percentile(r,q):+.0%}" for q in [5,25,50,75,95,99]))
    print(f"  peak-to-final decay: median {sub['dd_from_peak'].median():.1%}  "
          f"(median best-case MFE from listing {sub['mfe'].median():+.1%})")

print("\n" + "=" * 74)
print("A3. LIQUIDITY TIERS (median daily quote volume, USD)")
print("=" * 74)
bins = [0, 1e6, 1e7, 5e7, 2e8, 1e12]
labs = ["<$1M", "$1-10M", "$10-50M", "$50-200M", ">$200M"]
u["tier"] = pd.cut(u.adv_usd, bins, labels=labs)
print(u.groupby("tier", observed=True).agg(
    n=("adv_usd","size"), dead_pct=("alive", lambda s: 1-s.mean()),
    med_ret=("ret_listing","median")).to_string())

u.to_parquet("universe.parquet")
print("\nsaved universe.parquet")
