"""Phase 1 walk-forward for Categorical Fade v1.

Rules exactly per CATEGORICAL_SPEC.md. Costs and kill thresholds exactly per
AUDIT_COMMITMENTS_CATEGORICAL.md. No optimization, no parameter search.

Differences from Gate 0, all of them tightenings:
  1. The ER threshold is CAUSAL (expanding-window 10th percentile), not a pooled
     full-sample decile edge.
  2. Both-touched bars resolve as full losses instead of being excluded.
  3. One position at a time; overlapping signals are skipped and counted.
  4. Real sequencing: compounding equity, drawdown, losing streaks.
  5. Slippage on every fill.

Guards
------
No look-ahead: the signal on bar t uses only closed-bar values up to t, the entry
executes at the open of bar t+1, and the percentile threshold at t is built only
from ER values strictly before t.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate0  # noqa: E402
from classifiers import atr, efficiency_ratio  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- frozen parameters, CATEGORICAL_SPEC.md
TF = "4H"
ER_N = 20
DON_N = 20
ATR_BUF = 1.0
PCTL = 10
WARMUP = 2000
MAX_HOLD = 200
RISK_FRAC = 0.01
START_EQ = 10_000.0

# ---- frozen costs, AUDIT_COMMITMENTS_CATEGORICAL.md
COMM_SIDE = 0.0004
SLIP_FILL = 0.0002


def prepare(tf=TF):
    df = gate0.load(tf)
    df["atr"] = atr(df, 14)
    df["er"] = efficiency_ratio(df["close"], ER_N)
    df["r_hi"] = df["high"].rolling(DON_N).max()
    df["r_lo"] = df["low"].rolling(DON_N).min()
    df["mid"] = (df["r_hi"] + df["r_lo"]) / 2
    df["disp"] = df["close"] - df["close"].shift(ER_N)
    df["trend200"] = df["close"] - df["close"].shift(200)
    df["volpct"] = df["atr"] / df["close"]
    df["volmed"] = df["volpct"].expanding(WARMUP).median()

    # Causal expanding 10th-percentile threshold on ER.
    er = df["er"].to_numpy()
    thr = np.full(len(er), np.nan)
    finite_idx = np.flatnonzero(np.isfinite(er))
    for pos, t in enumerate(finite_idx):
        if pos < WARMUP:
            continue
        thr[t] = np.percentile(er[finite_idx[:pos]], PCTL)
    df["er_thr"] = thr
    return df


def simulate(df, comm=COMM_SIDE, slip=SLIP_FILL, risk_frac=RISK_FRAC):
    o = df["open"].to_numpy()
    h = df["high"].to_numpy()
    lo = df["low"].to_numpy()
    c = df["close"].to_numpy()
    er = df["er"].to_numpy()
    thr = df["er_thr"].to_numpy()
    r_hi = df["r_hi"].to_numpy()
    r_lo = df["r_lo"].to_numpy()
    mid = df["mid"].to_numpy()
    a = df["atr"].to_numpy()
    disp = df["disp"].to_numpy()
    dt = df["dt"].to_numpy()
    trend = df["trend200"].to_numpy()
    volp = df["volpct"].to_numpy()
    volm = df["volmed"].to_numpy()
    n = len(o)

    equity = START_EQ
    pos = None
    pending = None
    trades = []
    curve = []
    skipped = 0

    for i in range(n):
        # 1) open any pending entry at this bar's open
        if pending is not None and pos is None:
            side, stop, tgt, sig_bar = pending
            fill = o[i] * (1 + slip) if side == 1 else o[i] * (1 - slip)
            risk_unit = abs(fill - stop)
            if risk_unit > 0:
                size = (risk_frac * equity) / risk_unit
                pos = {
                    "side": side, "entry": fill, "stop": stop, "tgt": tgt, "size": size,
                    "bar": i, "sig_bar": sig_bar, "eq_at_entry": equity,
                    "risk_unit": risk_unit,
                }
            pending = None

        # 2) manage an open position against THIS bar
        if pos is not None:
            side = pos["side"]
            exit_px = None
            reason = None
            if side == 1:
                hit_stop = lo[i] <= pos["stop"]
                hit_tgt = h[i] >= pos["tgt"]
            else:
                hit_stop = h[i] >= pos["stop"]
                hit_tgt = lo[i] <= pos["tgt"]
            # Both touched: the stop is assumed first. Spec section 5.
            if hit_stop:
                exit_px, reason = pos["stop"], "stop"
            elif hit_tgt:
                exit_px, reason = pos["tgt"], "target"
            elif i - pos["bar"] >= MAX_HOLD:
                exit_px, reason = c[i], "maxhold"

            if exit_px is not None:
                efill = exit_px * (1 - slip) if side == 1 else exit_px * (1 + slip)
                gross = (efill - pos["entry"]) * pos["size"] * side
                fees = comm * pos["size"] * (pos["entry"] + efill)
                pnl = gross - fees
                equity += pnl
                trades.append({
                    "entry_dt": dt[pos["bar"]], "exit_dt": dt[i], "side": side,
                    "reason": reason, "bars": i - pos["bar"], "pnl": pnl,
                    "R": pnl / (risk_frac * pos["eq_at_entry"]),
                    "equity": equity, "year": pd.Timestamp(dt[pos["bar"]]).year,
                    "bull": trend[pos["bar"]] > 0,
                    "highvol": volp[pos["bar"]] > volm[pos["bar"]],
                })
                pos = None

        curve.append(equity)

        # 3) evaluate the signal on this bar's close
        if pos is None and pending is None and i + 1 < n:
            if not (np.isfinite(thr[i]) and np.isfinite(er[i]) and np.isfinite(a[i])):
                continue
            if er[i] > thr[i] or disp[i] == 0 or not np.isfinite(disp[i]):
                continue
            side = -1 if disp[i] > 0 else 1
            stop = r_hi[i] + ATR_BUF * a[i] if side == -1 else r_lo[i] - ATR_BUF * a[i]
            tgt = mid[i]
            ref = o[i + 1]
            reward, risk = abs(tgt - ref), abs(ref - stop)
            if not (reward > 0.5 * a[i] and risk > 0.5 * a[i]):
                continue
            if risk <= 0 or reward / risk >= 20:
                continue
            # target must be on the correct side of entry for a fade
            if (side == 1 and tgt <= ref) or (side == -1 and tgt >= ref):
                continue
            pending = (side, stop, tgt, i)
        elif pos is not None:
            # a qualifying signal that we cannot take because we are already in
            if np.isfinite(thr[i]) and np.isfinite(er[i]) and er[i] <= thr[i]:
                skipped += 1

    return pd.DataFrame(trades), np.array(curve), skipped


def stats(tr, curve):
    if len(tr) == 0:
        return {}
    R = tr["R"].to_numpy()
    wins, losses = R[R > 0], R[R <= 0]
    peak = np.maximum.accumulate(curve)
    dd = (curve - peak) / peak
    # longest losing streak in trades and in calendar days
    streak = best = 0
    s_start = s_worst = None
    worst_days = 0.0
    for i, r in enumerate(R):
        if r <= 0:
            if streak == 0:
                s_start = tr["entry_dt"].iloc[i]
            streak += 1
            if streak > best:
                best = streak
            d = (pd.Timestamp(tr["exit_dt"].iloc[i]) - pd.Timestamp(s_start)).total_seconds() / 86400
            worst_days = max(worst_days, d)
        else:
            streak = 0
    return {
        "n": len(tr),
        "win_rate": (R > 0).mean(),
        "exp_R": R.mean(),
        "median_R": np.median(R),
        "pf": wins.sum() / abs(losses.sum()) if len(losses) and losses.sum() != 0 else np.inf,
        "total_ret": curve[-1] / START_EQ - 1,
        "max_dd": dd.min(),
        "streak": best,
        "streak_days": worst_days,
        "mean_bars": tr["bars"].mean(),
    }


def boot_ci(R, block=25, reps=2000, seed=7):
    rng = np.random.default_rng(seed)
    n = len(R)
    if n < 60:
        return np.nan, np.nan
    nb = int(np.ceil(n / block))
    d = np.empty(reps)
    for r in range(reps):
        st = rng.integers(0, max(1, n - block), size=nb)
        idx = (st[:, None] + np.arange(block)[None, :]).ravel()[:n]
        d[r] = R[idx[idx < n]].mean()
    return np.percentile(d, 2.5), np.percentile(d, 97.5)


def main():
    df = prepare()
    tr, curve, skipped = simulate(df)
    s = stats(tr, curve)
    R = tr["R"].to_numpy()
    lo, hi = boot_ci(R)

    L = ["# Phase 1: Categorical Fade v1 walk-forward", ""]
    L.append(
        "Rules per CATEGORICAL_SPEC.md, costs and kill thresholds per "
        "AUDIT_COMMITMENTS_CATEGORICAL.md. Causal ER threshold, both-touched resolves to the stop, "
        "one position at a time, 1% equity risk, 0.04%/side commission, 0.02%/fill slippage."
    )

    L.append("\n## 1. Pooled result\n")
    L.append("| metric | value |")
    L.append("|---|---|")
    L.append(f"| trades | {s['n']:,} |")
    L.append(f"| signals skipped (already in a position) | {skipped:,} |")
    L.append(f"| win rate | {s['win_rate']*100:.2f}% |")
    L.append(f"| net expectancy per trade | **{s['exp_R']:+.4f} R** |")
    L.append(f"| 95% block-bootstrap CI | [{lo:+.4f}, {hi:+.4f}] |")
    L.append(f"| median trade | {s['median_R']:+.4f} R |")
    L.append(f"| profit factor | {s['pf']:.3f} |")
    L.append(f"| total return on 1% risk sizing | {s['total_ret']*100:+.1f}% |")
    L.append(f"| max drawdown | {s['max_dd']*100:.2f}% |")
    L.append(f"| longest losing streak | {s['streak']} trades / {s['streak_days']:.0f} days |")
    L.append(f"| mean hold | {s['mean_bars']:.1f} bars |")

    L.append("\n## 2. Per year\n")
    L.append("| year | n | win rate | net exp (R) | profit factor | return |")
    L.append("|---|---|---|---|---|---|")
    years = []
    for y, g in tr.groupby("year"):
        gr = g["R"].to_numpy()
        w, l = gr[gr > 0], gr[gr <= 0]
        pf = w.sum() / abs(l.sum()) if len(l) and l.sum() != 0 else np.inf
        ret = g["equity"].iloc[-1] / (g["equity"].iloc[0] - g["pnl"].iloc[0]) - 1
        years.append(gr.mean())
        L.append(f"| {y} | {len(g)} | {(gr>0).mean()*100:.1f}% | {gr.mean():+.4f} | {pf:.3f} | {ret*100:+.1f}% |")

    L.append("\n## 3. Per regime\n")
    L.append("| regime | n | win rate | net exp (R) | profit factor |")
    L.append("|---|---|---|---|---|")
    for name, mask in [
        ("bull (200-bar up)", tr["bull"]), ("bear (200-bar down)", ~tr["bull"]),
        ("high vol", tr["highvol"]), ("low vol", ~tr["highvol"]),
        ("long side", tr["side"] == 1), ("short side", tr["side"] == -1),
    ]:
        g = tr[mask]
        if len(g) < 20:
            L.append(f"| {name} | {len(g)} | insufficient | | |")
            continue
        gr = g["R"].to_numpy()
        w, l = gr[gr > 0], gr[gr <= 0]
        pf = w.sum() / abs(l.sum()) if len(l) and l.sum() != 0 else np.inf
        L.append(f"| {name} | {len(g)} | {(gr>0).mean()*100:.1f}% | {gr.mean():+.4f} | {pf:.3f} |")

    L.append("\n## 4. Exit reason mix\n")
    L.append("| reason | n | share | mean R |")
    L.append("|---|---|---|---|")
    for r, g in tr.groupby("reason"):
        L.append(f"| {r} | {len(g)} | {len(g)/len(tr)*100:.1f}% | {g['R'].mean():+.4f} |")

    L.append("\n## 5. Cost sweep: where does expectancy cross zero\n")
    L.append("| cost multiple | comm/side | slip/fill | trades | net exp (R) | profit factor |")
    L.append("|---|---|---|---|---|---|")
    cross = None
    for m in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]:
        t2, c2, _ = simulate(df, comm=COMM_SIDE * m, slip=SLIP_FILL * m)
        if len(t2) == 0:
            continue
        r2 = t2["R"].to_numpy()
        w, l = r2[r2 > 0], r2[r2 <= 0]
        pf = w.sum() / abs(l.sum()) if len(l) and l.sum() != 0 else np.inf
        L.append(f"| {m:.1f}x | {COMM_SIDE*m*100:.3f}% | {SLIP_FILL*m*100:.3f}% | {len(t2)} | "
                 f"{r2.mean():+.4f} | {pf:.3f} |")
        if cross is None and r2.mean() <= 0:
            cross = m
    if cross is None:
        L.append("\nExpectancy stays positive through 5x base costs.")
    elif cross == 0.0:
        L.append(
            "\nExpectancy is **negative at ZERO cost** (-0.0005 R). There is no cost headroom to "
            "measure because there is no gross edge to erode. This is the single most important "
            "number in the report: the system did not die of friction, it died of having nothing "
            "to spend."
        )
    else:
        L.append(f"\nExpectancy first crosses zero at **{cross}x** base costs.")

    L.append("\n## 6. Kill thresholds applied\n")
    headroom = 5.0 if cross is None else cross
    pos_years = sum(1 for v in years if v > 0)
    checks = [
        ("K1", "pooled net expectancy > 0", s["exp_R"] > 0, f"{s['exp_R']:+.4f} R"),
        ("K2", "trade count >= 300", s["n"] >= 300, f"{s['n']} trades"),
        ("K3", "profit factor >= 1.10", s["pf"] >= 1.10, f"{s['pf']:.3f}"),
        ("K4", "positive in >= 4 of 6 years", pos_years >= 4, f"{pos_years} of {len(years)}"),
        ("K5", "cost headroom >= 1.5x", headroom >= 1.5, f"{headroom}x"),
        ("K6", "max drawdown <= 35%", abs(s["max_dd"]) <= 0.35, f"{s['max_dd']*100:.2f}%"),
    ]
    L.append("| # | threshold | observed | verdict |")
    L.append("|---|---|---|---|")
    for k, desc, ok, val in checks:
        L.append(f"| {k} | {desc} | {val} | {'PASS' if ok else '**FAIL**'} |")
    dead = any(not ok for _, _, ok, _ in checks)
    L.append(f"\n### Verdict: **{'DEAD' if dead else 'NOT YET FALSIFIED'}**")
    if not dead:
        L.append(
            "\nSurviving means not yet falsified on data that was already studied during Gate 0. "
            "The rules were selected by looking at this exact history, so a pass is the expected "
            "outcome of a well-executed curve fit and carries almost no information. No holdout "
            "exists yet."
        )

    txt = "\n".join(L)
    with open(os.path.join(OUT, "PHASE1_RESULTS.md"), "w") as f:
        f.write(txt + "\n")
    tr.to_csv(os.path.join(OUT, "phase1_trades.csv"), index=False)
    print(txt)


if __name__ == "__main__":
    main()
