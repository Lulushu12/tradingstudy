"""Stage P: does the quiet-launch signal still work in the MODERN regime, and is the
resulting basket actually profitable -- or does it just rank you into breakeven?

Stage O found week-1 volume (inverted) has a within-cohort IC of +0.22 in all 7 cohorts and
a genuine tail effect (p=0.004). But its out-of-sample top quintile showed mean ~1.00x.
Those two facts have to be reconciled: a signal can rank correctly and still not pay.
"""
import numpy as np, pandas as pd
from scipy import stats as st

D = pd.read_parquet("launch_signals_binance.parquet")
D["q_vol"] = -D["adv_w"]                       # higher = quieter = predicted better
D["q_vol2"] = -D["vol_w"]

def quint(x, col):
    return pd.qcut(x[col].rank(method="first"), 5, labels=False)

print("="*100)
print("P1. THE SAME SIGNAL, SPLIT BY ERA  (quintiles of inverted week-1 volume)")
print("="*100)
for lab, sub in [("2020-2021 (the bull)", D[D.year <= 2021]),
                 ("2022-2023", D[(D.year >= 2022) & (D.year <= 2023)]),
                 ("2024-2026 (modern)", D[D.year >= 2024])]:
    if len(sub) < 60: continue
    q = quint(sub, "q_vol")
    print(f"\n{lab}   n={len(sub)}   (base: median {sub.fwd.median():.2f}x, "
          f"P(>2x) {(sub.fwd>2).mean():.1%}, P(>5x) {(sub.fwd>5).mean():.1%})")
    print(f"  {'quintile':>9} {'n':>5} {'median':>9} {'mean':>8} {'P(>1x)':>8} {'P(>2x)':>8} {'P(>5x)':>8}")
    for Q in range(5):
        z = sub[q == Q].fwd
        tag = "  <- quietest" if Q == 4 else ("  <- loudest" if Q == 0 else "")
        print(f"  {'Q'+str(Q+1):>9} {len(z):>5} {z.median():>8.2f}x {z.mean():>7.2f}x "
              f"{(z>1).mean():>7.1%} {(z>2).mean():>7.1%} {(z>5).mean():>7.1%}{tag}")
    ic = st.spearmanr(sub.q_vol, sub.fwd)[0]
    tab = pd.crosstab(q, sub.fwd > 2)
    pv = st.chi2_contingency(tab.values)[1] if tab.shape[1] == 2 else np.nan
    print(f"  IC {ic:+.3f}   chi2 p on P(>2x) across quintiles: {pv:.3f}")

print("\n" + "="*100)
print("P2. CLEANEST VIEW: rank WITHIN each listing cohort, then pool")
print("="*100)
D["rank_in_yr"] = D.groupby("year")["q_vol"].rank(pct=True)
D["yq"] = pd.cut(D.rank_in_yr, [0,.2,.4,.6,.8,1.0], labels=[1,2,3,4,5])
print(f"  {'within-year quintile':<24} {'n':>5} {'median':>9} {'mean':>8} {'P(>1x)':>8} "
      f"{'P(>2x)':>8} {'P(>5x)':>8}")
for Q in [1,2,3,4,5]:
    z = D[D.yq == Q].fwd
    print(f"  {'Q'+str(Q)+(' (quietest)' if Q==5 else ' (loudest)' if Q==1 else ''):<24} "
          f"{len(z):>5} {z.median():>8.2f}x {z.mean():>7.2f}x {(z>1).mean():>7.1%} "
          f"{(z>2).mean():>7.1%} {(z>5).mean():>7.1%}")
tab = pd.crosstab(D.yq, D.fwd > 5)
print(f"\n  chi2 p on P(>5x) across within-year quintiles: "
      f"{st.chi2_contingency(tab.values)[1]:.4f}")

print("\n  same, restricted to 2024+ only:")
M = D[D.year >= 2024].copy()
M["rank_in_yr"] = M.groupby("year")["q_vol"].rank(pct=True)
M["yq"] = pd.cut(M.rank_in_yr, [0,.2,.4,.6,.8,1.0], labels=[1,2,3,4,5])
for Q in [1,3,5]:
    z = M[M.yq == Q].fwd
    print(f"    Q{Q}: n={len(z):>3}  median {z.median():.2f}x  mean {z.mean():.2f}x  "
          f"P(>1x) {(z>1).mean():.1%}  P(>2x) {(z>2).mean():.1%}  P(>5x) {(z>5).mean():.1%}")
tab = pd.crosstab(M.yq, M.fwd > 2)
print(f"    chi2 p on P(>2x), 2024+: {st.chi2_contingency(tab.values)[1]:.4f}")

print("\n" + "="*100)
print("P3. THE BASKET YOU COULD ACTUALLY BUY  (quietest 20% of each year's listings)")
print("="*100)
sel = D[D.yq == 5]
print(f"  n={len(sel)} coins, median week-1 volume ${sel.adv_w.median():,.0f}/day")
rng = np.random.default_rng(9)
for lab, s in [("all years", sel), ("2024+ only", sel[sel.year >= 2024])]:
    v = s.fwd.to_numpy()
    if len(v) < 20: continue
    print(f"\n  {lab}: n={len(v)}  mean {v.mean():.2f}x  median {np.median(v):.2f}x")
    top = np.sort(v)[::-1]
    print(f"    top ticket = {top[0]/v.sum():.1%} of proceeds; top 3 = {top[:3].sum()/v.sum():.1%}")
    b = rng.choice(v, size=(20000, len(v)), replace=True).mean(axis=1)
    print(f"    bootstrap 95% CI on the mean: [{np.percentile(b,2.5):.2f}x, "
          f"{np.percentile(b,97.5):.2f}x]  P(mean<=1) = {(b<=1).mean():.3f}")
    for cost in [0.05, 0.10]:
        bc = b*(1-cost)
        print(f"    after {cost:.0%} round trip: mean {v.mean()*(1-cost):.2f}x  "
              f"P(mean<=1) = {(bc<=1).mean():.3f}")

print("\n" + "="*100)
print("P4. SANITY: what IS a quiet launch? (is the signal just 'small coin'?)")
print("="*100)
D["yq_i"] = D.yq.astype(float)
for Q in [1,3,5]:
    z = D[D.yq_i == Q]
    print(f"  Q{Q}: median week-1 $vol {z.adv_w.median():>13,.0f}  "
          f"median week-1 return {z.ret_w.median():>+7.1%}  "
          f"median week-1 vol {z.vol_w.median():>6.1f}  "
          f"median avg trade ${z.tsize.median():>7,.0f}")
print("\n  Note: 'quiet' here is relative to the SAME year's listings, so it is not a")
print("  disguised bet on the 2020 cohort being small.")
