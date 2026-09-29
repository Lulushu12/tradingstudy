"""Stage-4: build trade streams for strategy specs and run them through the prop account simulator.

Strategy spec:
  dict(name=..., tf="15m",
       sig=("lib", family, variant, htf, bias)  or  ("rsi", len, lo, style, htf, bias),
       exit=dict(sl_atr, tp_r=0, be_r=0, trail=0, trail_mult=0, max_bars=0, sma=None))
"""
import numpy as np
import pandas as pd

from data import SYMBOLS, IS_END, OOS_END, TF_MIN
from engine import simulate, FEE, SLIP
from lab import ctx
import features as fx
import ind
from features import cross_up, cross_dn


def build_signal(cx, spec, include_holdout):
    kind = spec["sig"][0]
    if kind == "lib":
        from stage3 import get_signal
        _, fam, var, htf, bias = spec["sig"]
        s, sl = get_signal(cx, fam, var, htf, bias, include_holdout=include_holdout)
        return s, sl
    if kind == "rsi":
        _, ln, lo, style, htf, bias = spec["sig"]
        r = fx.rsi(cx, ln)
        L, S = (r < lo, r > 100 - lo) if style == "level" else (cross_up(r, lo), cross_dn(r, 100 - lo))
        s = np.zeros(cx.c.size, np.int64)
        s[L] = 1
        s[S] = -1
        if htf == "ltf":
            b = np.where(cx.c > fx.ema(cx, 200), 1, -1)
            s = np.where(b == s, s, 0)
        elif htf != "none":
            b = fx.htf_bias(cx, htf, bias).astype(np.int64)
            s = np.where(b == s, s, 0)
        if not include_holdout:
            s[np.searchsorted(cx.df.index.values, OOS_END.to_datetime64()):] = 0
        return s, None
    raise ValueError(kind)


def strategy_trades(spec, syms=SYMBOLS, include_holdout=False):
    out = []
    ex = spec["exit"]
    for sym in syms:
        cx = ctx(sym, spec["tf"])
        s, sl = build_signal(cx, spec, include_holdout)
        sd = np.maximum(sl, 0.5 * cx.atr) if sl is not None else ex["sl_atr"] * cx.atr
        trail = ex.get("trail", 0)
        src = cx.c
        if ex.get("sma"):
            trail, src = 4, ind.sma(cx.c, ex["sma"])
        tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sd, cx.atr, src,
                      ex.get("tp_r", 0.0), ex.get("be_r", 0.0), trail, ex.get("trail_mult", 0.0),
                      ex.get("max_bars", 0), False, 0.0, 0.0, FEE, SLIP)
        t = pd.DataFrame(tr, columns=["ebar", "xbar", "dir", "entry", "exit", "sl_pct", "r", "reason"])
        t["time"] = cx.df.index[t.ebar.astype(int) + 1]
        t["xtime"] = cx.df.index[t.xbar.astype(int)] + pd.Timedelta(minutes=TF_MIN[spec["tf"]])
        t["sym"] = sym
        t["strat"] = spec["name"]
        out.append(t)
    t = pd.concat(out, ignore_index=True)
    if not include_holdout:
        t = t[t.time < OOS_END]
    return t


def period(t):
    return np.where(t.time < IS_END, "IS", np.where(t.time < OOS_END, "OOS", "HOLDOUT"))


