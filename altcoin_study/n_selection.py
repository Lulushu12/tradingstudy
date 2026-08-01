"""Stage N: DO LAUNCH-TIME SIGNALS PREDICT THE TAIL?

The honest gap left by LOTTERY_FINDINGS.md. Tested on the survivorship-free Binance perp
universe because that is where the statistical power is: 786 launches, full history, dead
coins included, and a real out-of-sample split by listing cohort.

DESIGN (strictly causal):
  - OBSERVATION WINDOW: the first W days of trading. Signals computed from this window only.
  - FORWARD OUTCOME    : the lottery result measured from the END of that window onward,
                         using the trailing-70%-off-peak rule that won in Stage H.
  So a signal never sees any part of the return it is predicting.

Because the outcome distribution is dominated by rare outliers, every signal is judged on
BOTH rank statistics (Spearman IC, decile medians -- robust) AND the mean multiple (what
you actually earn -- fragile). A signal that only moves the mean is probably noise.
"""
import numpy as np, pandas as pd
from scipy import stats as st

W_DAYS = 7                      # observation window
BARS = W_DAYS*6                 # 4h bars in the window

p = pd.read_parquet("panel_4h.parquet")
fund = pd.read_parquet("funding.parquet")
btc = p[p.symbol=="BTCUSDT"].set_index("dt")["close"].sort_index()
btc_ema = btc.ewm(span=200, adjust=False).mean()

def trail_mult(px, d=0.70):
    if len(px) < 3 or px[0] <= 0: return np.nan
    r = px/px[0]
    peak = np.maximum.accumulate(r); stop = peak*(1-d)
    hit = np.argmax(r <= stop) if (r <= stop).any() else -1
    return stop[hit] if hit > 0 else r[-1]

rows = []
for s, g in p.groupby("symbol"):
    if s == "BTCUSDT": continue
    g = g.sort_values("dt")
    if len(g) < BARS + 30: continue
    c = g["close"].to_numpy(float); o = g["open"].to_numpy(float)
    h = g["high"].to_numpy(float); l = g["low"].to_numpy(float)
    qv = g["quote_volume"].to_numpy(float); nt = g["count"].to_numpy(float)
    dts = g["dt"].to_numpy()
    win = slice(0, BARS)
    cw = c[win]; qvw = qv[win]
    if cw[0] <= 0 or not np.isfinite(cw).all(): continue

    ret_w   = cw[-1]/cw[0] - 1                       # first-week return
    peak_w  = h[win].max()/cw[0] - 1                 # best in window
    dd_w    = cw[-1]/h[win].max() - 1                # given back by end of window
    rets    = np.diff(np.log(np.maximum(cw, 1e-12)))
    vol_w   = rets.std()*np.sqrt(6*365) if len(rets) > 3 else np.nan
    adv_w   = np.median(qvw)*6                       # daily $ volume in window
    # volume trend: 2nd half vs 1st half of the window
    half = BARS//2
    vtrend  = (qvw[half:].sum()+1)/(qvw[:half].sum()+1)
    tsize   = np.nansum(qvw)/max(np.nansum(nt[win]), 1)   # avg trade size $
    # funding during the window: positioning / crowding at launch
    fs = fund[fund.symbol == s]
    fs = fs[(fs.dt >= dts[0]) & (fs.dt <= dts[BARS-1])]
    fund_w  = fs["rate"].mean() if len(fs) else np.nan
    # market regime at listing
    t0 = pd.Timestamp(dts[0])
    try:
        breg = float(btc.asof(t0)/btc_ema.asof(t0) - 1)
    except Exception:
        breg = np.nan

    fwd = trail_mult(c[BARS:])                       # OUTCOME, strictly after the window
    if not np.isfinite(fwd) or fwd <= 0: continue
    rows.append(dict(sym=s, year=t0.year, listed=t0,
                     ret_w=ret_w, peak_w=peak_w, dd_w=dd_w, vol_w=vol_w,
                     adv_w=adv_w, vtrend=vtrend, tsize=tsize, fund_w=fund_w,
                     btc_reg=breg, fwd=fwd, logfwd=np.log(fwd)))

D = pd.DataFrame(rows).dropna(subset=["fwd"])
print(f"launches with a clean {W_DAYS}-day observation window and forward outcome: {len(D)}")
print(f"outcome: mean {D.fwd.mean():.2f}x  median {D.fwd.median():.2f}x  "
      f"P(>2x) {(D.fwd>2).mean():.1%}  P(>5x) {(D.fwd>5).mean():.1%}\n")

