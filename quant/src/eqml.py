"""Cross-sectional ML on the Nasdaq-100 universe, volume-heavy feature set.

Why this setup rather than a repeat of the crypto work:
  - COST. Liquid US large caps round-trip for roughly 0.05% all-in versus 0.12%
    on crypto perps, and the crypto study died on cost drag.
  - BREADTH. Crypto gave 5 assets at rho=0.30, so 2.27 effective independent
    streams. Ninety-plus names with market beta removed give far more, and
    breadth is what converts a small edge into a usable Sharpe.

Design carried over from the crypto lessons:
  - long/short legs weighted by INVERSE VOLATILITY, not equal dollars. Equal
    dollars silently shorts the high-vol names and that tilt swamped the signal
    last time.
  - purged, embargoed walk-forward, reported next to the in-sample fit so the
    hindsight premium is always visible.
  - costs charged on realised turnover, not on gross notional.

Survivorship bias: current index membership over history. Long/short ranking
inside the surviving universe is far less exposed than a long-only test, but the
result is still an upper bound. Stated in every conclusion.
"""
import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "equity")
REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")

COST_RT = 0.0005          # 5 bps round trip, conservative for NDX large caps

PARAMS = dict(objective="regression", learning_rate=0.03, num_leaves=16,
              max_depth=4, min_data_in_leaf=500, feature_fraction=0.6,
              bagging_fraction=0.8, bagging_freq=1, lambda_l2=20.0,
              verbosity=-1, num_threads=4)


def load(min_names=30, start="1998-01-01"):
    df = pd.read_parquet(os.path.join(DATA, "ndx_daily.parquet"))
    df = df[df.dt >= pd.Timestamp(start, tz="UTC")].copy()
    # adjust OHLC by the split/dividend factor so geometry and returns agree
    f = (df["adjclose"] / df["close"]).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    for c in ("open", "high", "low"):
        df[c] = df[c] * f
    df["close"] = df["adjclose"]
    df["dollar_vol"] = df["close"] * df["volume"]
    df = df.sort_values(["symbol", "dt"]).reset_index(drop=True)
    cnt = df.groupby("dt")["symbol"].transform("size")
    df = df[cnt >= min_names].reset_index(drop=True)
    return df


