"""Research cycle 1: sandbox tests for candidates C1-C5, exactly per
RESEARCH_PROTOCOL.md. Sandbox span only (2021-01-07..2023-12-31; C2 from
2021-12-01). Validation span is not touched by this script.

Simulator: entry at next 15m open after the closed-bar signal; stop checked
every bar (gap-through exits at that bar's open); time exit at the close of
bar entry+limit-1; same cost stack as AUDIT_COMMITMENTS.md. net_R is gross
minus costs, in units of the stop distance.
"""
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

COMMISSION_RT = 0.0008
SLIP_PER_FILL = 0.0001
SWAP_PER_4H = 0.000055
MIN_STOP_PCT = 0.010
SANDBOX_START = pd.Timestamp("2021-01-07", tz="UTC")
SANDBOX_END = pd.Timestamp("2024-01-01", tz="UTC")     # exclusive


def load_bars():
    df = pd.read_parquet(os.path.join(ROOT, "audit", "studied_15m.parquet"))
    return df[["time", "dt", "open", "high", "low", "close"]].reset_index(drop=True)


def simulate(sigs, df):
    """sigs: list of (sig_bar, direction, stop_price, limit_bars, tag)."""
    t = df["time"].to_numpy()
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    n = len(df)
    trades, skipped = [], 0
    for sig, direction, stop, limit, tag in sigs:
        e = sig + 1
        if e >= n:
            continue
        entry = o[e]
        stop_d = (entry - stop) if direction == "long" else (stop - entry)
        if not np.isfinite(stop_d) or stop_d <= 0 or stop_d / entry < MIN_STOP_PCT:
            skipped += 1
            continue
        last = min(e + limit - 1, n - 1)
        gross = None
        for b in range(e, last + 1):
            gap = (o[b] <= stop) if direction == "long" else (o[b] >= stop)
            hit = (l[b] <= stop) if direction == "long" else (h[b] >= stop)
            if b == e:
                gap = False
            if gap:
                px = o[b]
                gross = ((px - entry) if direction == "long" else (entry - px)) / stop_d
                x = b
                break
            if hit:
                gross, x = -1.0, b
                break
        if gross is None:
            px = c[last]
            gross = ((px - entry) if direction == "long" else (entry - px)) / stop_d
            x = last
        n_swaps = int(t[x] // 14400) - int(t[e] // 14400)
        cost_r = (COMMISSION_RT + 2 * SLIP_PER_FILL + n_swaps * SWAP_PER_4H) * entry / stop_d
        trades.append(dict(sig=sig, e_bar=e, x_bar=x, dir=direction, tag=tag,
                           entry=entry, stop_d=stop_d, gross_r=gross,
                           net_r=gross - cost_r, t_entry=t[e], t_exit=t[x]))
    return trades, skipped


def in_sandbox(df, sig_bar, start=SANDBOX_START):
    dt_ = df["dt"].iloc[sig_bar + 1] if sig_bar + 1 < len(df) else df["dt"].iloc[-1]
    return start <= dt_ < SANDBOX_END


# ── candidates ───────────────────────────────────────────────────────────────

def c1_funding(df):
    f = pd.read_parquet(os.path.join(HERE, "funding.parquet"))
    ft = f["funding_time_ms"].to_numpy() // 1000
    fr = f["funding_rate"].to_numpy(float)
    bar_open = df["time"].to_numpy()
    idx_of_open = {v: i for i, v in enumerate(bar_open)}
    sigs, last = [], {"long": -10**9, "short": -10**9}
    for i in range(len(f)):
        T = int(round(ft[i] / 900) * 900)          # settle times are on 8h marks
        win = fr[(ft >= ft[i] - 90 * 86400) & (ft < ft[i])]
        if len(win) < 200:
            continue
        pct = np.mean(win < fr[i])
        direction = "short" if pct >= 0.98 else ("long" if pct <= 0.02 else None)
        if direction is None:
            continue
        e = idx_of_open.get(T)
        if e is None or e - 1 < 0:
            continue
        if e - last[direction] < 96:
            continue
        entry_ref = df["open"].iloc[e]
        stop = entry_ref * (0.97 if direction == "long" else 1.03)
        sigs.append((e - 1, direction, stop, 96, f"fund={fr[i]:+.5f}"))
        last[direction] = e
    return sigs


def c2_oi_flush(df):
    oi = pd.read_parquet(os.path.join(HERE, "oi5.parquet"))
    bars = df.copy()
    bars["close_ms"] = (bars["time"] + 900) * 1000
    m = pd.merge_asof(bars, oi.rename(columns={"ts_ms": "close_ms"}),
                      on="close_ms", direction="backward",
                      tolerance=30 * 60 * 1000)
    v = m["sum_open_interest"].to_numpy(float)
    c = df["close"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    sigs, last = [], {"long": -10**9, "short": -10**9}
    for tt in range(8, len(df)):
        if np.isnan(v[tt]) or np.isnan(v[tt - 8]) or v[tt - 8] == 0:
            continue
        oi_ret = v[tt] / v[tt - 8] - 1
        pr = c[tt] / c[tt - 8] - 1
        if oi_ret <= -0.05 and abs(pr) >= 0.02:
            direction = "long" if pr < 0 else "short"
            if tt + 1 - last[direction] < 96:
                continue
            stop = l[tt - 7:tt + 1].min() if direction == "long" else h[tt - 7:tt + 1].max()
            sigs.append((tt, direction, stop, 96, f"oi={oi_ret:+.3f},pr={pr:+.3f}"))
            last[direction] = tt + 1
    return sigs


def c3_premium(df):
    p = pd.read_parquet(os.path.join(HERE, "premium15.parquet"))
    p["time"] = p["open_time_ms"] // 1000
    m = df.merge(p[["time", "premium_close"]], on="time", how="left")
    s = m["premium_close"]
    rank = s.rolling(2880, min_periods=2880).rank()   # rank of current within window
    pct = (rank - 1) / (2880 - 1)
    o = df["open"].to_numpy(float)
    sigs, last = [], {"long": -10**9, "short": -10**9}
    for tt in range(len(df) - 1):
        if np.isnan(pct.iloc[tt]):
            continue
        direction = "short" if pct.iloc[tt] >= 0.995 else ("long" if pct.iloc[tt] <= 0.005 else None)
        if direction is None or tt + 1 - last[direction] < 96:
            continue
        stop = o[tt + 1] * (0.97 if direction == "long" else 1.03)
        sigs.append((tt, direction, stop, 96, f"prem={s.iloc[tt]:+.5f}"))
        last[direction] = tt + 1
    return sigs


def c4_weekend(df):
    t = df["time"].to_numpy()
    c = df["close"].to_numpy(float)
    o = df["open"].to_numpy(float)
    idx = {v: i for i, v in enumerate(t)}
    sigs = []
    is_sun_1945 = (t % 86400 == 71100) & (((t // 86400 + 4) % 7) == 6)
    for tt in np.where(is_sun_1945)[0]:
        fri = idx.get(t[tt] - 2 * 86400)
        if fri is None or tt + 1 >= len(df):
            continue
        r = c[tt] / c[fri] - 1
        if abs(r) < 0.015:
            continue
        direction = "short" if r > 0 else "long"
        stop = o[tt + 1] * (0.97 if direction == "long" else 1.03)
        sigs.append((tt, direction, stop, 96, f"wk={r:+.3f}"))
    return sigs


def c5_compression(df):
    d = df.set_index("dt").resample("1D").agg(
        high=("high", "max"), low=("low", "min"), close=("close", "last")).dropna()
    hi10 = d["high"].rolling(10).max()
    lo10 = d["low"].rolling(10).min()
    rng = (hi10 - lo10) / d["close"]
    pct = (rng.rolling(365, min_periods=365).rank() - 1) / 364
    compressed = pct <= 0.10
    day_of_bar = df["dt"].dt.floor("D")
    c = df["close"].to_numpy(float)
    sigs = []
    episode_active = False
    armed_until = None
    hi = lo = None
    traded = False
    days = list(d.index)
    day_first_bar = {day: int(day_of_bar.searchsorted(day, side="left")) for day in days}
    for k, day in enumerate(days):
        if compressed.iloc[k]:
            if not episode_active:
                episode_active, traded = True, False
            hi, lo = hi10.iloc[k], lo10.iloc[k]
            armed_until = day + pd.Timedelta(days=6)   # trigger window: next 5 days
        elif episode_active and day > (armed_until or day):
            episode_active = False
        if not episode_active or traded or hi is None:
            continue
        # scan 15m closes of the day AFTER the compressed day(s)
        if k + 1 < len(days):
            nxt = days[k + 1]
            b0 = day_first_bar.get(nxt)
            if b0 is None:
                continue
            b1 = int(day_of_bar.searchsorted(min(armed_until, days[-1]), side="right"))
            for tt in range(b0, min(b1, len(df) - 1)):
                if c[tt] > hi:
                    sigs.append((tt, "long", lo, 480, f"cmp_hi={hi:.0f}"))
                    traded = True
                    break
                if c[tt] < lo:
                    sigs.append((tt, "short", hi, 480, f"cmp_lo={lo:.0f}"))
                    traded = True
                    break
    return sigs


# ── reporting ────────────────────────────────────────────────────────────────

def half_label(ts):
    dt_ = pd.to_datetime(ts, unit="s", utc=True)
    return f"{dt_.year}H{1 if dt_.month <= 6 else 2}"


def report(name, trades, skipped, lines):
    rs = np.array([x["net_r"] for x in trades])
    lines.append(f"## {name}")
    if not len(rs):
        lines.append("no trades in sandbox. DEAD (degenerate count).\n")
        return False
    by_w = defaultdict(list)
    for x in trades:
        by_w[half_label(x["t_entry"])].append(x["net_r"])
    neg = sum(np.mean(v) < 0 for v in by_w.values())
    gp = rs[rs > 0].sum()
    gl = -rs[rs < 0].sum()
    pf = gp / gl if gl else float("inf")
    se = rs.std() / max(np.sqrt(len(rs)), 1)
    lines.append(f"trades={len(rs)} skipped={skipped} expectancy={rs.mean():+.4f}R "
                 f"(SE {se:.4f}) win={np.mean(rs > 0):.1%} PF={pf:.3f}")
    for w in sorted(by_w):
        v = np.array(by_w[w])
        lines.append(f"  {w}: n={len(v):3d} exp={v.mean():+.4f}R")
    k1 = rs.mean() >= 0.15
    k2 = neg <= len(by_w) / 2
    verdict = "SURVIVES SANDBOX" if (k1 and k2) else "DEAD"
    lines.append(f"pass bar: expectancy>=+0.15R: {'yes' if k1 else 'NO'}; "
                 f"windows nonneg majority: {'yes' if k2 else 'NO'} "
                 f"({len(by_w)-neg}/{len(by_w)})")
    lines.append(f"VERDICT: {verdict}\n")
    return k1 and k2


def main():
    df = load_bars()
    lines = ["# CYCLE 1 SANDBOX REPORT", "",
             "Per RESEARCH_PROTOCOL.md. Sandbox span only. One run per candidate.", ""]
    gens = [("C1 funding extreme fade", c1_funding, SANDBOX_START),
            ("C2 OI flush reversion", c2_oi_flush, pd.Timestamp("2021-12-01", tz="UTC")),
            ("C3 premium extreme fade", c3_premium, SANDBOX_START),
            ("C4 weekend move fade", c4_weekend, SANDBOX_START),
            ("C5 compression breakout", c5_compression, SANDBOX_START)]
    for name, gen, start in gens:
        sigs = [s for s in gen(df) if in_sandbox(df, s[0], start)]
        trades, skipped = simulate(sigs, df)
        report(name, trades, skipped, lines)
        pd.DataFrame(trades).to_csv(
            os.path.join(HERE, f"sandbox_{name.split()[0]}.csv"), index=False)
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "SANDBOX_REPORT.md"), "w") as fh:
        fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
