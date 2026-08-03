"""
Can the three survivors cover for each other?

Two claims are tested separately because they are not the same claim.

PASSIVE DIVERSIFICATION. Run all three concurrently. This cannot create edge:
the mean of a portfolio is the weighted mean of its parts, so combining
zero-expectancy systems gives a zero-expectancy portfolio. What it can do is cut
variance, and that matters statistically. Three systems each with a small real
edge, individually drowned in noise, pool into a larger effective sample. If the
edges are real and the correlations low, the combined t-statistic should rise
roughly as the square root of the number of independent streams. If the combined
t-statistic does NOT rise, that is evidence the individual point estimates were
noise rather than small real edges.

ACTIVE ROTATION. Switch capital to whichever system is currently working. This
is a much stronger claim: it requires that recent performance predicts future
performance. It is tested here by allocating each month to the system with the
best trailing record, using only information available at the time, and
comparing against the equal weight portfolio and against a random chooser.

All returns are net of 10bps round trip and come from the walk-forward
out-of-sample trades only, never the in-sample fitted ones.
"""

import warnings

import numpy as np
import pandas as pd

import data as dat
import indicators as ta
import walkforward as wf

warnings.filterwarnings("ignore")

RISK_PER_TRADE = 1.0     # each strategy risks the same notional per trade


def oos_trades():
    """Walk-forward out-of-sample trades per strategy, exactly as walkforward.py."""
    pool = {}
    for name, (fn, tf, convs) in wf.SURVIVORS.items():
        by_conv = {c: wf.all_trades(fn, tf, c) for c in convs}
        every = [t for ts in by_conv.values() for t in ts]
        lo = min(t.entry_time for t in every).normalize()
        hi = max(t.exit_time for t in every)
        picked = []
        for is_s, is_e, oos_e in wf.folds(lo, hi):
            scored = {}
            for c in convs:
                ins = wf.between(by_conv[c], is_s, is_e)
                scored[c] = wf.net_returns(ins).mean() if len(ins) >= 10 else -np.inf
            best = max(scored, key=scored.get)
            picked.extend(wf.between(by_conv[best], is_e, oos_e))
        pool[name] = picked
    return pool


def monthly(trades):
    """Net percent per month, summed over trades closed that month.

    Summing rather than compounding models a fixed stake per trade, which is how
    a portfolio of these would actually be run: risk is set per signal, not
    reinvested within the month.
    """
    if not trades:
        return pd.Series(dtype=float)
    s = pd.Series([t.ret_pct - wf.COST_BPS / 100.0 for t in trades],
                  index=pd.DatetimeIndex([t.exit_time for t in trades]))
    return s.groupby(s.index.to_period("M")).sum().sort_index()


def tstat(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 3 or x.std(ddof=1) == 0:
        return np.nan
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))


def sharpe(x, periods=12):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 3 or x.std(ddof=1) == 0:
        return np.nan
    return x.mean() / x.std(ddof=1) * np.sqrt(periods)


def max_dd(x):
    eq = np.cumsum(np.nan_to_num(x))
    peak = np.maximum.accumulate(eq)
    return float((eq - peak).min())


def regime_labels(index):
    """Causal regime labels for BTC, evaluated on daily bars.

    Every label at time t uses only data up to t: trailing 30 day realised
    volatility and ADX(14), each split against their own expanding median so the
    threshold is not set with hindsight either.
    """
    d = dat.load_tf("BTCUSDT", "1d", verbose=False)
    ret = d["close"].pct_change()
    vol = ret.rolling(30).std()
    adxv, _, _ = ta.adx(d["high"], d["low"], d["close"], 14)
    trend90 = d["close"].pct_change(90)

    vol_med = vol.expanding(min_periods=180).median()
    adx_med = adxv.expanding(min_periods=180).median()

    lab = pd.DataFrame({
        "vol": np.where(vol > vol_med, "high vol", "low vol"),
        "trend": np.where(adxv > adx_med, "trending", "chop"),
        "dir": np.where(trend90 > 0, "bull", "bear"),
    }, index=d.index)
    return lab.reindex(index, method="ffill")