def features(df):
    g = df.groupby("symbol", group_keys=False)
    c, h, l, o = df["close"], df["high"], df["low"], df["open"]
    v, dv = df["volume"], df["dollar_vol"]
    out = pd.DataFrame({"dt": df["dt"], "symbol": df["symbol"], "close": c})

    ret1 = g["close"].pct_change()
    out["ret1"] = ret1

    # ---- price/momentum over several horizons
    for n in (2, 5, 10, 21, 63, 126, 252):
        out[f"mom{n}"] = g["close"].pct_change(n)
    # momentum skipping the last week (classic 12-1 style, computed causally)
    out["mom252_21"] = g["close"].pct_change(252) - g["close"].pct_change(21)

    # ---- realised volatility and its structure
    for n in (5, 21, 63):
        out[f"vol{n}"] = g.apply(lambda x: x["close"].pct_change().rolling(n).std())\
            .reset_index(drop=True) if False else ret1.groupby(df["symbol"]).transform(
                lambda s: s.rolling(n).std())
    out["vol_ratio"] = out["vol5"] / out["vol63"].replace(0, np.nan)
    out["vol_of_vol"] = out["vol21"].groupby(df["symbol"]).transform(
        lambda s: s.rolling(63).std())

    # ---- VOLUME BLOCK (the part specifically asked for)
    out["dollar_vol"] = dv
    for n in (5, 21, 63):
        ma = dv.groupby(df["symbol"]).transform(lambda s: s.rolling(n).mean())
        out[f"dv_ratio{n}"] = dv / ma.replace(0, np.nan)
    out["dv_z21"] = dv.groupby(df["symbol"]).transform(
        lambda s: (s - s.rolling(21).mean()) / s.rolling(21).std().replace(0, np.nan))
    out["vol_trend"] = (dv.groupby(df["symbol"]).transform(lambda s: s.rolling(5).mean())
                        / dv.groupby(df["symbol"]).transform(lambda s: s.rolling(63).mean()).replace(0, np.nan))
    # Amihud illiquidity: price impact per dollar traded
    out["amihud"] = (ret1.abs() / dv.replace(0, np.nan))
    out["amihud21"] = out["amihud"].groupby(df["symbol"]).transform(
        lambda s: s.rolling(21).mean())
    # signed volume: volume concentrated on up days vs down days
    sgn_dv = np.sign(ret1) * dv
    for n in (5, 21):
        out[f"obv{n}"] = sgn_dv.groupby(df["symbol"]).transform(
            lambda s: s.rolling(n).sum()) / dv.groupby(df["symbol"]).transform(
            lambda s: s.rolling(n).sum()).replace(0, np.nan)
    # volume-return correlation: does volume confirm or fade the move?
    out["volret_corr"] = ret1.groupby(df["symbol"]).transform(
        lambda s: s.rolling(21).corr(dv.loc[s.index]))
    # turnover shock vs price move: heavy volume with no move = absorption
    out["absorb"] = out["dv_z21"] / (ret1.abs() / out["vol21"].replace(0, np.nan)).replace(0, np.nan)

    # ---- bar geometry, overnight vs intraday (a documented real split)
    rng_ = (h - l).replace(0, np.nan)
    out["intraday_ret"] = (c - o) / o
    out["overnight_ret"] = o / g["close"].shift(1) - 1
    for n in (5, 21, 63):
        out[f"overnight_sum{n}"] = out["overnight_ret"].groupby(df["symbol"]).transform(
            lambda s: s.rolling(n).sum())
        out[f"intraday_sum{n}"] = out["intraday_ret"].groupby(df["symbol"]).transform(
            lambda s: s.rolling(n).sum())
    out["close_loc"] = (c - l) / rng_
    out["up_wick"] = (h - np.maximum(c, o)) / rng_
    out["dn_wick"] = (np.minimum(c, o) - l) / rng_
    out["range_pct"] = rng_ / c
    out["range_z"] = out["range_pct"].groupby(df["symbol"]).transform(
        lambda s: (s - s.rolling(63).mean()) / s.rolling(63).std().replace(0, np.nan))
    out["gap_z"] = out["overnight_ret"].groupby(df["symbol"]).transform(
        lambda s: (s - s.rolling(63).mean()) / s.rolling(63).std().replace(0, np.nan))

    # ---- position within trailing range
    for n in (21, 63, 252):
        hh = h.groupby(df["symbol"]).transform(lambda s: s.rolling(n).max())
        ll = l.groupby(df["symbol"]).transform(lambda s: s.rolling(n).min())
        out[f"pos{n}"] = (c - ll) / (hh - ll).replace(0, np.nan)
        out[f"to_hi{n}"] = (hh - c) / c
    out["dow"] = pd.DatetimeIndex(df["dt"]).dayofweek
    out["dom"] = pd.DatetimeIndex(df["dt"]).day
    return out


NON_FEAT = {"dt", "symbol", "close", "ret1"}


def feat_cols(f):
    return [c for c in f.columns if c not in NON_FEAT]


def cs_normalise(f, cols):
    """Cross-sectional rank each feature within each day. Removes level and
    market-wide drift, which is what makes this a relative-value model."""
    g = f.groupby("dt")
    out = f[["dt", "symbol"]].copy()
    for c in cols:
        r = g[c].rank(pct=True)
        out[c] = r - 0.5
    return out


def forward_target(f, h):
    """Forward h-day return, cross-sectionally demeaned (market neutral)."""
    fwd = f.groupby("symbol")["close"].shift(-h) / f["close"] - 1
    tmp = pd.DataFrame({"dt": f["dt"], "y": fwd})
    tmp["y"] = tmp["y"] - tmp.groupby("dt")["y"].transform("mean")
    return tmp["y"].values


def walkforward(X, y, dates, train_years=6, step_months=6, embargo=21):
    dts = pd.DatetimeIndex(pd.Series(dates).values)
    if dts.tz is None:
        dts = dts.tz_localize("UTC")
    pred = np.full(len(y), np.nan)
    periods = pd.period_range(dts.min(), dts.max(), freq="M")
    i = train_years * 12
    while i < len(periods):
        tr_hi = periods[i].start_time.tz_localize("UTC")
        te_hi = periods[min(i + step_months, len(periods) - 1)].start_time.tz_localize("UTC")
        if te_hi <= tr_hi:
            break
        trm = (dts < tr_hi - pd.Timedelta(days=embargo)) & np.isfinite(y)
        tem = (dts >= tr_hi) & (dts < te_hi)
        if trm.sum() > 20000 and tem.sum() > 0:
            b = lgb.train(PARAMS, lgb.Dataset(X[trm], label=y[trm]), 300)
            pred[tem] = b.predict(X[tem])
        i += step_months
    return pred


