"""Alpha-decay test: is the 4H trend-continuation edge being arbitraged away?

Question this answers: if an edge is visible in years of public price data, the
efficient-markets objection says it should already be crowded out. That is not a
philosophical claim, it is a measurable one. A crowded-out edge decays: expectancy
per trade trends toward (and through) zero as more capital learns it.

Method (no new fitting, no parameter search):
  - Take the finalist strategies exactly as frozen in STRATEGY_FINDINGS.md.
  - Split realised net_R per trade by calendar year and by first/second half.
  - Regress net_R on time (years since first trade). A real decay shows a
    significantly NEGATIVE slope. Report the t-stat honestly, including the fact
    that per-trade R is very noisy so the test has low power.
  - Report the implied date expectancy crosses zero IF the point-estimate slope
    is real, plus the CI on that slope, so the uncertainty is visible.

This test can only falsify "the edge is decaying". It cannot prove persistence.
"""
import warnings; warnings.filterwarnings("ignore")
import math
import numpy as np, pandas as pd
import indicators as ind
from finalists import build_trades, sim_equity


def two_sided_p(t):
    return math.erfc(abs(t) / math.sqrt(2.0))


def taken_trades(tr, mode="single"):
    """Replay the single-position rule and return only the trades actually taken."""
    tr = tr.sort_values("entry_time").reset_index(drop=True)
    if mode == "concurrent":
        return tr
    busy_until = -1
    keep = []
    for i, r in tr.iterrows():
        if r["entry_time"] < busy_until:
            continue
        busy_until = r["exit_time"]
        keep.append(i)
    return tr.loc[keep].reset_index(drop=True)


def per_year(tr):
    t = tr.copy()
    t["dt"] = pd.to_datetime(t["entry_time"], unit="s", utc=True)
    t["year"] = t["dt"].dt.year
    rows = []
    for y, g in t.groupby("year"):
        n = len(g)
        m = g["net_R"].mean()
        se = g["net_R"].std(ddof=1) / math.sqrt(n) if n > 1 else float("nan")
        wr = (g["outcome"] == "target").mean()
        rows.append(dict(year=y, n=n, wr=wr, expR=m, se=se,
                         lo=m - 1.96 * se, hi=m + 1.96 * se))
    return pd.DataFrame(rows)


def slope_test(tr):
    """OLS of net_R on years-since-first-trade. Returns slope in R per year."""
    t = tr.sort_values("entry_time")
    x = (t["entry_time"].values - t["entry_time"].values[0]) / (365.25 * 86400.0)
    y = t["net_R"].values
    n = len(x)
    xb, yb = x.mean(), y.mean()
    sxx = ((x - xb) ** 2).sum()
    b = ((x - xb) * (y - yb)).sum() / sxx
    a = yb - b * xb
    resid = y - (a + b * x)
    s2 = (resid ** 2).sum() / (n - 2)
    se_b = math.sqrt(s2 / sxx)
    tstat = b / se_b
    return dict(n=n, intercept=a, slope=b, se=se_b, t=tstat, p=two_sided_p(tstat),
                lo=b - 1.96 * se_b, hi=b + 1.96 * se_b, span=x[-1])


def half_split(tr):
    t = tr.sort_values("entry_time").reset_index(drop=True)
    mid = len(t) // 2
    out = []
    for name, g in (("first half", t.iloc[:mid]), ("second half", t.iloc[mid:])):
        n = len(g)
        m = g["net_R"].mean()
        se = g["net_R"].std(ddof=1) / math.sqrt(n)
        d0 = pd.to_datetime(g["entry_time"].iloc[0], unit="s", utc=True).date()
        d1 = pd.to_datetime(g["entry_time"].iloc[-1], unit="s", utc=True).date()
        out.append(dict(half=name, n=n, expR=m, se=se, start=d0, end=d1,
                        wr=(g["outcome"] == "target").mean()))
    d = out[1]["expR"] - out[0]["expR"]
    se_d = math.sqrt(out[0]["se"] ** 2 + out[1]["se"] ** 2)
    return out, dict(diff=d, se=se_d, t=d / se_d, p=two_sided_p(d / se_d))