SIGNALS = [
    ("ret_w",   "first-week return"),
    ("peak_w",  "best gain within first week"),
    ("dd_w",    "give-back from week-1 peak"),
    ("vol_w",   "realised volatility (annualised)"),
    ("adv_w",   "week-1 daily $ volume"),
    ("vtrend",  "volume trend (2nd half / 1st half)"),
    ("tsize",   "average trade size $"),
    ("fund_w",  "mean funding rate in week 1"),
    ("btc_reg", "BTC vs its EMA200 at listing"),
]

print("="*104)
print("N1. DOES ANY LAUNCH SIGNAL PREDICT THE FORWARD OUTCOME? (full sample)")
print("="*104)
print(f"{'signal':<36} {'Spearman IC':>12} {'p':>8} {'top-decile':>12} {'bot-decile':>12} {'t/b mean':>10}")
print("-"*104)
res = {}
for k, lab in SIGNALS:
    x = D[[k,"fwd","logfwd"]].dropna()
    if len(x) < 60: continue
    ic, pv = st.spearmanr(x[k], x["fwd"])
    q = pd.qcut(x[k].rank(method="first"), 10, labels=False)
    top, bot = x[q==9], x[q==0]
    res[k] = (ic, pv)
    print(f"{lab:<36} {ic:>+11.3f} {pv:>8.3f} {top.fwd.median():>11.2f}x {bot.fwd.median():>11.2f}x "
          f"{top.fwd.mean()/max(bot.fwd.mean(),1e-9):>9.2f}")

print("\n  (Spearman IC = rank correlation between the signal and the forward multiple.")
print("   With n~700, |IC| below about 0.075 is not distinguishable from noise.)")

print("\n" + "="*104)
print("N2. OUT-OF-SAMPLE: fit the ranking on 2020-2023, test it on 2024-2026")
print("="*104)
tr, te = D[D.year <= 2023], D[D.year >= 2024]
print(f"train n={len(tr)}   test n={len(te)}\n")
print(f"{'signal':<36} {'train IC':>10} {'test IC':>10} {'sign holds':>12} {'test top-dec med':>18}")
print("-"*104)
survivors = []
for k, lab in SIGNALS:
    a = tr[[k,"fwd"]].dropna(); b = te[[k,"fwd"]].dropna()
    if len(a) < 60 or len(b) < 60: continue
    ica, _ = st.spearmanr(a[k], a["fwd"]); icb, pb = st.spearmanr(b[k], b["fwd"])
    holds = "yes" if np.sign(ica) == np.sign(icb) and abs(icb) > 0.05 else "no"
    q = pd.qcut(b[k].rank(method="first"), 10, labels=False)
    print(f"{lab:<36} {ica:>+9.3f} {icb:>+9.3f} {holds:>12} {b[q==9].fwd.median():>17.2f}x")
    if holds == "yes": survivors.append((k, lab, ica, icb))

print("\n" + "="*104)
print("N3. WHAT SURVIVES, AND IS IT WORTH ANYTHING?")
print("="*104)
if not survivors:
    print("  Nothing kept a consistent sign with a non-trivial IC out of sample.")
else:
    for k, lab, ica, icb in survivors:
        sub = te[[k,"fwd"]].dropna()
        q = pd.qcut(sub[k].rank(method="first"), 5, labels=False)
        print(f"\n  {lab}   (train IC {ica:+.3f} -> test IC {icb:+.3f})")
        print(f"    {'quintile':>10} {'n':>5} {'median':>9} {'mean':>8} {'P(>1x)':>8} {'P(>2x)':>8}")
        for Q in range(5):
            z = sub[q==Q].fwd
            print(f"    {'Q'+str(Q+1):>10} {len(z):>5} {z.median():>8.2f}x {z.mean():>7.2f}x "
                  f"{(z>1).mean():>7.1%} {(z>2).mean():>7.1%}")

print("\n" + "="*104)
print("N4. THE POWER PROBLEM -- can this sample even detect a tail-picking edge?")
print("="*104)
n = len(D); base = (D.fwd > 5).mean()
print(f"  n={n} launches, {(D.fwd>5).sum()} of them ({base:.1%}) returned >5x after the window.")
print(f"  A top-decile selector holds ~{n//10} names and would contain ~{base*n/10:.1f} such coins by chance.")
for lift in [2, 3, 5]:
    k = base*n/10
    # Poisson tail: probability of seeing >= lift*k winners by chance alone
    from scipy.stats import poisson
    pv = 1 - poisson.cdf(np.ceil(lift*k)-1, k)
    print(f"    a selector {lift}x better than chance would show ~{lift*k:.1f} winners "
          f"in that decile (p={pv:.3f} vs chance)")
print("\n  So this sample can only detect a LARGE tail edge. A subtle one is invisible here,")
print("  and absence of evidence at this sample size is weak evidence of absence.")

D.to_parquet("launch_signals_binance.parquet")
