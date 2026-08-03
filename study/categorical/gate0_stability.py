"""Per-year split of the trade-shaped Gate 0 tests.

GATE0_VERDICT.md section 4 flagged this as the most likely thing to kill the
surviving result. The symmetric-barrier version of the effect was sign-flipped
for three consecutive years, but the trade-shaped templates were only ever
measured pooled across 2021-2026. If the higher-timeframe edge lives in 2021 it
is a bull-market artifact and the framework dies here.

Decile edges are computed ONCE on the pooled sample and then held fixed across
years, so "decile 0" means the same volatility-normalised condition every year.
Computing edges per year would silently redefine the condition and make the
comparison meaningless.

Confidence intervals come from a moving-block bootstrap within each year, since
trades overlap in calendar time and the naive count overstates information.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate0  # noqa: E402
from classifiers import atr, efficiency_ratio  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260803)

COST_RT = 0.08 / 100  # repo standing assumption, pending Gate 0 fee verification

# 1h is EXCLUDED. Its parquet has a 520-day hole (2022-12-31 -> 2024-06-04) that
# swallows all of 2023, and rolling windows straddling that discontinuity are
# meaningless. The 1h row in the first GATE0_VERDICT.md cost table was computed
# before this was found and should be disregarded. 15m and 4H have complete
# coverage (15m: one 1-hour gap in 2021; 4H: none).
TIMEFRAMES = ["15m", "4H"]


def build(tf, template, n=20, k=1.0, horizon=200):
    """Return a per-trade frame for one template on one timeframe.

    template "fade": target = range midpoint, stop = beyond the extreme.
    template "breakout": target = extreme plus buffer, stop = range midpoint.
    """
    df = gate0.load(tf)
    a = atr(df, 14)
    close = df["close"]
    r_hi = df["high"].rolling(n).max()
    r_lo = df["low"].rolling(n).min()
    mid = (r_hi + r_lo) / 2

    score = efficiency_ratio(close, n).to_numpy()
    sign = np.sign((close - close.shift(n)).to_numpy())
    entry = df["open"].shift(-1).to_numpy()
    buf = (k * a).to_numpy()
    ext = np.where(sign > 0, r_hi.to_numpy() + buf, r_lo.to_numpy() - buf)

    if template == "fade":
        tgt, stp = mid.to_numpy(), ext
    else:
        tgt, stp = ext, mid.to_numpy()

    # The barrier race takes an upper and a lower level; which one is the target
    # depends on trade direction, so resolve by price rather than by sign.
    up = np.maximum(tgt, stp)
    dn = np.minimum(tgt, stp)

    res = gate0.barrier_race(
        df, np.nan_to_num(up, nan=np.inf), np.nan_to_num(dn, nan=-np.inf), horizon
    )
    tgt_is_up = tgt > stp
    won = np.where(tgt_is_up, res == gate0.UP, res == gate0.DOWN)
    lost = np.where(tgt_is_up, res == gate0.DOWN, res == gate0.UP)

    risk = np.abs(entry - stp)
    reward = np.abs(tgt - entry)
    rr = reward / np.where(risk > 0, risk, np.nan)

    valid = (
        np.isfinite(score) & np.isfinite(rr) & np.isfinite(entry) & (sign != 0)
        & (res != gate0.PENDING) & (res != gate0.BOTH) & (won | lost)
        & (reward > 0.5 * buf) & (risk > 0.5 * buf) & (rr < 20)
    )
    return pd.DataFrame(
        {
            "year": df["dt"].dt.year.to_numpy(),
            "score": score,
            "won": won,
            "rr": rr,
            "risk_pct": risk / entry,
            "valid": valid,
        }
    )[valid]


def expectancy(won, rr, risk_pct):
    gross = (won * rr - (~won) * 1.0).mean()
    cost_r = COST_RT / np.median(risk_pct)
    return gross, cost_r, gross - cost_r


def block_ci(won, rr, block=40, reps=1000):
    """Moving-block bootstrap CI for gross expectancy in R."""
    n = len(won)
    if n < 60:
        return np.nan, np.nan
    block = min(block, max(5, n // 8))
    nb = int(np.ceil(n / block))
    draws = np.empty(reps)
    for r in range(reps):
        st = RNG.integers(0, max(1, n - block), size=nb)
        idx = (st[:, None] + np.arange(block)[None, :]).ravel()[:n]
        idx = idx[idx < n]
        draws[r] = (won[idx] * rr[idx] - (~won[idx]) * 1.0).mean()
    return np.percentile(draws, 2.5), np.percentile(draws, 97.5)


def robustness(n=20, k=1.0, horizon=200):
    """Three checks that could each manufacture the fade edge artificially.

    1. Holding period and concurrent overlap. If trades overlap heavily the
       nominal sample count is fiction.
    2. Both-hit exclusion. A bar that touches target and stop together is dropped;
       if that is common it silently removes losses from a high-win-rate setup.
    3. Fill realism. The target is close to entry and the median hold is short, so
       "high >= target means filled" is the most dangerous assumption in the study.
       Requiring the bar to penetrate the target by pen x ATR is deliberately unfair.
    """
    out = ["\n## Robustness of the fade result\n"]
    out.append("| TF | median hold (bars) | p90 | mean concurrent positions | both-hit % | net R if all both-hits are losses |")
    out.append("|---|---|---|---|---|---|")

    for tf in TIMEFRAMES:
        df = gate0.load(tf)
        a = atr(df, 14)
        close = df["close"]
        r_hi = df["high"].rolling(n).max()
        r_lo = df["low"].rolling(n).min()
        mid = (r_hi + r_lo) / 2
        score = efficiency_ratio(close, n).to_numpy()
        sign = np.sign((close - close.shift(n)).to_numpy())
        entry = df["open"].shift(-1).to_numpy()
        buf = (k * a).to_numpy()
        ext = np.where(sign > 0, r_hi.to_numpy() + buf, r_lo.to_numpy() - buf)
        tgt, stp = mid.to_numpy(), ext
        up, dn = np.maximum(tgt, stp), np.minimum(tgt, stp)

        hi, lo = df["high"].to_numpy(), df["low"].to_numpy()
        N = len(hi)
        t = np.arange(N)
        bars = np.full(N, -1)
        done = np.zeros(N, bool)
        for h in range(horizon):
            f = t + 1 + h
            live = (f < N) & ~done
            idx = np.where(live, f, 0)
            hit = live & ((hi[idx] >= up) | (lo[idx] <= dn))
            bars[hit] = h + 1
            done |= hit

        res = gate0.barrier_race(df, np.nan_to_num(up, nan=np.inf), np.nan_to_num(dn, nan=-np.inf), horizon)
        tu = tgt > stp
        won = np.where(tu, res == gate0.UP, res == gate0.DOWN)
        lost = np.where(tu, res == gate0.DOWN, res == gate0.UP)
        risk, reward = np.abs(entry - stp), np.abs(tgt - entry)
        rr = reward / np.where(risk > 0, risk, np.nan)
        base = (
            np.isfinite(score) & np.isfinite(rr) & (sign != 0)
            & (res != gate0.PENDING) & (reward > 0.5 * buf) & (risk > 0.5 * buf) & (rr < 20)
        )
        e = np.quantile(score[base & (won | lost)], np.linspace(0, 1, 11))
        b = np.clip(np.digitize(score, e[1:-1]), 0, 9)
        dec, amb = base & (b == 0) & (won | lost), base & (b == 0) & (res == gate0.BOTH)
        ntot = dec.sum() + amb.sum()
        cr = COST_RT / np.median((risk / entry)[dec])
        worst = (won[dec] * rr[dec] - (~won[dec]) * 1.0).sum() / ntot - amb.sum() / ntot
        hold = bars[dec]
        out.append(
            f"| {tf} | {np.median(hold):.0f} | {np.percentile(hold, 90):.0f} | "
            f"{hold.mean()*dec.sum()/N:.2f} | {amb.sum()/ntot*100:.2f}% | {worst-cr:+.4f} |"
        )

    out.append("\n### Pessimistic fill: target must be penetrated by pen x ATR to count as filled\n")
    out.append("| TF | pen 0.00 | pen 0.05 | pen 0.10 | pen 0.25 |")
    out.append("|---|---|---|---|---|")
    for tf in TIMEFRAMES:
        df = gate0.load(tf)
        a = atr(df, 14)
        close = df["close"]
        r_hi = df["high"].rolling(n).max()
        r_lo = df["low"].rolling(n).min()
        mid = (r_hi + r_lo) / 2
        score = efficiency_ratio(close, n).to_numpy()
        sign = np.sign((close - close.shift(n)).to_numpy())
        entry = df["open"].shift(-1).to_numpy()
        buf = (k * a).to_numpy()
        ext = np.where(sign > 0, r_hi.to_numpy() + buf, r_lo.to_numpy() - buf)
        risk = np.abs(entry - ext)
        cells = []
        for pen in (0.0, 0.05, 0.10, 0.25):
            tgt = np.where(sign > 0, mid.to_numpy() - pen * buf, mid.to_numpy() + pen * buf)
            up, dn = np.maximum(tgt, ext), np.minimum(tgt, ext)
            res = gate0.barrier_race(df, np.nan_to_num(up, nan=np.inf), np.nan_to_num(dn, nan=-np.inf), horizon)
            tu = tgt > ext
            won = np.where(tu, res == gate0.UP, res == gate0.DOWN)
            lost = np.where(tu, res == gate0.DOWN, res == gate0.UP)
            rw = np.abs(tgt - entry)
            rr = rw / np.where(risk > 0, risk, np.nan)
            ok = (
                np.isfinite(score) & np.isfinite(rr) & (sign != 0) & (res != gate0.PENDING)
                & (res != gate0.BOTH) & (won | lost) & (rw > 0.5 * buf) & (risk > 0.5 * buf) & (rr < 20)
            )
            e = np.quantile(score[ok], np.linspace(0, 1, 11))
            b = np.clip(np.digitize(score, e[1:-1]), 0, 9)
            m = ok & (b == 0)
            g = (won[m] * rr[m] - (~won[m]) * 1.0).mean()
            cells.append(f"{g - COST_RT/np.median((risk/entry)[m]):+.4f}")
        out.append(f"| {tf} | " + " | ".join(cells) + " |")
    return out


def main():
    lines = ["# Gate 0 stability: per-year split of the trade-shaped tests", ""]
    lines.append(
        "Decile edges fixed on the pooled sample, then held constant across years. "
        f"Costs at {COST_RT*100:.2f}% round trip, no slippage. "
        "CIs are moving-block bootstrap on gross expectancy."
    )

    for template, title in [("fade", "CONSOLIDATION template (fade to range midpoint)"),
                            ("breakout", "DIRECTION template (break to new extreme)")]:
        lines.append(f"\n## {title}\n")
        for tf in TIMEFRAMES:
            d = build(tf, template)
            edges = np.quantile(d["score"], np.linspace(0, 1, 11))
            dec = np.clip(np.digitize(d["score"], edges[1:-1]), 0, 9)
            target_dec = 0 if template == "fade" else 9
            sel = d[dec == target_dec]

            lines.append(f"\n### {tf}, ER decile {target_dec}\n")
            lines.append("| year | n | win rate | gross R | 95% CI | cost/R | net R |")
            lines.append("|---|---|---|---|---|---|---|")
            for y, g in sel.groupby("year"):
                if len(g) < 30:
                    lines.append(f"| {y} | {len(g)} | insufficient | | | | |")
                    continue
                won = g["won"].to_numpy()
                rr = g["rr"].to_numpy()
                gross, cr, net = expectancy(won, rr, g["risk_pct"].to_numpy())
                lo, hi = block_ci(won, rr)
                lines.append(
                    f"| {y} | {len(g):,} | {won.mean()*100:.1f}% | {gross:+.4f} | "
                    f"[{lo:+.4f}, {hi:+.4f}] | {cr:.4f} | **{net:+.4f}** |"
                )
            won = sel["won"].to_numpy()
            rr = sel["rr"].to_numpy()
            gross, cr, net = expectancy(won, rr, sel["risk_pct"].to_numpy())
            lo, hi = block_ci(won, rr)
            lines.append(
                f"| **pooled** | {len(sel):,} | {won.mean()*100:.1f}% | {gross:+.4f} | "
                f"[{lo:+.4f}, {hi:+.4f}] | {cr:.4f} | **{net:+.4f}** |"
            )

            yrs = [
                expectancy(g["won"].to_numpy(), g["rr"].to_numpy(), g["risk_pct"].to_numpy())[2]
                for y, g in sel.groupby("year") if len(g) >= 30
            ]
            if yrs:
                pos = sum(1 for v in yrs if v > 0)
                lines.append(
                    f"\nNet positive in **{pos} of {len(yrs)}** years. "
                    f"Worst year {min(yrs):+.4f} R, best {max(yrs):+.4f} R."
                )

    lines += robustness()

    txt = "\n".join(lines)
    with open(os.path.join(OUT, "GATE0_STABILITY.md"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