def main():
    print(f"all figures net of {wf.COST_BPS}bps round trip, "
          f"walk-forward out-of-sample trades only\n")
    pool = oos_trades()
    names = list(pool)

    m = pd.DataFrame({n: monthly(pool[n]) for n in names}).sort_index()
    m = m.loc[m.notna().any(axis=1)]
    m_filled = m.fillna(0.0)      # a month with no signals is a flat month

    # ---------------------------------------------------------- correlations
    print("=== monthly return correlation (months where both traded) ===")
    print(m.corr().round(3).to_string())
    print("\nmonths active:", {n: int(m[n].notna().sum()) for n in names})

    # ---------------------------------------------------------- individual vs combined
    rows = []
    for n in names:
        x = m_filled[n]
        rows.append({"portfolio": n, "months": int(m[n].notna().sum()),
                     "mean_pct_mo": round(x.mean(), 3), "t_stat": round(tstat(x), 2),
                     "sharpe": round(sharpe(x), 2), "max_dd_pct": round(max_dd(x), 1),
                     "total_pct": round(x.sum(), 1)})

    eq = m_filled.mean(axis=1)
    rows.append({"portfolio": "EQUAL WEIGHT (all 3)", "months": len(eq),
                 "mean_pct_mo": round(eq.mean(), 3), "t_stat": round(tstat(eq), 2),
                 "sharpe": round(sharpe(eq), 2), "max_dd_pct": round(max_dd(eq), 1),
                 "total_pct": round(eq.sum(), 1)})

    # volatility parity: scale each to the same monthly vol before averaging
    vol = m_filled.std(ddof=1).replace(0, np.nan)
    vp = (m_filled / vol).mean(axis=1) * vol.mean()
    rows.append({"portfolio": "VOL PARITY (all 3)", "months": len(vp),
                 "mean_pct_mo": round(vp.mean(), 3), "t_stat": round(tstat(vp), 2),
                 "sharpe": round(sharpe(vp), 2), "max_dd_pct": round(max_dd(vp), 1),
                 "total_pct": round(vp.sum(), 1)})

    print("\n=== individual vs combined ===")
    print(pd.DataFrame(rows).to_string(index=False))

    # ---------------------------------------------------------- rotation
    print("\n=== active rotation: allocate next month to the best trailing "
          "performer ===")
    rot_rows = []
    for look in (1, 2, 3, 6, 12):
        picks, rets = [], []
        for i in range(look, len(m_filled)):
            trail = m_filled.iloc[i - look:i].sum()
            best = trail.idxmax()
            picks.append(best)
            rets.append(m_filled.iloc[i][best])
        r = np.array(rets)
        rot_rows.append({
            "rule": f"best of last {look}mo", "months": len(r),
            "mean_pct_mo": round(r.mean(), 3), "t_stat": round(tstat(r), 2),
            "sharpe": round(sharpe(r), 2), "max_dd_pct": round(max_dd(r), 1),
            "total_pct": round(r.sum(), 1),
            "switches": int(sum(1 for a, b in zip(picks, picks[1:]) if a != b)),
        })
    # Benchmark: a chooser with no skill. ONE random path is worthless here,
    # because monthly variance is large enough that a single draw can beat every
    # rule by luck. 2000 paths give the distribution a skill-free rule lives in,
    # and a rotation rule only means something if it beats that distribution.
    rng = np.random.default_rng(7)
    arr = m_filled.to_numpy()
    means = np.empty(2000)
    for k in range(2000):
        pick = rng.integers(0, arr.shape[1], size=arr.shape[0])
        means[k] = arr[np.arange(arr.shape[0]), pick].mean()
    rot_rows.append({
        "rule": "random pick (2000 paths, median)", "months": len(arr),
        "mean_pct_mo": round(float(np.median(means)), 3),
        "t_stat": np.nan, "sharpe": np.nan, "max_dd_pct": np.nan,
        "total_pct": round(float(np.median(means) * len(arr)), 1), "switches": np.nan})
    rot_rows.append({
        "rule": "random pick 5th-95th pct", "months": len(arr),
        "mean_pct_mo": np.nan, "t_stat": np.nan, "sharpe": np.nan,
        "max_dd_pct": np.nan,
        "total_pct": f"{np.percentile(means,5)*len(arr):.0f} to "
                     f"{np.percentile(means,95)*len(arr):.0f}",
        "switches": np.nan})
    best_hind = m_filled.sum().idxmax()
    x = m_filled[best_hind]
    rot_rows.append({"rule": f"hindsight: always {best_hind}", "months": len(x),
                     "mean_pct_mo": round(x.mean(), 3), "t_stat": round(tstat(x), 2),
                     "sharpe": round(sharpe(x), 2), "max_dd_pct": round(max_dd(x), 1),
                     "total_pct": round(x.sum(), 1), "switches": 0})
    print(pd.DataFrame(rot_rows).to_string(index=False))

    # does last month's rank predict this month's rank at all?
    print("\n=== does trailing performance predict next month? ===")
    for look in (1, 3, 6):
        cs = []
        for i in range(look, len(m_filled)):
            trail = m_filled.iloc[i - look:i].sum()
            nxt = m_filled.iloc[i]
            if trail.std() > 0 and nxt.std() > 0:
                cs.append(np.corrcoef(trail.values, nxt.values)[0, 1])
        cs = np.array([c for c in cs if not np.isnan(c)])
        print(f"  trailing {look:2d}mo vs next month, mean cross-sectional "
              f"correlation: {cs.mean():+.3f}  (t={tstat(cs):.2f}, n={len(cs)})")

    # ---------------------------------------------------------- regimes
    print("\n=== mean net % per trade by regime (are they complementary?) ===")
    for axis in ("vol", "trend", "dir"):
        out = {}
        for n in names:
            tr = pool[n]
            lab = regime_labels(pd.DatetimeIndex([t.entry_time for t in tr]))[axis].values
            r = wf.net_returns(tr)
            out[n] = {k: round(float(r[lab == k].mean()), 3) if (lab == k).any() else np.nan
                      for k in pd.unique(lab)}
            out[n].update({f"n_{k}": int((lab == k).sum()) for k in pd.unique(lab)})
        print(f"\n-- by {axis}")
        print(pd.DataFrame(out).T.to_string())

    # ------------------------------------------------- switch on regime, not on P&L
    # The regime table below shows S5 earning in trends and S6 earning in chop.
    # If that is real rather than an artifact, switching on the REGIME should
    # work where switching on trailing P&L did not. Two versions are run: a
    # hindsight one that picks each regime's best strategy using the whole
    # sample, which is an optimistic ceiling and not tradable, and a walk-forward
    # one that only ever uses months already past.
    daily = regime_labels(dat.load_tf("BTCUSDT", "1d", verbose=False).index)
    # a month's regime is the label standing on the last day of the PREVIOUS
    # month, so it is known before the month starts
    dm = daily.copy()
    dm["p"] = dm.index.to_period("M")
    last = dm.groupby("p").last()
    reg_month = last.shift(1).reindex(m_filled.index)

    print("\n=== switching on regime rather than on trailing P&L ===")
    reg_rows = []
    for axis in ("trend", "vol", "dir"):
        lab = reg_month[axis]
        ok = lab.notna()

        # hindsight ceiling
        hind = []
        for i, (per, row) in enumerate(m_filled.iterrows()):
            if not ok.iloc[i]:
                continue
            sub = m_filled[lab.values == lab.iloc[i]]
            hind.append(row[sub.mean().idxmax()])
        reg_rows.append({"rule": f"{axis}: hindsight best per regime",
                         "months": len(hind), "mean_pct_mo": round(np.mean(hind), 3),
                         "t_stat": round(tstat(hind), 2), "sharpe": round(sharpe(hind), 2),
                         "max_dd_pct": round(max_dd(hind), 1),
                         "total_pct": round(np.sum(hind), 1)})

        # walk-forward: only months strictly before the current one
        wfr = []
        for i in range(len(m_filled)):
            if not ok.iloc[i]:
                continue
            hist = m_filled.iloc[:i]
            hlab = lab.iloc[:i]
            sub = hist[hlab.values == lab.iloc[i]]
            if len(sub) < 6:
                continue
            wfr.append(m_filled.iloc[i][sub.mean().idxmax()])
        reg_rows.append({"rule": f"{axis}: walk-forward best per regime",
                         "months": len(wfr),
                         "mean_pct_mo": round(np.mean(wfr), 3) if wfr else np.nan,
                         "t_stat": round(tstat(wfr), 2) if wfr else np.nan,
                         "sharpe": round(sharpe(wfr), 2) if wfr else np.nan,
                         "max_dd_pct": round(max_dd(wfr), 1) if wfr else np.nan,
                         "total_pct": round(np.sum(wfr), 1) if wfr else np.nan})
    reg_rows.append({"rule": "EQUAL WEIGHT reference", "months": len(eq),
                     "mean_pct_mo": round(eq.mean(), 3), "t_stat": round(tstat(eq), 2),
                     "sharpe": round(sharpe(eq), 2), "max_dd_pct": round(max_dd(eq), 1),
                     "total_pct": round(eq.sum(), 1)})
    print(pd.DataFrame(reg_rows).to_string(index=False))
    pd.DataFrame(reg_rows).to_csv("playlist_study/results/combine_regime.csv", index=False)

    m_filled.to_csv("playlist_study/results/combine_monthly.csv")
    pd.DataFrame(rows).to_csv("playlist_study/results/combine_portfolios.csv", index=False)
    pd.DataFrame(rot_rows).to_csv("playlist_study/results/combine_rotation.csv", index=False)
    print("\nwrote combine_{monthly,portfolios,rotation}.csv")


if __name__ == "__main__":
    main()