def account(trades, risk=0.005, start=10_000.0, floor=9_400.0, daily_guard=0.025, one_per_symbol=True,
            max_open=99, max_same_dir=99):
    """Continuous account simulation WITHOUT stopping at failure (so we can see the full path).
    Returns per-trade log (taken, pnl), equity curve, and summary incl. how often the static floor
    / daily limit WOULD have been hit if the account restarted each month."""
    t = trades.sort_values(["time", "strat"]).reset_index(drop=True)
    n = len(t)
    ent = t.time.values
    ext = t.xtime.values
    order = np.argsort(np.concatenate([ext, ent]), kind="stable")  # exits first on ties
    kinds = np.concatenate([np.zeros(n, int), np.ones(n, int)])[order]
    ids = np.concatenate([np.arange(n), np.arange(n)])[order]
    times = np.concatenate([ext, ent])[order]
    lev = np.array([10 if s in ("BTCUSDT", "ETHUSDT") else 5 for s in t.sym])
    slp = t.sl_pct.values
    rr = t.r.values
    syms = t.sym.values
    dirs = t.dir.values
    taken = np.zeros(n, bool)
    pnl = np.zeros(n)
    risk_i = np.zeros(n)
    open_syms = {}
    open_risk = 0.0
    bal = start
    day = None
    day_start = bal
    day_real = 0.0
    risk_usd = risk * start
    for k in range(2 * n):
        i = ids[k]
        d = times[k].astype("datetime64[D]")
        if d != day:
            day, day_start, day_real = d, bal, 0.0
        if kinds[k] == 0:
            if not taken[i]:
                continue
            p = risk_i[i] * rr[i]
            pnl[i] = p
            bal += p
            day_real += p
            open_risk -= risk_i[i]
            open_syms.pop(syms[i], None)
        else:
            if one_per_symbol and syms[i] in open_syms:
                continue
            if len(open_syms) >= max_open:
                continue
            if sum(1 for j in open_syms.values() if dirs[j] == dirs[i]) >= max_same_dir:
                continue
            scale = min(1.0, lev[i] * bal / (risk_usd / slp[i]))
            ri = risk_usd * scale
            if day_real - open_risk - ri < -daily_guard * day_start:
                continue
            taken[i] = True
            risk_i[i] = ri
            open_risk += ri
            open_syms[syms[i]] = i
    t = t.assign(taken=taken, pnl=pnl)
    return t


def monthly_report(t, start=10_000.0, floor_dd=0.06):
    tk = t[t.taken]
    m = tk.groupby(tk.xtime.dt.strftime("%Y-%m")).pnl.sum() / start
    # max drawdown of the continuous (non-compounded) equity curve, in % of initial balance
    eq = tk.sort_values("xtime").pnl.cumsum() / start
    dd = (eq.cummax().clip(lower=0) - eq).max()
    # rolling "challenge" view: from each month start, does the path breach -6% before +10%?
    return m, dd


def challenge_stats(t, start=10_000.0, target=0.10, max_loss=0.06, horizon_days=90):
    """Start a new challenge at each week; walk realized P&L until +target or -max_loss (static) or horizon."""
    tk = t[t.taken].sort_values("xtime")
    xt = tk.xtime.values
    cum = np.cumsum(tk.pnl.values) / start
    starts = pd.date_range(tk.time.min().ceil("7D"), tk.xtime.max() - pd.Timedelta(days=horizon_days), freq="7D")
    res = []
    for s in starts:
        a = np.searchsorted(xt, s.to_datetime64())
        b = np.searchsorted(xt, (s + pd.Timedelta(days=horizon_days)).to_datetime64())
        if b <= a:
            res.append("timeout"); continue
        base = cum[a - 1] if a > 0 else 0.0
        path = cum[a:b] - base
        hit_t = np.argmax(path >= target) if (path >= target).any() else None
        hit_l = np.argmax(path <= -max_loss) if (path <= -max_loss).any() else None
        if hit_t is not None and (hit_l is None or hit_t < hit_l):
            res.append(("pass", (xt[a + hit_t] - s.to_datetime64()) / np.timedelta64(1, "D")))
        elif hit_l is not None:
            res.append(("fail", 0))
        else:
            res.append(("timeout", 0))
    o = pd.Series([r[0] if isinstance(r, tuple) else r for r in res])
    days = [r[1] for r in res if isinstance(r, tuple) and r[0] == "pass"]
    return dict(n=len(o), pass_rate=(o == "pass").mean(), fail_rate=(o == "fail").mean(),
                timeout=(o == "timeout").mean(), median_days_to_pass=np.median(days) if days else np.nan)
