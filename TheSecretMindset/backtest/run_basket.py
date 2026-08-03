"""Run the declared list across the basket. Same spec, same parameters as the single-symbol run.

Nothing is retuned here. The only change is the number of instruments.

Statistics, per Amendment 3 of the spec:
  primary   calendar-month block bootstrap. Crypto's dominant dependence is cross-sectional
            at a point in time, so 87 coins inside one month are close to one observation,
            not 87. Resampling months respects that; resampling symbols does not.
  secondary naive trade-level bootstrap, printed only to show how much it overstates.
  economic  a run must also keep a positive lower bound with costs doubled to 0.10% per side.
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import Engine                                             # noqa: E402
from strategies import s1_macd, s2_donchian, s3_mfi, s4_outside_bar   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASKET = os.path.join(HERE, "basket")
HOLDOUT_START = pd.Timestamp("2025-01-01", tz="UTC")
BASE_COST = 0.0005
STRESS_COST = 0.0010
MIN_BARS = 250

RUNS_1D = {
    "s1_flat":   lambda d: s1_macd(d, flip=False),
    "s1_flip":   lambda d: s1_macd(d, flip=True),
    "s2_mid":    lambda d: s2_donchian(d, mid_exit=True),
    "s2_band":   lambda d: s2_donchian(d, mid_exit=False),
    "s3_atr":    lambda d: s3_mfi(d, use_stop=True),
    "s3_nostop": lambda d: s3_mfi(d, use_stop=False),
    "s4":        lambda d: s4_outside_bar(d),
}
RUNS_4H = {
    "s1_flat_4h": lambda d: s1_macd(d, flip=False),
    "s1_flip_4h": lambda d: s1_macd(d, flip=True),
}


def load_symbol(path: str):
    d = pd.read_csv(path)
    d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
    d = d[d["dt"] < HOLDOUT_START].reset_index(drop=True)
    return d if len(d) >= MIN_BARS else None


def block_bootstrap(by_key: dict, n: int = 5_000, seed: int = 20260803):
    """Resample whole clusters with replacement and pool their trades."""
    keys = [k for k, v in by_key.items() if len(v)]
    if len(keys) < 8:
        return None
    rng = np.random.default_rng(seed)
    arrs = [np.asarray(by_key[k], dtype=float) for k in keys]
    sizes = np.array([len(a) for a in arrs], dtype=float)
    sums = np.array([a.sum() for a in arrs], dtype=float)
    idx = rng.integers(0, len(keys), size=(n, len(keys)))
    return sums[idx].sum(axis=1) / sizes[idx].sum(axis=1)


def collect(loaded: dict, build, cost: float) -> dict:
    by_month: dict[str, list[float]] = {}
    by_symbol: dict[str, list[float]] = {}
    all_r, year_R, n_sig = [], {}, 0
    for sym, d in loaded.items():
        sig, kw = build(d)
        n_sig += int((sig["entry"] != 0).sum())
        trades, _ = Engine(d, cost_per_side=cost).run(sig, **kw)
        rs = []
        for t in trades:
            if not np.isfinite(t.r_multiple) or t.exit_dt is None:
                continue
            ts = pd.Timestamp(t.exit_dt)
            by_month.setdefault(f"{ts.year}-{ts.month:02d}", []).append(t.r_multiple)
            year_R[ts.year] = year_R.get(ts.year, 0.0) + t.r_multiple
            rs.append(t.r_multiple)
        if rs:
            by_symbol[sym] = rs
            all_r.extend(rs)
    return {"by_month": by_month, "by_symbol": by_symbol, "all_r": np.array(all_r),
            "year_R": year_R, "n_signals": n_sig, "n_symbols": len(loaded)}


def buy_hold_basket(loaded: dict, cost: float = BASE_COST) -> dict:
    rets, dds = [], []
    for _, d in loaded.items():
        eq = d["close"] / d["close"].iloc[0] * (1 - cost) ** 2
        rets.append(100 * (eq.iloc[-1] - 1))
        dds.append(100 * (eq / eq.cummax() - 1).min())
    return {"median_return_pct": round(float(np.median(rets)), 1),
            "mean_return_pct": round(float(np.mean(rets)), 1),
            "median_max_dd_pct": round(float(np.median(dds)), 1),
            "pct_symbols_positive": round(100 * float(np.mean(np.array(rets) > 0)), 1)}


def main():
    files = {"1d": sorted(glob.glob(os.path.join(BASKET, "*_1d.csv"))),
             "4h": sorted(glob.glob(os.path.join(BASKET, "*_4h.csv")))}
    print("=" * 112)
    print("BASKET RUN  |  same spec, same parameters, holdout >= %s never loaded"
          % HOLDOUT_START.date())
    print("=" * 112)

    loaded_by_tf, results, stressed = {}, {}, {}
    for tf, runs in (("1d", RUNS_1D), ("4h", RUNS_4H)):
        loaded = {}
        for f in files[tf]:
            sym = os.path.basename(f).rsplit("_", 1)[0]
            d = load_symbol(f)
            if d is not None:
                loaded[sym] = d
        loaded_by_tf[tf] = loaded
        print(f"{tf}: {len(loaded)} symbols usable of {len(files[tf])}")
        for name, build in runs.items():
            results[name] = collect(loaded, build, BASE_COST)
            stressed[name] = collect(loaded, build, STRESS_COST)

    bh = buy_hold_basket(loaded_by_tf["1d"])
    print("\n" + "=" * 112)
    print("CONTROL: buy and hold every basket member, daily, same costs")
    print("=" * 112)
    print(f"  median symbol return {bh['median_return_pct']}%   mean {bh['mean_return_pct']}%"
          f"   median max drawdown {bh['median_max_dd_pct']}%"
          f"   symbols positive {bh['pct_symbols_positive']}%")

    print("\n" + "=" * 112)
    print("POOLED RESULTS  (mean R per trade; month-block CI is the one that counts)")
    print("=" * 112)
    hdr = (f"{'run':12s}{'trades':>8s}{'meanR':>9s}   {'naive 95% CI':^20s}  "
           f"{'MONTH-BLOCK 95% CI':^22s}  {'Bonferroni':^22s} {'%sym+':>7s}")
    print(hdr)
    print("-" * len(hdr))
    rng = np.random.default_rng(11)
    verdicts, table = {}, []
    for name, R in results.items():
        r = R["all_r"]
        if len(r) < 10:
            print(f"{name:12s}{len(r):8d}   too few trades")
            verdicts[name] = "UNDECIDABLE (too few trades)"
            continue
        nb = rng.choice(r, size=(10_000, len(r)), replace=True).mean(axis=1)
        nlo, nhi = np.percentile(nb, [2.5, 97.5])
        mb = block_bootstrap(R["by_month"])
        mlo, mhi = np.percentile(mb, [2.5, 97.5])
        blo, bhi = np.percentile(mb, [0.625, 99.375])       # 4 strategy families
        exps = [np.mean(v) for v in R["by_symbol"].values()]
        pos = 100 * float(np.mean(np.array(exps) > 0))

        sb = block_bootstrap(stressed[name]["by_month"])
        slo = float(np.percentile(sb, 2.5)) if sb is not None else np.nan
        s_mean = stressed[name]["all_r"].mean() if len(stressed[name]["all_r"]) else np.nan

        print(f"{name:12s}{len(r):8d}{r.mean():+9.3f}   [{nlo:+7.3f},{nhi:+7.3f}]  "
              f"  [{mlo:+7.3f},{mhi:+7.3f}]    [{blo:+7.3f},{bhi:+7.3f}]  {pos:6.1f}%")

        if blo <= 0:
            v = "DEAD (month-block CI includes 0 after correction)"
        elif slo <= 0:
            v = f"FRAGILE (dies at 0.10%/side: meanR {s_mean:+.3f}, lower bound {slo:+.3f})"
        else:
            v = "survives both corrections and doubled costs"
        verdicts[name] = v
        table.append({"run": name, "trades": len(r), "mean_R": round(float(r.mean()), 4),
                      "month_lo": round(float(mlo), 4), "month_hi": round(float(mhi), 4),
                      "bonf_lo": round(float(blo), 4), "bonf_hi": round(float(bhi), 4),
                      "stress_mean_R": round(float(s_mean), 4),
                      "stress_lo": round(float(slo), 4),
                      "pct_symbols_positive": round(pos, 1), "verdict": v})

    print("\n" + "=" * 112)
    print("VERDICT")
    print("=" * 112)
    for k, v in verdicts.items():
        print(f"  {k:12s} {v}")

    print("\n" + "=" * 112)
    print("REGIME: pooled net R by calendar year")
    print("=" * 112)
    print(pd.DataFrame({k: v["year_R"] for k, v in results.items()})
          .T.sort_index(axis=1).round(1).to_string())

    if "s4" in results:
        s4 = results["s4"]
        print("\n" + "=" * 112)
        print("S4 ACROSS THE BASKET (the question one symbol could not answer)")
        print("=" * 112)
        print(f"  entry signals across {s4['n_symbols']} symbols: {s4['n_signals']}")
        print(f"  completed trades: {len(s4['all_r'])}")
        if len(s4["all_r"]):
            print(f"  mean R {s4['all_r'].mean():+.3f}   "
                  f"win rate {100 * float(np.mean(s4['all_r'] > 0)):.1f}%")

    out = os.path.join(HERE, "results")
    os.makedirs(out, exist_ok=True)
    pd.DataFrame(table).to_csv(os.path.join(out, "basket_summary.csv"), index=False)
    print(f"\nwritten to {out}/basket_summary.csv")


if __name__ == "__main__":
    main()
