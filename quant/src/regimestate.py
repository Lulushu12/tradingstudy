"""Can the profitable regimes be identified IN ADVANCE?

Part 10 showed 69% of profit arrives in 7 of 66 months and that the strategy's
own equity curve cannot predict which. This asks the separate question: does
MARKET STATE identify them?

Two levels, deliberately:

  MONTH LEVEL   descriptive only. Seven positive examples out of sixty-six is
                far too few to fit on; any classifier would memorise. Used to
                describe what those months looked like, never to predict.

  TRADE LEVEL   the real test. Each trade carries the market state prevailing at
                its signal bar, giving thousands of observations instead of
                sixty-six. Conditioning is then validated WALK-FORWARD: the
                threshold is fitted on trailing data only and applied forward.

Regime features are market-wide (averaged over the universe) rather than
per-symbol, because the question is about the environment, not the instrument.
All are causal: state is read strictly BEFORE the signal bar.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auxfeat as A       # noqa: E402
import clusters as C      # noqa: E402
import data as D          # noqa: E402
import run_mtf as RM      # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def market_state(freq="4h"):
    per = []
    for sym in RM.CORE:
        bars, _ = D.load(sym, freq, "DESIGN", pad_bars=600)
        b = bars.set_index("dt")
        c = b["close"]
        ret = np.log(c).diff()
        s = pd.DataFrame(index=b.index)
        s["vol"] = ret.rolling(180).std()
        s["vol_rank"] = s["vol"].rolling(1000).rank(pct=True)
        # trend efficiency: net displacement over total path travelled. The
        # diagnosed failure mode was chop, which is exactly low efficiency.
        for n in (60, 180, 360):
            s[f"eff{n}"] = (ret.rolling(n).sum().abs()
                            / ret.abs().rolling(n).sum().replace(0, np.nan))
        s["absmom180"] = (c / c.shift(180) - 1).abs()
        s["dd_from_high"] = c / c.rolling(1080).max() - 1
        try:
            ax = A.features(A.attach(bars, sym, freq))
            n = min(len(ax), len(s))
            for src, dst in (("funding_ma21", "funding_ma"),
                             ("oi_chg96", "oi_chg"), ("svc_z", "svc")):
                if src in ax:
                    v = np.full(len(s), np.nan)
                    v[:n] = ax[src].values[:n]
                    s[dst] = v
        except Exception:                       # noqa: BLE001
            pass
        per.append(s)
    idx = per[0].index
    for p in per[1:]:
        idx = idx.intersection(p.index)
    return (sum(p.loc[idx] for p in per) / len(per)).sort_index()


def attach_state(T, M):
    T = T.sort_values("close_dt").reset_index(drop=True)
    sig = pd.DatetimeIndex(T["close_dt"]).values.astype("datetime64[ns]")
    mi = M.index.values.astype("datetime64[ns]")
    pos = np.searchsorted(mi, sig, side="right") - 1     # strictly before
    ok = pos >= 0
    out = T.copy()
    for c in M.columns:
        v = np.full(len(T), np.nan)
        v[ok] = M[c].values[pos[ok]]
        out[c] = v
    return out


def month_profile(T, M):
    m = C.monthly(T)
    j = M.resample("ME").last().reindex(m.index)
    top = m.nlargest(7).index
    rest = m.index.difference(top)
    print("=== what did the 7 big months look like? (DESCRIPTIVE ONLY) ===")
    print(f"  they carry {100*m.loc[top].sum()/m.sum():.0f}% of all profit")
    print(f"{'feature':<14}{'top-7 mean':>12}{'other mean':>12}{'ratio':>8}")
    for c in j.columns:
        a, b = j.loc[top, c].mean(), j.loc[rest, c].mean()
        if np.isfinite(a) and np.isfinite(b) and b != 0:
            print(f"{c:<14}{a:>12.4f}{b:>12.4f}{a/b:>8.2f}")
    return m, top


def trade_level(T, cols):
    print("\n=== trade level: does regime at signal time separate outcomes? ===")
    print(f"{'feature':<14}{'lo tercile':>12}{'mid':>9}{'hi':>9}{'spread':>9}")
    rows = []
    for c in cols:
        x = T[c].values
        if np.isfinite(x).sum() < 500:
            continue
        q = pd.qcut(pd.Series(x), 3, labels=False, duplicates="drop")
        g = T.groupby(q)["r"].mean()
        if len(g) < 3:
            continue
        sp = g.iloc[-1] - g.iloc[0]
        rows.append((c, sp))
        print(f"{c:<14}{g.iloc[0]:>12.4f}{g.iloc[1]:>9.4f}{g.iloc[2]:>9.4f}{sp:>9.4f}")
    return rows


def wf_regime(T, col, train_months=24, step_months=3, q=0.5, side=1):
    T = T.sort_values("close_dt").reset_index(drop=True)
    dt = pd.DatetimeIndex(T["close_dt"])
    months = pd.period_range(dt.min(), dt.max(), freq="M")
    keep = np.zeros(len(T), bool)
    i = train_months
    while i < len(months):
        tr_hi = months[i].start_time.tz_localize("UTC")
        te_hi = months[min(i + step_months, len(months) - 1)].start_time.tz_localize("UTC")
        if te_hi <= tr_hi:
            break
        trm = np.asarray(dt < tr_hi)
        tem = np.asarray((dt >= tr_hi) & (dt < te_hi))
        x_tr = T[col].values[trm]
        x_tr = x_tr[np.isfinite(x_tr)]
        if np.isfinite(x_tr).sum() > 300 and tem.sum() > 0:
            thr = np.quantile(x_tr, q)
            sel = (T[col].values >= thr) if side > 0 else (T[col].values <= thr)
            keep |= (np.asarray(tem) & sel)
        i += step_months
    return keep


def score(r, mt):
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(cum) - cum))
    mo = r.sum() / mt
    return mo, dd, (min(0.06 / dd, 0.02) * mo if dd > 0 else 0.0)


def main():
    T = C.build_trades(mode=1)
    M = market_state("4h")
    T = attach_state(T, M)
    mt = ((pd.Timestamp(T.close_dt.max())
           - pd.Timestamp(T.close_dt.min())).days / 30.44)
    cols = [c for c in M.columns if T[c].notna().sum() > 500]
    month_profile(T, M)
    rows = trade_level(T, cols)

    b_mo, b_dd, b_pm = score(T["r"].values, mt)
    print(f"\n=== WALK-FORWARD regime filter (threshold fitted on the past) ===")
    print(f"  baseline: n={len(T)} expR {T.r.mean():+.4f} moR {b_mo:+.2f} "
          f"maxDD {b_dd:.1f} -> {100*b_pm:.2f}%/mo")
    print(f"{'feature':<14}{'dir':>4}{'q':>5}{'kept':>7}{'expR':>9}"
          f"{'moR':>8}{'maxDD':>8}{'%/mo':>8}")
    best = None
    for c, sp in sorted(rows, key=lambda z: -abs(z[1]))[:6]:
        for sd in (1, -1):
            for q in (0.3, 0.5, 0.7):
                k = wf_regime(T, c, q=q, side=sd)
                if k.sum() < 300:
                    continue
                r = T.loc[k, "r"].values
                mo, dd, pm = score(r, mt)
                print(f"{c:<14}{'>=' if sd>0 else '<=':>4}{q:>5.1f}"
                      f"{100*k.mean():>6.0f}%{r.mean():>9.4f}{mo:>8.2f}"
                      f"{dd:>8.1f}{100*pm:>7.2f}%")
                if best is None or pm > best[0]:
                    best = (pm, c, sd, q)
    if best:
        print(f"\n  best walk-forward regime filter: {best[1]} "
              f"{'>=' if best[2]>0 else '<='} q{best[3]} -> {100*best[0]:.2f}%/mo "
              f"(baseline {100*b_pm:.2f}%/mo)")
        print(f"  {'IMPROVES' if best[0] > b_pm else 'does NOT improve'} on trading always")


if __name__ == "__main__":
    main()
