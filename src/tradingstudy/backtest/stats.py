"""Performance statistics, deflated Sharpe ratio and the prop-firm Monte Carlo (PROTOCOL sections 8-9)."""
from __future__ import annotations

import math

import numba as nb
import numpy as np
import pandas as pd
from scipy import stats as sps

from tradingstudy.backtest.engine import CANCELLED, EXPIRED, FILLED
from tradingstudy.backtest.portfolio import DAILY_GUARD, DAILY_LIMIT, MAX_DD_LEVEL, RISK

FOLDS = [("2023H1", "2023-01-01", "2023-07-01"), ("2023H2", "2023-07-01", "2024-01-01"),
         ("2024H1", "2024-01-01", "2024-07-01"), ("2024H2", "2024-07-01", "2025-01-01"),
         ("2025H1", "2025-01-01", "2025-07-01"), ("2025H2", "2025-07-01", "2025-11-15")]
WF_START, WF_END = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2025-11-15", tz="UTC")


def core(r: pd.Series) -> dict:
    r = r.dropna()
    n = len(r)
    if n == 0:
        return {"n": 0}
    pos, neg = r[r > 0].sum(), -r[r < 0].sum()
    sd = r.std(ddof=1) if n > 1 else np.nan
    losses = (r <= 0).astype(int).to_numpy()
    streak = cur = 0
    for x in losses:
        cur = cur + 1 if x else 0
        streak = max(streak, cur)
    return {"n": n, "exp_R": float(r.mean()), "win_rate": float((r > 0).mean()), "pf": float(pos / neg) if neg > 0 else np.inf,
            "sd_R": float(sd), "sr": float(r.mean() / sd) if sd and sd > 0 else np.nan, "total_R": float(r.sum()),
            "max_loss_streak": int(streak), "skew": float(sps.skew(r)) if n > 2 else np.nan,
            "kurt": float(sps.kurtosis(r, fisher=False)) if n > 3 else np.nan}


def summarize(s: pd.DataFrame, days: float) -> dict:
    """s: portfolio output restricted to the evaluation window (taken orders only are used)."""
    t = s[s["taken"]]
    f = t[t["status"] == FILLED]
    out = core(f["net_R"])
    unfilled = t[t["status"].isin([CANCELLED, EXPIRED])]
    missed = unfilled[unfilled["touched"] == 1]
    out.update({
        "orders": len(t), "fill_rate": len(f) / len(t) if len(t) else np.nan,
        "missed_fills": len(missed), "missed_winners": int((missed["missed_hyp_net_R"] > 0).sum()),
        "missed_hyp_exp_R": float(missed["missed_hyp_net_R"].mean()) if len(missed) else np.nan,
        "fee_R": float(f["fee_R"].mean()) if len(f) else np.nan, "slip_R": float(f["slip_R"].mean()) if len(f) else np.nan,
        "gross_R": float(f["gross_R"].mean()) if len(f) else np.nan,
        "trades_per_day": len(f) / days if days else np.nan,
        "timeouts": int((f["exit_reason"] == 3).sum()),
    })
    if len(f):
        m = f.groupby(pd.to_datetime(f["fill_ts"], utc=True).dt.to_period("M"))["net_R"].sum()
        out["months_positive"] = float((m > 0).mean())
    return out


def deflated_sharpe(sr: float, n: int, skew: float, kurt: float, n_trials: int, sr_var_trials: float) -> float:
    """Bailey & Lopez de Prado (2014). sr = per-trade Sharpe of the candidate, n = trades, n_trials = configurations
    tried, sr_var_trials = variance of per-trade Sharpe across the trials. Returns the probability that the true
    Sharpe exceeds the best Sharpe expected from n_trials attempts at pure noise."""
    if n < 3 or not np.isfinite(sr) or n_trials < 1:
        return np.nan
    g = 0.5772156649
    if n_trials > 1:
        sr0 = math.sqrt(max(sr_var_trials, 0.0)) * ((1 - g) * sps.norm.ppf(1 - 1 / n_trials) + g * sps.norm.ppf(1 - 1 / (n_trials * math.e)))
    else:
        sr0 = 0.0
    denom = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr**2, 1e-12))
    return float(sps.norm.cdf((sr - sr0) * math.sqrt(n - 1) / denom))


@nb.njit(cache=True)
def _mc_paths(flat, offs, picks, risk, guard, limit, max_level):
    P, H = picks.shape
    first_daily = np.full(P, np.inf)
    first_max = np.full(P, np.inf)
    final = np.empty(P)
    for p in range(P):
        eq = 1.0
        for k in range(H):
            di = picks[p, k]
            start_eq = eq
            day_pnl = 0.0
            for q in range(offs[di], offs[di + 1]):
                if day_pnl <= guard * start_eq:
                    break
                x = flat[q] * risk * eq
                eq += x
                day_pnl += x
            if day_pnl <= limit * start_eq and first_daily[p] == np.inf:
                first_daily[p] = k + 1
            if eq <= max_level and first_max[p] == np.inf:
                first_max[p] = k + 1
        final[p] = eq
    return first_daily, first_max, final


def prop_monte_carlo(f: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, paths: int = 10_000,
                     horizons=(30, 60, 90), seed: int = 0) -> dict:
    """Block bootstrap by calendar day of filled trades (net_R, in exit order). Each path draws whole days with
    replacement, applies the -2% daily guard, 0.5% risk of current equity, and records the first breach of the 3%
    daily limit (realized, start-of-day balance) and of the 6% static max drawdown."""
    rng = np.random.default_rng(seed)
    days = pd.date_range(start.normalize(), end.normalize() - pd.Timedelta(days=1), freq="D", tz="UTC")
    exit_day = pd.to_datetime(f["end_ts"], utc=True).dt.normalize()
    byday = {d: g.sort_values("end_ts")["net_R"].to_numpy() for d, g in f.groupby(exit_day)}
    seqs = [byday.get(d, np.array([])) for d in days]
    H = max(horizons)
    flat = np.concatenate([np.asarray(x, dtype=np.float64) for x in seqs]) if seqs else np.zeros(0)
    offs = np.r_[0, np.cumsum([len(x) for x in seqs])].astype(np.int64)
    picks = rng.integers(0, len(seqs), (paths, H))
    first_daily, first_max, final = _mc_paths(flat, offs, picks, RISK, DAILY_GUARD, DAILY_LIMIT, MAX_DD_LEVEL)
    out = {}
    for h in horizons:
        out[f"p_daily_breach_{h}d"] = float((first_daily <= h).mean())
        out[f"p_max_breach_{h}d"] = float((first_max <= h).mean())
        out[f"p_any_breach_{h}d"] = float((np.minimum(first_daily, first_max) <= h).mean())
    out["median_return_90d"] = float(np.median(final) - 1)
    return out
