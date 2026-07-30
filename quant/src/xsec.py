"""Cross-sectional (relative-value) search across the 5-asset universe.

Rationale: crypto majors share one dominant factor (BTC beta). Time-series
directional bets are bets on that factor, and its volatility is what makes the
6% drawdown budget unreachable. Ranking assets AGAINST each other and trading
the spread cancels the common factor, so a weak signal can produce a much
higher Sharpe than the same signal traded outright.

Design discipline: BTC-only was used for the time-series search. Here all five
assets are needed by construction, so this section is fit on TRAIN and judged
on TEST, and the HOLDOUT stays sealed either way.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import features as F      # noqa: E402
import engine as E        # noqa: E402

SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def panel(tf="1h", block="TRAIN", syms=SYMS, unlock=None):
    """Aligned feature panel: dict[symbol] -> feature frame on a common index."""
    out = {}
    for s in syms:
        bars, m1 = D.load(s, tf, block, unlock=unlock)
        f = F.build(bars, m1, tf)
        f = f[f["tradeable"]].reset_index(drop=True)
        out[s] = f.set_index("dt")
    common = None
    for s in out:
        idx = out[s].index
        common = idx if common is None else common.intersection(idx)
    for s in out:
        out[s] = out[s].loc[common]
    return out, common


def xs_matrix(pan, col):
    return pd.DataFrame({s: pan[s][col] for s in pan})


def xs_ic(pan, horizons=(1, 2, 4, 8, 24, 48), cols=None):
    """Cross-sectional rank IC: rank assets by feature, correlate with the
    cross-sectionally demeaned forward return."""
    syms = list(pan)
    close = xs_matrix(pan, "close")
    cols = cols or [c for c in F.feature_cols(pan[syms[0]]) if c in pan[syms[0]]]
    rows = []
    for h in horizons:
        fwd = np.log(close.shift(-h) / close)
        fwd = fwd.sub(fwd.mean(axis=1), axis=0)      # market neutral target
        for c in cols:
            X = xs_matrix(pan, c)
            if X.isna().all().all():
                continue
            xr = X.rank(axis=1)
            xr = xr.sub(xr.mean(axis=1), axis=0)
            fr = fwd.rank(axis=1)
            fr = fr.sub(fr.mean(axis=1), axis=0)
            num = (xr * fr).sum(axis=1)
            den = np.sqrt((xr ** 2).sum(axis=1) * (fr ** 2).sum(axis=1))
            ic = (num / den.replace(0, np.nan)).dropna()
            if len(ic) < 500:
                continue
            rows.append({"feature": c, "h": h, "ic": float(ic.mean()),
                         "ic_t": float(ic.mean() / (ic.std(ddof=0) / np.sqrt(len(ic)))),
                         "n": len(ic)})
    return pd.DataFrame(rows)


def ls_backtest(pan, col, h, hold_bars=None, n_side=2, cost=2 * (E.TAKER + E.SLIP),
                sign=1.0):
    """Equal-notional long/short portfolio, rebalanced every `hold_bars`.

    Returns per-rebalance net portfolio returns. Costs are charged on the
    turnover actually incurred, not on gross notional.
    """
    hold_bars = hold_bars or h
    close = xs_matrix(pan, "close")
    X = xs_matrix(pan, col) * sign
    idx = np.arange(0, len(close) - hold_bars, hold_bars)

    rets, dates, w_prev = [], [], pd.Series(0.0, index=close.columns)
    for i in idx:
        x = X.iloc[i]
        if x.notna().sum() < 4:
            continue
        r = x.rank()
        w = pd.Series(0.0, index=close.columns)
        w[r.nlargest(n_side).index] = 1.0 / n_side
        w[r.nsmallest(n_side).index] = -1.0 / n_side
        # forward return over the holding period, entry at next bar open
        o = pd.DataFrame({s: pan[s]["open_next"] for s in pan})
        entry = o.iloc[i]
        exit_ = o.iloc[i + hold_bars]
        pr = (exit_ / entry - 1.0)
        gross = float((w * pr).sum())
        turnover = float((w - w_prev).abs().sum())
        rets.append(gross - turnover * (E.TAKER + E.SLIP))
        dates.append(close.index[i + hold_bars])
        w_prev = w
    return pd.Series(rets, index=pd.DatetimeIndex(dates))


def summarise(r, per_year):
    if len(r) < 10:
        return {}
    eq = (1 + r).cumprod()
    peak = eq.cummax()
    dd = ((peak - eq) / peak).max()
    mu = r.mean() * per_year
    sd = r.std(ddof=0) * np.sqrt(per_year)
    return {"n": len(r), "mean_per_trade": r.mean(), "ann_ret": mu,
            "ann_vol": sd, "sharpe": mu / sd if sd > 0 else np.nan,
            "max_dd": dd, "hit": float((r > 0).mean()),
            "total": float(eq.iloc[-1] - 1)}


def main():
    for tf, per_year_bars in [("1h", 8760), ("4h", 2190), ("30min", 17520)]:
        print(f"\n=================== {tf} ===================")
        pan_tr, _ = panel(tf, "TRAIN")
        pan_te, _ = panel(tf, "TEST")
        ic = xs_ic(pan_tr)
        if not len(ic):
            continue
        ic["abs"] = ic["ic"].abs()
        top = ic.sort_values("abs", ascending=False).head(15)
        print(f"{'feature':<18}{'h':>4}{'xsIC':>9}{'t':>8}   -> TEST xsIC")
        ic_te = xs_ic(pan_te, horizons=tuple(sorted(top['h'].unique())),
                      cols=list(top["feature"].unique()))
        m = ic_te.set_index(["feature", "h"])["ic"].to_dict()
        keep = []
        for _, r in top.iterrows():
            t_ic = m.get((r.feature, r.h), np.nan)
            same = np.isfinite(t_ic) and np.sign(t_ic) == np.sign(r.ic)
            print(f"{r.feature:<18}{r.h:>4}{r.ic:>9.4f}{r.ic_t:>8.1f}   "
                  f"{t_ic:>+.4f} {'OK' if same else '..'}")
            if same:
                keep.append((r.feature, int(r.h), np.sign(r.ic)))

        print(f"\nsign-stable cross-sectional signals: {len(keep)}/{len(top)}")
        for feat, h, sg in keep[:6]:
            for nside in (1, 2):
                rtr = ls_backtest(pan_tr, feat, h, n_side=nside, sign=sg)
                rte = ls_backtest(pan_te, feat, h, n_side=nside, sign=sg)
                py = per_year_bars / h
                a, b = summarise(rtr, py), summarise(rte, py)
                if not a or not b:
                    continue
                print(f"  LS {feat:<16} h={h:<3} n_side={nside}  "
                      f"TRAIN sharpe {a['sharpe']:+.2f} ret {100*a['ann_ret']:+6.1f}% "
                      f"dd {100*a['max_dd']:4.1f}%  |  "
                      f"TEST sharpe {b['sharpe']:+.2f} ret {100*b['ann_ret']:+6.1f}% "
                      f"dd {100*b['max_dd']:4.1f}%")


if __name__ == "__main__":
    main()
