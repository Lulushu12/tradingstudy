"""Breakoutprop 1-step $10k account simulator.

Rules modelled:
- Static max drawdown: account fails if equity < 9,400.
- Daily loss limit 3% of the day's starting balance (day = UTC). We enforce a guard: a new trade is
  only opened if (realized today) - (open risk) - (new risk) stays above -daily_guard. So the
  3% limit cannot be hit by design unless slippage beyond the stop is extreme.
- Leverage caps: 10x BTC/ETH, 5x others. Position notional = risk$ / stop%. If that exceeds the
  cap, the position is shrunk (so that trade's P&L in $ shrinks proportionally).
- Risk per trade is a fixed % of the INITIAL balance (fits a static drawdown).
- Optional: max concurrent positions.
"""
import numpy as np
import pandas as pd

LEV = {"BTCUSDT": 10, "ETHUSDT": 10}
DEFAULT_LEV = 5


def simulate_account(trades, risk=0.005, start_bal=10_000.0, floor=9_400.0, daily_limit=0.03,
                     daily_guard=0.025, max_concurrent=99, target=None, stop_at_fail=True):
    """trades: DataFrame with time, xtime, sym, r, sl_pct. Returns dict of results + trade log."""
    t = trades.sort_values("time").reset_index(drop=True)
    events = []
    for i, row in enumerate(t.itertuples(index=False)):
        events.append((pd.Timestamp(row.time), 1, i))
        events.append((pd.Timestamp(row.xtime), 0, i))
    events.sort(key=lambda e: (e[0], e[1]))  # exits before entries at the same timestamp

    bal = start_bal
    open_risk = {}
    taken = np.zeros(len(t), bool)
    pnl = np.zeros(len(t))
    day = None
    day_start = bal
    day_real = 0.0
    failed_at = None
    hit_target_at = None
    risk_usd = risk * start_bal
    peak = bal
    maxdd = 0.0
    for ts, kind, i in events:
        d = ts.floor("1D")
        if d != day:
            day, day_start, day_real = d, bal, 0.0
        if kind == 0:
            if not taken[i]:
                continue
            row = t.iloc[i]
            p = open_risk.pop(i) * row.r
            pnl[i] = p
            bal += p
            day_real += p
            peak = max(peak, bal)
            maxdd = max(maxdd, (peak - bal) / start_bal)
            if bal < floor or day_real < -daily_limit * day_start:
                if failed_at is None:
                    failed_at = ts
                if stop_at_fail:
                    break
            if target is not None and hit_target_at is None and bal >= start_bal * (1 + target):
                hit_target_at = ts
                if stop_at_fail:
                    break
        else:
            if len(open_risk) >= max_concurrent:
                continue
            row = t.iloc[i]
            lev = LEV.get(row.sym, DEFAULT_LEV)
            notional = risk_usd / row.sl_pct
            scale = min(1.0, lev * bal / notional)
            this_risk = risk_usd * scale
            worst = day_real - sum(open_risk.values()) - this_risk
            if worst < -daily_guard * day_start:
                continue
            # also never let open risk push below the static floor
            if bal - sum(open_risk.values()) - this_risk < floor:
                continue
            open_risk[i] = this_risk
            taken[i] = True
    t = t.assign(taken=taken, pnl=pnl)
    tk = t[t.taken]
    monthly = tk.groupby(pd.to_datetime(tk.xtime, utc=True).dt.strftime("%Y-%m")).pnl.sum() / start_bal
    return dict(final=bal, ret=(bal - start_bal) / start_bal, maxdd=maxdd, failed_at=failed_at,
                hit_target_at=hit_target_at, monthly=monthly, trades=tk, n=len(tk))


def eval_pass_rate(trades, risk, target=0.10, starts_every="7D", horizon_days=120, **kw):
    """Start a fresh challenge every `starts_every`; report pass / fail / timeout rates and days to pass."""
    t = trades.sort_values("time")
    tt = pd.to_datetime(t.time, utc=True)
    starts = pd.date_range(tt.min().ceil("1D"), tt.max() - pd.Timedelta(days=30), freq=starts_every)
    res = []
    for s in starts:
        sub = t[(tt >= s) & (tt < s + pd.Timedelta(days=horizon_days))]
        if len(sub) == 0:
            continue
        r = simulate_account(sub, risk=risk, target=target, **kw)
        if r["hit_target_at"] is not None:
            res.append(("pass", (r["hit_target_at"] - s).days))
        elif r["failed_at"] is not None:
            res.append(("fail", (r["failed_at"] - s).days))
        else:
            res.append(("timeout", horizon_days))
    df = pd.DataFrame(res, columns=["outcome", "days"])
    return dict(pass_rate=(df.outcome == "pass").mean(), fail_rate=(df.outcome == "fail").mean(),
                median_days_pass=df[df.outcome == "pass"].days.median(), n=len(df))


def summarize(res):
    m = res["monthly"]
    return dict(n=res["n"], total=res["ret"], maxdd=res["maxdd"], failed=res["failed_at"] is not None,
                avg_month=m.mean(), med_month=m.median(), worst_month=m.min(), pct_pos_months=(m > 0).mean(),
                months_ge_10=(m >= 0.10).mean())
