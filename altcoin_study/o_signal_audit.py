"""Stage O: audit the launch signals that survived Stage N.

Three ways they could still be fake or useless:
  O1 They are one factor wearing six hats (all collinear proxies for "hype at launch").
  O2 They are a listing-ERA proxy: 2020 listings were quiet AND lucky, so the signal is
     really just "was it 2020". Test WITHIN each cohort.
  O3 They predict the BODY (which coins bleed less) but not the TAIL (which coins 10x).
     Only tail prediction is worth anything to the lottery thesis.
Then: is the surviving edge tradeable after the friction those coins actually carry?
"""
import numpy as np, pandas as pd
from scipy import stats as st

D = pd.read_parquet("launch_signals_binance.parquet")
SIG = {"adv_w":"week-1 daily $ volume", "vol_w":"realised volatility",
       "dd_w":"give-back from week-1 peak", "peak_w":"best gain in week 1",
       "tsize":"average trade size", "btc_reg":"BTC vs EMA200 at listing"}
# orient every signal so that HIGHER = predicted BETTER, using full-sample sign
ORIENT = {"adv_w":-1, "vol_w":-1, "dd_w":+1, "peak_w":-1, "tsize":-1, "btc_reg":-1}

for k, sgn in ORIENT.items():
    D[k+"_z"] = sgn*st.zscore(np.log1p(D[k].rank(pct=True)*10), nan_policy="omit")

print("="*100)
print("O1. ARE THESE SIX SIGNALS ACTUALLY ONE SIGNAL?")
print("="*100)
Z = D[[k+"_z" for k in SIG]].dropna()
C = Z.corr(method="spearman")
C.index = [SIG[k] for k in SIG]; C.columns = [k[:9] for k in SIG]
print(C.round(2).to_string())
ev = np.linalg.eigvalsh(np.corrcoef(Z.T.values))[::-1]
print(f"\n  first principal component explains {ev[0]/ev.sum():.0%} of the variance "
      f"-> {'largely ONE factor' if ev[0]/ev.sum() > 0.45 else 'genuinely distinct factors'}")

print("\n" + "="*100)
print("O2. IS IT JUST A LISTING-ERA PROXY? (Spearman IC computed WITHIN each cohort)")
print("="*100)
print(f"{'signal':<30} {'pooled IC':>10} " + "".join(f"{y:>8}" for y in sorted(D.year.unique())) + f"{'mean within':>13}")
print("-"*100)
for k, lab in SIG.items():
    x = D[[k,"fwd","year"]].dropna()
    pooled = st.spearmanr(x[k], x["fwd"])[0]*ORIENT[k]
    per = []
    line = ""
    for y in sorted(D.year.unique()):
        z = x[x.year == y]
        if len(z) < 25:
            line += f"{'-':>8}"; continue
        ic = st.spearmanr(z[k], z["fwd"])[0]*ORIENT[k]
        per.append(ic); line += f"{ic:>+8.2f}"
    print(f"{lab:<30} {pooled:>+10.3f} {line} {np.mean(per):>+12.3f}")
print("\n  (pooled >> mean-within means the signal is mostly telling you the listing year)")

print("\n" + "="*100)
print("O3. BODY OR TAIL? does the signal concentrate the big winners?")
print("="*100)
print(f"  base rates: P(>2x)={  (D.fwd>2).mean():.1%}   P(>5x)={(D.fwd>5).mean():.1%}   "
      f"P(>10x)={(D.fwd>10).mean():.1%}\n")
print(f"{'signal':<30} {'Q5 median':>11} {'Q1 median':>11} {'Q5 P(>2x)':>11} {'Q1 P(>2x)':>11} "
      f"{'Q5 P(>5x)':>11} {'Q1 P(>5x)':>11}")
print("-"*100)
for k, lab in SIG.items():
    x = D[[k+"_z","fwd"]].dropna()
    q = pd.qcut(x[k+"_z"].rank(method="first"), 5, labels=False)
    hi, lo = x[q==4].fwd, x[q==0].fwd     # Q5 = signal says BEST
    print(f"{lab:<30} {hi.median():>10.2f}x {lo.median():>10.2f}x {(hi>2).mean():>10.1%} "
          f"{(lo>2).mean():>10.1%} {(hi>5).mean():>10.1%} {(lo>5).mean():>10.1%}")

print("\n  chi-square: is the count of >5x outcomes different across quintiles?")
for k, lab in SIG.items():
    x = D[[k+"_z","fwd"]].dropna()
    q = pd.qcut(x[k+"_z"].rank(method="first"), 5, labels=False)
    tab = pd.crosstab(q, x.fwd > 5)
    if tab.shape[1] < 2: continue
    chi2, pv, _, _ = st.chi2_contingency(tab.values)
    print(f"    {lab:<30} p={pv:.3f}  "
          f"{'TAIL SIGNAL' if pv < 0.05 else 'no tail effect'}")

print("\n" + "="*100)
print("O4. COMBINED FACTOR vs THE SINGLE BEST")
print("="*100)
D["combo"] = D[[k+"_z" for k in SIG]].mean(axis=1)
for name, col in [("week-1 volume alone", "adv_w_z"), ("6-signal composite", "combo")]:
    x = D[[col,"fwd","year"]].dropna()
    ic = st.spearmanr(x[col], x["fwd"])[0]
    tr = x[x.year <= 2023]; te = x[x.year >= 2024]
    ictr = st.spearmanr(tr[col], tr["fwd"])[0]; icte = st.spearmanr(te[col], te["fwd"])[0]
    q = pd.qcut(te[col].rank(method="first"), 5, labels=False)
    best = te[q==4]
    print(f"  {name:<24} IC {ic:+.3f}  (train {ictr:+.3f} / test {icte:+.3f})   "
          f"test-Q5: median {best.fwd.median():.2f}x  mean {best.fwd.mean():.2f}x  "
          f"P(>2x) {(best.fwd>2).mean():.1%}")

print("\n" + "="*100)
print("O5. IS THE SURVIVING EDGE TRADEABLE?")
print("="*100)
x = D[["adv_w_z","adv_w","fwd"]].dropna()
q = pd.qcut(x["adv_w_z"].rank(method="first"), 5, labels=False)
print(f"{'quintile':<10} {'median $vol/day':>18} {'median':>9} {'mean':>8} {'P(>1x)':>8} {'P(>2x)':>8}")
for Q in range(5):
    z = x[q==Q]
    print(f"{'Q'+str(Q+1):<10} {z.adv_w.median():>17,.0f} {z.fwd.median():>8.2f}x "
          f"{z.fwd.mean():>7.2f}x {(z.fwd>1).mean():>7.1%} {(z.fwd>2).mean():>7.1%}")
best = x[q==4]
print(f"\n  The 'best' quintile is the QUIETEST launches: median ${best.adv_w.median():,.0f}/day.")
print(f"  Its basket outcome is mean {best.fwd.mean():.2f}x, median {best.fwd.median():.2f}x.")
for cost in [0.0, 0.05, 0.10]:
    print(f"    after a {cost:.0%} round trip: mean {best.fwd.mean()*(1-cost):.2f}x  "
          f"median {best.fwd.median()*(1-cost):.2f}x")
