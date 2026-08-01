"""Stage H: the LOTTERY TICKET thesis.

Not shorting. The actual question: buy small positions in random shitcoins, let them run,
accept that most go to zero, and get paid by the fat right tail.

Tested on the full survivorship-free Binance USDT-perp universe. Note this is the
FAVOURABLE end of the shitcoin spectrum -- a coin that earned a Binance perp listing has
already survived a brutal selection funnel. Whatever we measure here is an UPPER BOUND on
what random DEX/memecoin tickets would do.

Every ticket is benchmarked against simply holding BTC over the identical calendar window,
because that is the real alternative use of the money.
"""
import numpy as np, pandas as pd

p = pd.read_parquet("panel_4h.parquet")
btc = p[p.symbol == "BTCUSDT"].set_index("dt")["close"].sort_index()

def btc_ret(t0, t1):
    try:
        a = btc.asof(t0); b = btc.asof(t1)
        return b/a - 1 if np.isfinite(a) and np.isfinite(b) and a > 0 else np.nan
    except Exception:
        return np.nan

# ---------------------------------------------------------------- exit rules
def apply_rule(px, rule, **kw):
    """px: 1-D close path starting at entry (px[0] = entry price).
       returns (multiple_on_capital, bars_held)"""
    e = px[0]
    r = px/e
    n = len(r)
    if rule == "hold":
        return r[-1], n
    if rule == "tp":                                    # hard take-profit at X
        X = kw["X"]
        hit = np.argmax(r >= X) if (r >= X).any() else -1
        return (X, hit) if hit > 0 else (r[-1], n)
    if rule == "trail":                                 # trailing stop, % off peak
        d = kw["d"]
        peak = np.maximum.accumulate(r)
        stop = peak*(1-d)
        hit = np.argmax(r <= stop) if (r <= stop).any() else -1
        if hit > 0:
            return stop[hit], hit
        return r[-1], n
    if rule == "free_ride":                             # sell cost basis at 2x, trail rest
        X, d = kw.get("X", 2.0), kw.get("d", 0.5)
        hit = np.argmax(r >= X) if (r >= X).any() else -1
        if hit <= 0:
            return r[-1], n                             # never doubled: full exposure
        banked = 1.0                                    # took original stake off the table
        rest = r[hit:]/r[hit]                           # remaining (X-1)/X of position rides
        keep = (X-1.0)/X
        peak = np.maximum.accumulate(rest); stop = peak*(1-d)
        h2 = np.argmax(rest <= stop) if (rest <= stop).any() else -1
        tail = stop[h2] if h2 > 0 else rest[-1]
        return banked + keep*X*tail, (hit + (h2 if h2 > 0 else len(rest)))
    if rule == "stop":                                  # hard stop-loss, else hold
        d = kw["d"]
        hit = np.argmax(r <= (1-d)) if (r <= (1-d)).any() else -1
        return ((1-d), hit) if hit > 0 else (r[-1], n)
    if rule == "time":                                  # hold N days then sell
        k = min(int(kw["days"]*6), n-1)
        return r[k], k
    raise ValueError(rule)

RULES = [
    ("hold to today / death",            "hold",      {}),
    ("take profit 2x",                   "tp",        dict(X=2)),
    ("take profit 5x",                   "tp",        dict(X=5)),
    ("take profit 10x",                  "tp",        dict(X=10)),
    ("trailing stop 30% off peak",       "trail",     dict(d=0.30)),
    ("trailing stop 50% off peak",       "trail",     dict(d=0.50)),
    ("trailing stop 70% off peak",       "trail",     dict(d=0.70)),
    ("free ride: bank stake @2x, trail 50%", "free_ride", dict(X=2.0, d=0.50)),
    ("free ride: bank stake @3x, trail 50%", "free_ride", dict(X=3.0, d=0.50)),
    ("hard stop -50%, else hold",        "stop",      dict(d=0.50)),
    ("hold 30 days",                     "time",      dict(days=30)),
    ("hold 90 days",                     "time",      dict(days=90)),
    ("hold 180 days",                    "time",      dict(days=180)),
]