def run(df, kind, rr=2.0, mode="single"):
    tr = taken_trades(build_trades(df, kind, rr), mode)
    print(f"\n===== {kind}  rr={rr}  mode={mode}  n={len(tr)} =====")

    py = per_year(tr)
    print("  per-year net expectancy (R/trade, 95% CI):")
    for _, r in py.iterrows():
        flag = "" if r["lo"] <= 0 <= r["hi"] else ("  *pos" if r["lo"] > 0 else "  *NEG")
        print(f"    {int(r['year'])}  n={int(r['n']):3d}  WR={r['wr']:5.1%}  "
              f"expR={r['expR']:+.3f}  [{r['lo']:+.3f},{r['hi']:+.3f}]{flag}")

    halves, diff = half_split(tr)
    print("  split-half:")
    for h in halves:
        print(f"    {h['half']:12} {h['start']}..{h['end']}  n={h['n']:3d}  "
              f"WR={h['wr']:5.1%}  expR={h['expR']:+.3f} (se {h['se']:.3f})")
    print(f"    second minus first = {diff['diff']:+.3f} R  "
          f"(se {diff['se']:.3f}, t={diff['t']:+.2f}, p={diff['p']:.2f})")

    s = slope_test(tr)
    print("  decay regression (net_R ~ time):")
    print(f"    slope = {s['slope']:+.4f} R per year  "
          f"[95% CI {s['lo']:+.4f}, {s['hi']:+.4f}]  t={s['t']:+.2f}  p={s['p']:.2f}")
    print(f"    intercept (expectancy at t0) = {s['intercept']:+.3f} R, "
          f"span = {s['span']:.1f} years")
    if s["slope"] < 0:
        yrs_to_zero = -s["intercept"] / s["slope"]
        print(f"    IF the point estimate were real, expectancy hits zero at "
              f"t0 + {yrs_to_zero:.1f} years")
    else:
        print("    point estimate is non-negative: no decay signal in the data")
    # power note
    print(f"    detectable slope at 80% power over this span is roughly "
          f"±{2.8 * s['se']:.4f} R/yr; anything smaller this test cannot see")
    return tr, py, s


def regime_table(df, win=30):
    """Per-year market character, to separate 'the edge decayed' from 'the market
    stopped trending'. A trend-continuation strategy is SUPPOSED to earn less in a
    low-efficiency (chop) year. If the down years are also the choppy years, decay
    is not the parsimonious explanation.

    efficiency ratio = |net move over `win` bars| / sum of |bar moves| over `win`.
    High = clean directional travel. Low = chop.
    """
    c = df["close"]
    net = (c - c.shift(win)).abs()
    path = c.diff().abs().rolling(win).sum()
    eff = net / path
    r = np.log(c).diff()
    vol = r.rolling(win).std() * math.sqrt(6 * 365)   # 4H bars -> annualised
    t = pd.DataFrame({"year": df["dt"].dt.year, "eff": eff, "vol": vol,
                      "ret": r}).dropna()
    print("\n===== market character by year (4H) =====")
    print("  year   trend-efficiency   annualised vol   year return")
    for y, g in t.groupby("year"):
        print(f"  {y}      {g['eff'].mean():.3f}              {g['vol'].mean():.0%}"
              f"           {math.expm1(g['ret'].sum()):+.0%}")


def main():
    df = ind.enrich(pd.read_parquet("data/4H.parquet"))
    print(f"data span {df['dt'].iloc[0].date()} .. {df['dt'].iloc[-1].date()}")
    for kind in ["volspike", "trig"]:
        for rr in (2.0, 1.0):
            run(df, kind, rr)
    regime_table(df)


if __name__ == "__main__":
    main()
