"""Cross-asset replication of the frozen 4H volume-spike trend-continuation rule.

Motivation: the BTC-only decay test has poor power. Another year of BTC adds little.
Testing the SAME rule, with ZERO refitting, on assets that were never looked at while
developing it is a much stronger test. It attacks two failure modes at once:

  1. Curve-fit. If the rule only works on the one asset it was built on, the +0.21R is
     selection, not edge.
  2. Priced-in. If the rule is being competed away on BTC specifically (the most liquid,
     most systematically traded crypto), it should look healthier on thinner alts.

Rule is taken verbatim from finalists.make_signals("volspike"):
  close vs EMA200 for trend, volume > 1.8x its 20-bar average, bar closing with the
  trend, stop 1.5*ATR(14), fixed R:R, entry next bar open, one position at a time,
  0.08% round-trip fees. Nothing is re-tuned per asset.

Honesty flags, stated before the numbers:
  - Alt data is OKX, BTC data is Binance. Different venue, different volume convention.
  - These assets are heavily correlated with BTC and with each other. They are NOT
    independent samples. Pooled significance is overstated; the script estimates how
    much by correlating monthly strategy returns across assets.
  - Alts have thinner books and worse real slippage than the 0.08% modelled here, so
    live results would be worse than these numbers on the smaller names.
"""
import warnings; warnings.filterwarnings("ignore")
import glob, math, os
import numpy as np, pandas as pd
import indicators as ind
from finalists import build_trades
from decay import taken_trades, per_year, slope_test, two_sided_p

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_all():
    out = {"BTC": pd.read_parquet(f"{DATA}/4H.parquet")}
    for p in sorted(glob.glob(f"{DATA}/alt_*.parquet")):
        out[os.path.basename(p)[4:-8]] = pd.read_parquet(p)
    return out


def summarise(tr):
    n = len(tr)
    m = tr["net_R"].mean()
    se = tr["net_R"].std(ddof=1) / math.sqrt(n)
    return dict(n=n, wr=(tr["outcome"] == "target").mean(), expR=m, se=se,
                lo=m - 1.96 * se, hi=m + 1.96 * se, t=m / se, p=two_sided_p(m / se))


def monthly_R(tr):
    s = pd.Series(tr["net_R"].values,
                  index=pd.to_datetime(tr["exit_time"], unit="s", utc=True))
    return s.resample("ME").sum()


def main(rr=2.0):
    frames = load_all()
    print(f"===== frozen volspike rule, rr={rr}, single position, no refitting =====")
    print(f"{'asset':6} {'span':24} {'n':>4} {'WR':>6} {'expR':>7} {'95% CI':>18} "
          f"{'p':>6}  {'decay slope':>12}")
    rows, mret = {}, {}
    for sym, raw in frames.items():
        df = ind.enrich(raw)
        tr = taken_trades(build_trades(df, "volspike", rr))
        if len(tr) < 40:
            print(f"{sym:6} too few trades ({len(tr)}), skipped")
            continue
        s = summarise(tr)
        sl = slope_test(tr)
        rows[sym] = s
        mret[sym] = monthly_R(tr)
        span = f"{df['dt'].iloc[0].date()}..{df['dt'].iloc[-1].date()}"
        star = "*" if s["lo"] > 0 else " "
        print(f"{sym:6} {span:24} {s['n']:4d} {s['wr']:6.1%} {s['expR']:+7.3f} "
              f"[{s['lo']:+.3f},{s['hi']:+.3f}] {s['p']:6.3f}{star} "
              f"{sl['slope']:+8.4f}/yr {'' if sl['p']>0.05 else '(sig)'}")

    alts = [k for k in rows if k != "BTC"]
    print(f"\n  assets with positive point estimate: "
          f"{sum(1 for k in rows if rows[k]['expR'] > 0)}/{len(rows)}")
    print(f"  assets whose 95% CI excludes zero:   "
          f"{sum(1 for k in rows if rows[k]['lo'] > 0)}/{len(rows)}")

    # Pooled excluding BTC: the actual out-of-sample question.
    if alts:
        vals = []
        for sym in alts:
            df = ind.enrich(frames[sym])
            vals.append(taken_trades(build_trades(df, "volspike", rr))["net_R"].values)
        v = np.concatenate(vals)
        m = v.mean(); se = v.std(ddof=1) / math.sqrt(len(v))
        print(f"\n  pooled ex-BTC: n={len(v)} expR={m:+.3f} "
              f"[{m-1.96*se:+.3f},{m+1.96*se:+.3f}] p={two_sided_p(m/se):.4f}")

        # correlation deflation: these are not independent samples
        M = pd.DataFrame(mret).dropna(how="all")
        C = M.corr()
        offdiag = C.values[np.triu_indices_from(C.values, 1)]
        rbar = np.nanmean(offdiag)
        k = len(C)
        eff = k / (1 + (k - 1) * rbar) if rbar > -1 / (k - 1) else k
        print(f"  mean pairwise correlation of monthly strategy returns = {rbar:.2f}")
        print(f"  {k} assets behave like roughly {eff:.1f} independent ones; "
              f"correlation-adjusted p is about {two_sided_p((m/se)*math.sqrt(eff/k)):.3f}")


if __name__ == "__main__":
    import sys
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 2.0)