if __name__ == "__main__":
    paths = {}
    for s, g in p.groupby("symbol"):
        g = g.sort_values("dt")
        paths[s] = (g["close"].to_numpy(float), g["dt"].to_numpy())
    print(f"universe: {len(paths)} coins\n")

    print("="*112)
    print("H1. THE RAW LOTTERY DISTRIBUTION -- buy at listing, what is the best it ever got?")
    print("="*112)
    mfe = []
    for s,(px,dts) in paths.items():
        if len(px) < 30: continue
        mfe.append((s, px.max()/px[0], px[-1]/px[0], len(px)))
    m = pd.DataFrame(mfe, columns=["sym","peak_mult","final_mult","bars"])
    for thr in [1.5, 2, 3, 5, 10, 20, 50, 100]:
        print(f"  reached {thr:>4g}x at some point: {(m.peak_mult>=thr).mean():6.1%}   "
              f"|  still {thr:>4g}x at the end: {(m.final_mult>=thr).mean():6.1%}")
    print(f"\n  median peak multiple {m.peak_mult.median():.2f}x, "
          f"median final multiple {m.final_mult.median():.2f}x")
    print(f"  best coin peaked at {m.peak_mult.max():.0f}x ({m.loc[m.peak_mult.idxmax(),'sym']})")

    print("\n" + "="*112)
    print("H2. EXIT RULES -- equal-weight ticket across every coin, buy at listing")
    print("="*112)
    print(f"{'rule':<40} {'mean mult':>10} {'median':>8} {'>1x':>7} {'>2x':>7} {'>10x':>7} "
          f"{'vs BTC':>9} {'beat BTC':>9}")
    print("-"*112)
    res = {}
    for lab, rule, kw in RULES:
        mults, bmk = [], []
        for s,(px,dts) in paths.items():
            if len(px) < 30 or s == "BTCUSDT": continue
            mu, held = apply_rule(px, rule, **kw)
            if not np.isfinite(mu) or mu <= 0: continue
            mults.append(mu)
            j = min(held, len(dts)-1)
            b = btc_ret(pd.Timestamp(dts[0]), pd.Timestamp(dts[j]))
            bmk.append(b)
        mults = np.array(mults); bmk = np.array(bmk, dtype=float)
        ok = np.isfinite(bmk)
        excess = mults[ok] - (1+bmk[ok])
        res[lab] = mults
        print(f"{lab:<40} {mults.mean():>9.2f}x {np.median(mults):>7.2f}x "
              f"{(mults>1).mean():>6.1%} {(mults>2).mean():>6.1%} {(mults>10).mean():>6.1%} "
              f"{excess.mean():>+8.2f} {(excess>0).mean():>8.1%}")

    print("\n" + "="*112)
    print("H3. HOW CONCENTRATED IS THE PAYOFF? (best rule by mean)")
    print("="*112)
    best = max(res, key=lambda k: res[k].mean())
    v = np.sort(res[best])[::-1]
    print(f"  rule: {best}   (n={len(v)} tickets, mean {v.mean():.2f}x)")
    tot = v.sum()
    for k in [1, 3, 5, 10, 25]:
        print(f"    top {k:>2} tickets = {v[:k].sum()/tot:5.1%} of all proceeds")
    print(f"    bottom 50% of tickets = {v[len(v)//2:].sum()/tot:5.1%} of proceeds")

    print("\n" + "="*112)
    print("H4. HOW MANY TICKETS DO YOU NEED? (bootstrap, 20k draws per basket size)")
    print("="*112)
    rng = np.random.default_rng(11)
    arr = res[best]
    print(f"  using rule: {best}")
    print(f"  {'tickets':>8} {'median':>9} {'mean':>8} {'P(lose money)':>15} {'P(>2x basket)':>15} {'p5':>7} {'p95':>8}")
    for N in [1, 5, 10, 25, 50, 100, 200, len(arr)]:
        draws = rng.choice(arr, size=(20000, N), replace=True).mean(axis=1)
        print(f"  {N:>8} {np.median(draws):>8.2f}x {draws.mean():>7.2f}x "
              f"{(draws<1).mean():>14.1%} {(draws>2).mean():>14.1%} "
              f"{np.percentile(draws,5):>6.2f}x {np.percentile(draws,95):>7.2f}x")

    print("\n" + "="*112)
    print("H5. DOES THE ENTRY MATTER? (same rules, entry at a RANDOM point in the coin's life)")
    print("="*112)
    rng2 = np.random.default_rng(5)
    for lab, rule, kw in [r for r in RULES if r[0] in
                          ("hold to today / death","trailing stop 50% off peak",
                           "free ride: bank stake @2x, trail 50%","take profit 2x")]:
        mults = []
        for s,(px,dts) in paths.items():
            if len(px) < 200 or s == "BTCUSDT": continue
            for _ in range(3):
                i = rng2.integers(0, len(px)-60)
                mu,_ = apply_rule(px[i:], rule, **kw)
                if np.isfinite(mu) and mu > 0: mults.append(mu)
        mults = np.array(mults)
        print(f"  {lab:<40} mean {mults.mean():>6.2f}x  median {np.median(mults):>5.2f}x  "
              f"P(>1x) {(mults>1).mean():5.1%}  P(>10x) {(mults>10).mean():5.1%}  n={len(mults)}")
