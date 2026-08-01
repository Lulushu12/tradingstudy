"""Stage I: extrapolate from Binance-listed coins toward real shitcoins.

Two things Stage H could not see:
  I1  Does the lottery get better or worse as the coin gets smaller/thinner? If economics
      degrade monotonically down the liquidity ladder, the memecoin end is worse, not better.
  I2  Real shitcoins cost far more to trade than Binance perps (DEX fees, slippage on both
      sides, MEV, token transfer taxes) and can go to EXACTLY zero (rug/honeypot), which a
      Binance perp effectively never does. How much of the edge survives that?
"""
import numpy as np, pandas as pd
from h_lottery import apply_rule, btc_ret

p = pd.read_parquet("panel_4h.parquet")
u = pd.read_parquet("universe.parquet")

paths = {}
for s, g in p.groupby("symbol"):
    g = g.sort_values("dt")
    paths[s] = (g["close"].to_numpy(float), g["dt"].to_numpy())

RULE = ("trail", dict(d=0.70))          # best mean rule from Stage H
RULE2 = ("trail", dict(d=0.50))         # best-vs-BTC rule from Stage H

def basket(syms, rule, kw, cost=0.0, rug=0.0, seed=3):
    """cost = round-trip frictional cost as a fraction; rug = prob the ticket is a total loss."""
    rng = np.random.default_rng(seed)
    mults, exc = [], []
    for s in syms:
        if s not in paths: continue
        px, dts = paths[s]
        if len(px) < 30 or s == "BTCUSDT": continue
        mu, held = apply_rule(px, rule, **kw)
        if not np.isfinite(mu) or mu <= 0: continue
        if rug > 0 and rng.random() < rug:
            mu = 0.0
        else:
            mu *= (1 - cost)
        mults.append(mu)
        j = min(held, len(dts)-1)
        b = btc_ret(pd.Timestamp(dts[0]), pd.Timestamp(dts[j]))
        if np.isfinite(b): exc.append(mu - (1+b))
    return np.array(mults), np.array(exc)

print("="*106)
print("I1. LOTTERY ECONOMICS BY LIQUIDITY TIER  (trailing stop 70% off peak, buy at listing)")
print("="*106)
print(f"{'tier (median daily $ volume)':<32} {'n':>5} {'mean':>8} {'median':>8} {'P(>1x)':>8} "
      f"{'P(>10x)':>8} {'vs BTC':>9}")
print("-"*106)
bins = [0, 5e6, 2e7, 5e7, 2e8, 1e12]
labs = ["<$5M", "$5-20M", "$20-50M", "$50-200M", ">$200M"]
u["tier"] = pd.cut(u.adv_usd, bins, labels=labs)
for lab in labs:
    syms = u[u.tier == lab].index.tolist()
    m, e = basket(syms, *RULE)
    if len(m) < 10: continue
    print(f"{lab:<32} {len(m):>5} {m.mean():>7.2f}x {np.median(m):>7.2f}x "
          f"{(m>1).mean():>7.1%} {(m>10).mean():>7.1%} {e.mean():>+8.2f}")

print("\nsame, split by listing era (younger cohorts = the current shitcoin regime):")
u["list_year"] = u["first"].dt.year
for y in sorted(u.list_year.unique()):
    syms = u[u.list_year == y].index.tolist()
    m, e = basket(syms, *RULE)
    if len(m) < 20: continue
    print(f"  listed {int(y)}: n={len(m):>3}  mean {m.mean():>5.2f}x  median {np.median(m):>5.2f}x  "
          f"P(>10x) {(m>10).mean():>5.1%}  vs BTC {e.mean():>+6.2f}")

print("\n" + "="*106)
print("I2. FRICTION: what real shitcoin trading costs do to the basket")
print("="*106)
allsyms = list(paths.keys())
print("A round trip on a Binance perp costs ~0.1%. On a DEX small cap: LP fee 0.6-2%,")
print("slippage in and out, MEV sandwich, plus token transfer taxes. 5-15% round trip is normal.\n")
print(f"{'round-trip cost':>16} {'mean mult':>11} {'vs BTC':>9} {'beat BTC':>10}")
print("-"*52)
for cost in [0.001, 0.02, 0.05, 0.10, 0.15, 0.20]:
    m, e = basket(allsyms, *RULE, cost=cost)
    print(f"{cost:>15.1%} {m.mean():>10.2f}x {e.mean():>+8.2f} {(e>0).mean():>9.1%}")

print("\nAnd rug risk -- the fraction of tickets that go to EXACTLY zero (LP pull, honeypot,")
print("mint authority abuse). Binance-listed coins essentially never do this; DEX tokens do.\n")
print(f"{'rug rate':>10} {'@5% cost':>12} {'@10% cost':>12} {'vs BTC @10%':>13}")
print("-"*50)
for rug in [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]:
    m5, _ = basket(allsyms, *RULE, cost=0.05, rug=rug)
    m10, e10 = basket(allsyms, *RULE, cost=0.10, rug=rug)
    print(f"{rug:>9.0%} {m5.mean():>11.2f}x {m10.mean():>11.2f}x {e10.mean():>+12.2f}")

print("\n" + "="*106)
print("I3. BREAKEVEN -- how bad can the real shitcoin world be before the lottery is a losing game?")
print("="*106)
m0, _ = basket(allsyms, *RULE)
print(f"  Binance-listed baseline: mean {m0.mean():.3f}x per ticket")
for rug in [0.0, 0.1, 0.2, 0.3]:
    lo, hi = 0.0, 0.95
    for _ in range(40):
        mid = (lo+hi)/2
        m, _ = basket(allsyms, *RULE, cost=mid, rug=rug)
        if m.mean() > 1.0: lo = mid
        else: hi = mid
    print(f"  at a {rug:.0%} rug rate, the basket breaks even at a round-trip cost of {lo:.1%}")
print("\n  (breakeven vs simply holding BTC is a much higher bar than breakeven vs cash)")
