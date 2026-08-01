"""Is the edge clustered, and can the bad clusters be filtered out causally?

Two separate questions.

DIAGNOSIS. Compare the real monthly-R series against a null built by shuffling
the TRADES (which preserves the return distribution exactly and destroys only
the time ordering). If the real series has fatter month-level variance, longer
sign runs, or a variance ratio above 1, the edge arrives in clusters rather than
compounding evenly.

FILTERING. Clustering only helps if cluster STATE is knowable in advance. Every
filter here is evaluated causally: the decision to trade bar t uses only
information available before t. The obvious candidates:
  - equity-curve filter: stand aside after the strategy's own trailing R turns
    negative (classic, and usually fails because strategy returns are near-iid)
  - volatility regime
  - trend-efficiency regime (the diagnosed failure mode was chop)
  - funding regime
A filter that helps in-sample but not walk-forward is reported as such.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exits as X         # noqa: E402
import run_exits as RE    # noqa: E402
import run_mtf as RM      # noqa: E402
import data as D          # noqa: E402
import auxfeat as A       # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def build_trades(mode=1, ltf="15min", buf=0.05):
    parts = []
    for sym in RM.CORE:
        sig, m1 = RM.htf_signals(sym, "4h")
        ev = RE.ltf_events(sym, ltf)
        for side in (1, -1):
            ss = sig[sig.side == side]
            if not len(ss):
                continue
            e = ev[side]
            d = X.run(ss, m1, e["div_dt"], e["div_lvl"], e["dot_dt"],
                      mode=mode, buf_frac=buf)
            if len(d):
                d = d.copy()
                d["symbol"] = sym
                parts.append(d)
    T = pd.concat(parts).sort_values("close_dt").reset_index(drop=True)
    T["close_dt"] = pd.to_datetime(T["close_dt"], utc=True)
    return T


def monthly(T):
    return T.set_index(pd.DatetimeIndex(T.close_dt))["r"].resample("ME").sum()


def runs_stat(x):
    s = np.sign(x)
    s = s[s != 0]
    if len(s) < 3:
        return np.nan, np.nan
    runs = 1 + int((s[1:] != s[:-1]).sum())
    longest_neg = 0
    cur = 0
    for v in s:
        cur = cur + 1 if v < 0 else 0
        longest_neg = max(longest_neg, cur)
    return runs, longest_neg


def variance_ratio(m, k):
    """Var of k-month sums / (k * var of 1-month). >1 means positive
    autocorrelation, i.e. clustering."""
    x = m.values
    if len(x) < k * 3:
        return np.nan
    v1 = np.var(x, ddof=1)
    agg = pd.Series(x).rolling(k).sum().dropna().values
    vk = np.var(agg, ddof=1)
    return float(vk / (k * v1)) if v1 > 0 else np.nan


def diagnose(T, n_null=3000, seed=0):
    m = monthly(T)
    rng = np.random.default_rng(seed)
    r = T["r"].values
    dtidx = pd.DatetimeIndex(T.close_dt)

    real = {"months": len(m), "mean": m.mean(), "std": m.std(),
            "pos_share": float((m > 0).mean()), "worst": m.min(),
            "best": m.max()}
    real["runs"], real["longest_neg"] = runs_stat(m.values)
    for k in (2, 3, 6):
        real[f"vr{k}"] = variance_ratio(m, k)
    # top-decile concentration: share of total R from the best 10% of months
    srt = np.sort(m.values)[::-1]
    top = max(1, int(0.1 * len(srt)))
    real["top10_share"] = float(srt[:top].sum() / m.sum()) if m.sum() != 0 else np.nan

    null = {k: [] for k in ("std", "longest_neg", "vr2", "vr3", "vr6",
                            "top10_share", "pos_share")}
    for _ in range(n_null):
        perm = rng.permutation(len(r))
        t2 = pd.Series(r[perm], index=dtidx).resample("ME").sum()
        null["std"].append(t2.std())
        null["pos_share"].append(float((t2 > 0).mean()))
        _, ln = runs_stat(t2.values)
        null["longest_neg"].append(ln)
        for k in (2, 3, 6):
            null[f"vr{k}"].append(variance_ratio(t2, k))
        s2 = np.sort(t2.values)[::-1]
        tp = max(1, int(0.1 * len(s2)))
        null["top10_share"].append(float(s2[:tp].sum() / t2.sum())
                                   if t2.sum() != 0 else np.nan)

    print("=== is the edge clustered? (null = same trades, shuffled order) ===")
    print(f"  months {real['months']}, mean {real['mean']:+.2f}R, "
          f"positive {100*real['pos_share']:.0f}%, worst {real['worst']:+.1f}R")
    print(f"{'statistic':<18}{'real':>10}{'null mean':>11}{'null p95':>10}{'pctile':>9}")
    for k, label in (("std", "monthly std"), ("longest_neg", "longest neg run"),
                     ("vr2", "var ratio 2mo"), ("vr3", "var ratio 3mo"),
                     ("vr6", "var ratio 6mo"), ("top10_share", "top-10% share")):
        arr = np.array(null[k], float)
        arr = arr[np.isfinite(arr)]
        if not len(arr):
            continue
        pct = float((arr < real[k]).mean())
        print(f"{label:<18}{real[k]:>10.3f}{arr.mean():>11.3f}"
              f"{np.percentile(arr,95):>10.3f}{100*pct:>8.0f}%")
    return m, real


def apply_filter(T, mask_fn, label, months_total=None):
    keep = mask_fn(T)
    sub = T[keep]
    if len(sub) < 100:
        return None
    mt = months_total or ((pd.Timestamp(T.close_dt.max())
                           - pd.Timestamp(T.close_dt.min())).days / 30.44)
    r = sub["r"].values
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(cum) - cum))
    moR = r.sum() / mt
    return {"filter": label, "n": len(sub), "kept": len(sub) / len(T),
            "expR": float(r.mean()), "moR": moR, "maxDD_R": dd,
            "monthly_ret": min(0.06 / dd, 0.02) * moR if dd > 0 else 0.0}


def equity_filter(T, lookback, thresh=0.0):
    """Stand aside when the strategy's own trailing R is below thresh.

    CAUSAL: only trades whose EXIT preceded this signal are counted. Sorting by
    signal time and taking the previous k rows is look-ahead, because trades
    hold for days and many of those k were still open at the decision point.
    That bug inflated the 10-trade filter to 4.43%/mo."""
    T = T.sort_values("close_dt").reset_index(drop=True)
    sig = pd.DatetimeIndex(T["close_dt"]).values.astype("datetime64[ns]")
    exi = pd.DatetimeIndex(T["exit_dt"]).values.astype("datetime64[ns]")
    order = np.argsort(exi)
    exi_s = exi[order]
    r_s = T["r"].values[order]
    csum = np.concatenate([[0.0], np.cumsum(r_s)])
    # number of trades fully closed before each signal
    pos = np.searchsorted(exi_s, sig, side="left")
    lo = np.maximum(pos - lookback, 0)
    trail = csum[pos] - csum[lo]
    enough = (pos - lo) >= lookback
    return enough & (trail > thresh)


def main():
    T = build_trades(mode=1)
    mt = ((pd.Timestamp(T.close_dt.max())
           - pd.Timestamp(T.close_dt.min())).days / 30.44)
    print(f"TIGHTEN system: {len(T)} trades over {mt:.1f} months\n")
    m, real = diagnose(T)

    print("\n=== can losing clusters be filtered CAUSALLY? ===")
    rows = [apply_filter(T, lambda d: np.ones(len(d), bool), "none (baseline)", mt)]
    for lb in (10, 25, 50, 100):
        rows.append(apply_filter(T, lambda d, lb=lb: equity_filter(d, lb),
                                 f"trailing {lb}-trade R > 0", mt))
    rows = [r for r in rows if r]
    print(f"{'filter':<28}{'kept':>7}{'n':>7}{'expR':>9}{'mo R':>8}"
          f"{'maxDD':>9}{'%/mo':>8}")
    for r in rows:
        print(f"{r['filter']:<28}{100*r['kept']:>6.0f}%{r['n']:>7}"
              f"{r['expR']:>9.4f}{r['moR']:>8.2f}{r['maxDD_R']:>9.1f}"
              f"{100*r['monthly_ret']:>7.2f}%")

    print("\nmonth-to-month autocorrelation of the strategy's own returns:")
    for lag in (1, 2, 3):
        ac = m.autocorr(lag)
        print(f"  lag {lag}: {ac:+.3f}"
              + ("   (predictable)" if abs(ac) > 0.3 else "   (no signal)"))
    pd.DataFrame(rows).to_csv(os.path.join(REP, "clusters.csv"), index=False)


if __name__ == "__main__":
    main()