def ls_portfolio(f, score, hold, frac=0.1, cost=COST_RT):
    """Risk-parity long/short, rebalanced every `hold` days."""
    d = f[["dt", "symbol", "close"]].copy()
    d["score"] = score
    d["vol"] = d.groupby("symbol")["close"].pct_change().groupby(
        d["symbol"]).transform(lambda s: s.rolling(63).std())
    days = np.sort(d["dt"].unique())
    reb = days[::hold]
    piv_c = d.pivot_table(index="dt", columns="symbol", values="close",
                          dropna=False)
    piv_s = d.pivot_table(index="dt", columns="symbol", values="score",
                          dropna=False).reindex(piv_c.index)
    piv_v = d.pivot_table(index="dt", columns="symbol", values="vol",
                          dropna=False).reindex(piv_c.index)
    reb = [t for t in reb if t in piv_c.index]

    rets, dates = [], []
    w_prev = pd.Series(0.0, index=piv_c.columns)
    for i in range(len(reb) - 1):
        t0, t1 = reb[i], reb[i + 1]
        s = piv_s.loc[t0].dropna()
        v = piv_v.loc[t0]
        s = s[v.reindex(s.index).notna() & (v.reindex(s.index) > 0)]
        if len(s) < 20:
            continue
        k = max(int(len(s) * frac), 3)
        longs = s.nlargest(k).index
        shorts = s.nsmallest(k).index
        iv = 1.0 / v
        wl = iv[longs] / iv[longs].sum()
        ws = iv[shorts] / iv[shorts].sum()
        w = pd.Series(0.0, index=piv_c.columns)
        w[longs] = wl
        w[shorts] = -ws * (wl * v[longs]).sum() / max((ws * v[shorts]).sum(), 1e-12)
        w = w / w.abs().sum()
        pr = piv_c.loc[t1] / piv_c.loc[t0] - 1
        ok = pr.notna() & (w != 0)
        gross = float((w[ok] * pr[ok]).sum())
        turn = float((w - w_prev).abs().sum())
        rets.append(gross - turn * cost / 2)
        dates.append(t1)
        w_prev = w
    return pd.Series(rets, index=pd.DatetimeIndex(dates))


def summarise(r, hold, label):
    if len(r) < 12:
        return None
    py = 252 / hold
    mu, sd = r.mean() * py, r.std(ddof=0) * np.sqrt(py)
    eq = (1 + r).cumprod()
    dd = float(((eq.cummax() - eq) / eq.cummax()).max())
    mo = eq.resample("ME").last().pct_change().dropna()
    return {"label": label, "hold": hold, "n": len(r), "ann_ret": mu,
            "ann_vol": sd, "sharpe": mu / sd if sd > 0 else np.nan,
            "maxDD": dd, "hit": float((r > 0).mean()),
            "mean_mo": float(mo.mean()), "worst_mo": float(mo.min()),
            "pos_mo": float((mo > 0).mean())}


def main():
    print("loading universe ...")
    df = load()
    print(f"  {df.symbol.nunique()} symbols, {len(df):,} rows, "
          f"{df.dt.min().date()} -> {df.dt.max().date()}")
    f = features(df)
    cols = feat_cols(f)
    print(f"  {len(cols)} features "
          f"({sum(1 for c in cols if any(k in c for k in ('dv','vol','amihud','obv','absorb')))} volume-derived)")
    fx = cs_normalise(f, cols)
    X = fx[cols].values.astype(np.float32)
    X = np.nan_to_num(X, nan=0.0)

    rows = []
    for h in (1, 5, 21):
        y = forward_target(f, h)
        ok = np.isfinite(y)
        print(f"\n=== horizon {h}d ===")
        # in-sample
        b = lgb.train(PARAMS, lgb.Dataset(X[ok], label=y[ok]), 300)
        p_is = b.predict(X)
        # walk-forward
        p_wf = walkforward(X, y, f["dt"])
        for tag, p in (("IS", p_is), ("WF", p_wf)):
            valid = np.isfinite(p)
            sc = np.where(valid, p, np.nan)
            r = ls_portfolio(f, sc, hold=h)
            s = summarise(r, h, f"{tag} h={h}")
            if s:
                rows.append(s)
                print(f"  {tag}: ann {100*s['ann_ret']:+6.1f}%  vol {100*s['ann_vol']:5.1f}%  "
                      f"Sharpe {s['sharpe']:+5.2f}  maxDD {100*s['maxDD']:5.1f}%  "
                      f"mean/mo {100*s['mean_mo']:+5.2f}%  pos {100*s['pos_mo']:.0f}%")
        imp = pd.Series(b.feature_importance("gain"), index=cols).sort_values(ascending=False)
        print(f"  top features: {', '.join(imp.head(8).index)}")

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(REP, "eqml.csv"), index=False)
    print("\nsaved reports/eqml.csv")


if __name__ == "__main__":
    main()
