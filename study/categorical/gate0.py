"""Gate 0 for categorical trading: does the regime label predict forward behaviour?

No trading rules. No costs. No entries or exits. This asks one question only:

    Conditional on where a bar sits on the consolidation <-> direction spectrum,
    is price measurably more likely to continue its recent displacement (direction)
    or to retrace it (consolidation)?

If the answer is no, the framework in VIDEO_EXTRACT.md has no predictive content
and no entry trigger can rescue it. That is the kill condition.

Pass condition, pre-committed before any result was computed (SYSTEMIZATION.md s4):
  monotone separation of continuation probability across the classifier spectrum,
  not merely one good bucket. Monotonicity is what a mechanism looks like; a single
  lucky bucket is what noise looks like.

Causality
---------
The classifier at bar t uses closes up to and including t. The forward measurement
starts at the OPEN of bar t+1 and barriers are sized from ATR at bar t. Nothing in
the outcome path feeds back into the label.

Inference
---------
Samples overlap heavily (rolling windows, overlapping forward paths), so the naive
sample count massively overstates the information content. All confidence intervals
come from a moving-block bootstrap with blocks longer than the dependence horizon.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifiers import CLASSIFIERS, atr, efficiency_ratio  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUT = os.path.dirname(os.path.abspath(__file__))

RNG = np.random.default_rng(20260803)

# Outcome codes for the barrier race.
PENDING, UP, DOWN, BOTH = 0, 1, 2, 3


def load(tf):
    df = pd.read_parquet(os.path.join(DATA, f"{tf}.parquet"))
    return df.reset_index(drop=True)


# ---------------------------------------------------------------- barrier race
def barrier_race(df, up_b, dn_b, horizon):
    """First-passage of symmetric barriers, entered at bar t+1 open.

    up_b / dn_b are arrays indexed by SIGNAL bar t. Scanning starts at bar t+1
    and runs for `horizon` bars. Returns an int8 array of outcome codes.

    A bar whose high clears the upper barrier and whose low clears the lower
    barrier in the same bar is recorded as BOTH rather than silently resolved.
    Intrabar path is unknowable from OHLC, so those samples are bounded rather
    than assumed.
    """
    hi = df["high"].to_numpy(np.float64)
    lo = df["low"].to_numpy(np.float64)
    n = len(hi)
    t = np.arange(n)
    res = np.full(n, PENDING, dtype=np.int8)
    done = np.zeros(n, dtype=bool)

    for h in range(horizon):
        fwd = t + 1 + h
        live = (fwd < n) & ~done
        if not live.any():
            break
        idx = np.where(live, fwd, 0)
        u = live & (hi[idx] >= up_b)
        d = live & (lo[idx] <= dn_b)
        both = u & d
        res[both] = BOTH
        res[u & ~both] = UP
        res[d & ~both] = DOWN
        done |= (u | d)
    return res


def build_samples(df, n_win, k_atr, horizon, classifier="ER"):
    """One row per signal bar: classifier value, recent-move sign, race outcome.

    `continuation` is True when the barrier in the direction of the last n-bar
    displacement is struck first. That is the exact quantity the video claims the
    category predicts: direction means "go to a new area", consolidation means
    "stay where it has already been".
    """
    close = df["close"]
    a = atr(df, 14)

    score = CLASSIFIERS[classifier](df, n_win)
    disp = close - close.shift(n_win)
    sign = np.sign(disp.to_numpy())

    entry = df["open"].shift(-1).to_numpy()
    band = (k_atr * a).to_numpy()
    up_b = entry + band
    dn_b = entry - band

    res = barrier_race(df, np.nan_to_num(up_b, nan=np.inf), np.nan_to_num(dn_b, nan=-np.inf), horizon)

    valid = (
        np.isfinite(score.to_numpy())
        & np.isfinite(entry)
        & np.isfinite(band)
        & (band > 0)
        & (sign != 0)
        & (res != PENDING)
    )

    hit_up = res == UP
    hit_dn = res == DOWN
    cont = np.where(sign > 0, hit_up, hit_dn)
    rev = np.where(sign > 0, hit_dn, hit_up)
    ambiguous = res == BOTH

    return pd.DataFrame(
        {
            "score": score.to_numpy(),
            "sign": sign,
            "cont": cont,
            "rev": rev,
            "ambig": ambiguous,
            "valid": valid,
        }
    )


# ------------------------------------------------------------------- inference
def block_bootstrap_stats(bucket, cont, decided, n_buckets, block, reps=500):
    """Moving-block bootstrap over the sample sequence.

    Blocks preserve the local dependence created by overlapping windows and
    overlapping forward paths. Returns per-bucket continuation-rate draws and
    Spearman-rho draws across buckets.
    """
    n = len(bucket)
    n_blocks = int(np.ceil(n / block))
    rates = np.full((reps, n_buckets), np.nan)
    rhos = np.full(reps, np.nan)
    ranks = np.arange(n_buckets, dtype=float)

    for r in range(reps):
        starts = RNG.integers(0, max(1, n - block), size=n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        idx = idx[idx < n]
        b, c, d = bucket[idx], cont[idx], decided[idx]
        for j in range(n_buckets):
            m = (b == j) & d
            tot = m.sum()
            if tot >= 30:
                rates[r, j] = c[m].sum() / tot
        ok = np.isfinite(rates[r])
        if ok.sum() >= 4:
            rhos[r] = stats.spearmanr(ranks[ok], rates[r][ok]).statistic
    return rates, rhos


def analyse(samples, n_buckets=10, block=500, reps=500, label=""):
    s = samples[samples["valid"]].reset_index(drop=True)
    if len(s) < 5000:
        return None

    # Full-sample quantile bucketing. This is a descriptive conditional study,
    # not a predictive rule; a live implementation must use causal thresholds.
    # The causal-threshold robustness run is in run_causal_bucket_check().
    edges = np.unique(np.quantile(s["score"], np.linspace(0, 1, n_buckets + 1)))
    bucket = np.clip(np.digitize(s["score"], edges[1:-1]), 0, len(edges) - 2)
    nb = len(edges) - 1

    cont = s["cont"].to_numpy()
    decided = (~s["ambig"]).to_numpy() & (s["cont"].to_numpy() | s["rev"].to_numpy())

    rows = []
    for j in range(nb):
        m = bucket == j
        md = m & decided
        tot = int(md.sum())
        if tot == 0:
            continue
        rows.append(
            {
                "bucket": j,
                "score_lo": edges[j],
                "score_hi": edges[j + 1],
                "n": tot,
                "n_ambig": int((m & s["ambig"].to_numpy()).sum()),
                "cont_rate": cont[md].sum() / tot,
            }
        )
    table = pd.DataFrame(rows)

    rates, rhos = block_bootstrap_stats(bucket, cont, decided, nb, block, reps)
    table["ci_lo"] = [np.nanpercentile(rates[:, j], 2.5) for j in table["bucket"]]
    table["ci_hi"] = [np.nanpercentile(rates[:, j], 97.5) for j in table["bucket"]]

    ok = np.isfinite(table["cont_rate"])
    rho = stats.spearmanr(table["bucket"][ok], table["cont_rate"][ok]).statistic
    rho_lo, rho_hi = np.nanpercentile(rhos, [2.5, 97.5])

    # Ambiguity bound: re-run the extremes assuming every both-hit resolved the
    # way that would most damage the conclusion.
    amb = s["ambig"].to_numpy()
    worst = []
    for j in (0, nb - 1):
        m = bucket == j
        tot = int((m & decided).sum()) + int((m & amb).sum())
        base = cont[m & decided].sum()
        if tot == 0:
            worst.append((np.nan, np.nan))
            continue
        # low bucket should be LOW: push it up. high bucket should be HIGH: push it down.
        if j == 0:
            worst.append((base / tot, (base + (m & amb).sum()) / tot))
        else:
            worst.append(((base) / tot, base / tot))
    return {
        "label": label,
        "table": table,
        "rho": rho,
        "rho_ci": (rho_lo, rho_hi),
        "n_total": int(decided.sum()),
        "ambig_rate": float(amb.mean()),
        "spread": float(table["cont_rate"].iloc[-1] - table["cont_rate"].iloc[0]),
        "worst_case_low_bucket": worst[0][1],
    }


def fmt(res):
    t = res["table"]
    lines = [f"\n### {res['label']}"]
    lines.append(
        f"decided samples {res['n_total']:,}   ambiguous(both-hit) {res['ambig_rate']*100:.2f}%"
    )
    lines.append("")
    lines.append("| bucket | score range | n | continuation % | 95% block-bootstrap CI |")
    lines.append("|---|---|---|---|---|")
    for _, r in t.iterrows():
        lines.append(
            f"| {int(r['bucket'])} | {r['score_lo']:.3f} to {r['score_hi']:.3f} | {int(r['n']):,} | "
            f"{r['cont_rate']*100:.2f} | {r['ci_lo']*100:.2f} to {r['ci_hi']*100:.2f} |"
        )
    lines.append("")
    lines.append(
        f"Spearman rho(bucket, continuation) = **{res['rho']:.3f}**  "
        f"95% CI [{res['rho_ci'][0]:.3f}, {res['rho_ci'][1]:.3f}]   "
        f"spread bottom to top = **{res['spread']*100:+.2f} pts**"
    )
    return "\n".join(lines)


# ------------------------------------------------------------------- robustness
def run_causal_bucket_check(df, n_win, k_atr, horizon, warmup=20000):
    """Repeat the headline test with EXPANDING-window quantile thresholds.

    Decile edges at bar t are computed only from classifier history up to t, so
    nothing about bucket membership uses the future. Slower and noisier, but it
    is the version a live system could actually run.
    """
    s = build_samples(df, n_win, k_atr, horizon, "ER")
    s = s[s["valid"]].reset_index(drop=True)
    score = s["score"].to_numpy()
    n = len(score)
    if n < warmup + 5000:
        return None

    bucket = np.full(n, -1, dtype=int)
    step = 2000
    for start in range(warmup, n, step):
        end = min(start + step, n)
        edges = np.quantile(score[:start], np.linspace(0, 1, 11))[1:-1]
        bucket[start:end] = np.clip(np.digitize(score[start:end], edges), 0, 9)

    keep = bucket >= 0
    cont = s["cont"].to_numpy()[keep]
    decided = ((~s["ambig"].to_numpy()) & (s["cont"].to_numpy() | s["rev"].to_numpy()))[keep]
    b = bucket[keep]

    rows = []
    for j in range(10):
        m = (b == j) & decided
        if m.sum() < 100:
            continue
        rows.append({"bucket": j, "n": int(m.sum()), "cont_rate": cont[m].sum() / m.sum()})
    tab = pd.DataFrame(rows)
    rho = stats.spearmanr(tab["bucket"], tab["cont_rate"]).statistic
    return tab, rho


def build_range_samples(df, n_win, k_atr, horizon):
    """Trade-shaped test 1: the CONSOLIDATION template.

    The headline test conditions only on the sign of recent displacement. The
    video's consolidation trade conditions on POSITION IN THE RANGE: price at the
    top of the range is shorted with a target inside and a stop outside. That is a
    sharper condition, so the framework deserves to be tested on it directly.

    Here `revert` means the barrier pointing back toward the range midpoint was
    struck first. The claim under test is that revert-rate rises as ER falls, and
    rises further the closer price sits to a range extreme.
    """
    close, a = df["close"], atr(df, 14)
    r_hi = df["high"].rolling(n_win).max()
    r_lo = df["low"].rolling(n_win).min()
    width = (r_hi - r_lo).replace(0, np.nan)
    pos = ((close - r_lo) / width).to_numpy()

    score = efficiency_ratio(close, n_win).to_numpy()
    entry = df["open"].shift(-1).to_numpy()
    band = (k_atr * a).to_numpy()
    res = barrier_race(
        df,
        np.nan_to_num(entry + band, nan=np.inf),
        np.nan_to_num(entry - band, nan=-np.inf),
        horizon,
    )

    upper = pos > 0.5
    revert = np.where(upper, res == DOWN, res == UP)
    extend = np.where(upper, res == UP, res == DOWN)
    valid = (
        np.isfinite(score) & np.isfinite(pos) & np.isfinite(entry)
        & np.isfinite(band) & (band > 0) & (res != PENDING)
    )
    return pd.DataFrame(
        {"score": score, "pos": pos, "cont": revert, "rev": extend,
         "ambig": res == BOTH, "valid": valid}
    )


def build_breakout_samples(df, n_win, k_atr, horizon):
    """Trade-shaped test 2: the DIRECTION template.

    "Target new areas, stop inside the range." Barrier out is the n-bar Donchian
    extreme in the displacement direction plus a buffer; barrier in is the range
    midpoint. This is deliberately asymmetric because the trade is asymmetric, so
    the raw hit rate is not comparable to 50%. Expectancy in R is reported instead.
    """
    close, a = df["close"], atr(df, 14)
    r_hi = df["high"].rolling(n_win).max()
    r_lo = df["low"].rolling(n_win).min()
    mid = (r_hi + r_lo) / 2
    score = efficiency_ratio(close, n_win).to_numpy()
    sign = np.sign((close - close.shift(n_win)).to_numpy())
    entry = df["open"].shift(-1).to_numpy()
    buf = (k_atr * a).to_numpy()

    tgt = np.where(sign > 0, r_hi.to_numpy() + buf, r_lo.to_numpy() - buf)
    stp = mid.to_numpy()
    up_b = np.where(sign > 0, tgt, stp)
    dn_b = np.where(sign > 0, stp, tgt)

    res = barrier_race(df, np.nan_to_num(up_b, nan=np.inf), np.nan_to_num(dn_b, nan=-np.inf), horizon)
    won = np.where(sign > 0, res == UP, res == DOWN)
    lost = np.where(sign > 0, res == DOWN, res == UP)

    reward = np.abs(tgt - entry)
    risk = np.abs(entry - stp)
    rr = reward / np.where(risk > 0, risk, np.nan)
    valid = (
        np.isfinite(score) & np.isfinite(entry) & np.isfinite(rr) & (sign != 0)
        & (risk > 0) & (reward > 0) & (res != PENDING) & (rr < 20)
    )
    return pd.DataFrame(
        {"score": score, "won": won, "lost": lost, "rr": rr,
         "ambig": res == BOTH, "valid": valid}
    )


def analyse_breakout(samples, n_buckets=10):
    """Expectancy in R per ER decile for the asymmetric direction template."""
    s = samples[samples["valid"]].reset_index(drop=True)
    edges = np.unique(np.quantile(s["score"], np.linspace(0, 1, n_buckets + 1)))
    b = np.clip(np.digitize(s["score"], edges[1:-1]), 0, len(edges) - 2)
    rows = []
    for j in range(len(edges) - 1):
        m = (b == j) & (s["won"].to_numpy() | s["lost"].to_numpy()) & ~s["ambig"].to_numpy()
        if m.sum() < 100:
            continue
        won = s["won"].to_numpy()[m]
        rr = s["rr"].to_numpy()[m]
        rows.append({
            "bucket": j, "score_lo": edges[j], "score_hi": edges[j + 1], "n": int(m.sum()),
            "win_rate": won.mean(), "mean_rr": rr.mean(),
            "exp_R": (won * rr - (~won) * 1.0).mean(),
        })
    return pd.DataFrame(rows)


def main():
    report = ["# Gate 0 results: does the categorical label predict forward behaviour?", ""]
    report.append(
        "Generated by `study/categorical/gate0.py`. No trading rules, no costs, no entries. "
        "Every number below is a conditional forward-behaviour statistic on BTCUSDT.P."
    )

    HEAD_TF, HEAD_N, HEAD_K, HEAD_H = "5m", 20, 1.0, 40

    # ---- headline
    df = load(HEAD_TF)
    s = build_samples(df, HEAD_N, HEAD_K, HEAD_H, "ER")
    head = analyse(s, block=10 * (HEAD_N + HEAD_H), label=f"HEADLINE  {HEAD_TF} ER({HEAD_N}) barriers +/-{HEAD_K}xATR14 horizon {HEAD_H} bars")
    report.append("\n## 1. Headline test\n")
    report.append(
        "Signal bar t: compute ER and the sign of the n-bar close displacement. Enter at the open "
        "of t+1. Place symmetric barriers at +/- k x ATR14(t). Race them for H bars. "
        "`continuation` means the barrier in the direction of the recent displacement was struck first."
    )
    report.append(fmt(head))

    # ---- classifier horse race
    report.append("\n## 2. Classifier horse race (same bars, same barriers)\n")
    race = {}
    for name in ["ER", "RangeEff", "VR", "ADX", "Hurst"]:
        ss = build_samples(df, HEAD_N, HEAD_K, HEAD_H, name)
        r = analyse(ss, block=10 * (HEAD_N + HEAD_H), reps=300, label=f"{name}({HEAD_N})")
        if r:
            race[name] = r
    report.append("| classifier | rho | 95% CI | bottom decile | top decile | spread |")
    report.append("|---|---|---|---|---|---|")
    for name, r in race.items():
        t = r["table"]
        report.append(
            f"| {name} | {r['rho']:.3f} | [{r['rho_ci'][0]:.3f}, {r['rho_ci'][1]:.3f}] | "
            f"{t['cont_rate'].iloc[0]*100:.2f}% | {t['cont_rate'].iloc[-1]*100:.2f}% | "
            f"{r['spread']*100:+.2f} pts |"
        )

    # ---- parameter robustness
    report.append("\n## 3. Parameter robustness (ER, 5m)\n")
    report.append("| n_win | k x ATR | horizon | n decided | rho | bottom | top | spread |")
    report.append("|---|---|---|---|---|---|---|---|")
    grid = []
    for n_win in (10, 20, 40, 80):
        for k in (0.5, 1.0, 2.0):
            for H in (20, 40, 80):
                ss = build_samples(df, n_win, k, H, "ER")
                r = analyse(ss, block=10 * (n_win + H), reps=200, label=f"n{n_win} k{k} H{H}")
                if not r:
                    continue
                t = r["table"]
                grid.append((n_win, k, H, r["rho"], r["spread"]))
                report.append(
                    f"| {n_win} | {k} | {H} | {r['n_total']:,} | {r['rho']:.3f} | "
                    f"{t['cont_rate'].iloc[0]*100:.2f}% | {t['cont_rate'].iloc[-1]*100:.2f}% | "
                    f"{r['spread']*100:+.2f} pts |"
                )

    # ---- timeframe robustness
    report.append("\n## 4. Timeframe robustness (ER(20), +/-1.0xATR, 40 bars)\n")
    report.append("| timeframe | n decided | rho | bottom | top | spread |")
    report.append("|---|---|---|---|---|---|")
    for tf in ("5m", "15m", "1h", "4H"):
        d = load(tf)
        ss = build_samples(d, HEAD_N, HEAD_K, HEAD_H, "ER")
        r = analyse(ss, block=10 * (HEAD_N + HEAD_H), reps=200, label=tf)
        if not r:
            report.append(f"| {tf} | insufficient | | | | |")
            continue
        t = r["table"]
        report.append(
            f"| {tf} | {r['n_total']:,} | {r['rho']:.3f} | {t['cont_rate'].iloc[0]*100:.2f}% | "
            f"{t['cont_rate'].iloc[-1]*100:.2f}% | {r['spread']*100:+.2f} pts |"
        )

    # ---- causal bucketing
    report.append("\n## 5. Causal-threshold robustness\n")
    report.append(
        "Section 1 buckets by full-sample quantiles, which is descriptive rather than tradeable. "
        "Here decile edges at bar t use only ER history up to t."
    )
    cb = run_causal_bucket_check(df, HEAD_N, HEAD_K, HEAD_H)
    if cb:
        tab, rho = cb
        report.append("\n| bucket | n | continuation % |")
        report.append("|---|---|---|")
        for _, r in tab.iterrows():
            report.append(f"| {int(r['bucket'])} | {int(r['n']):,} | {r['cont_rate']*100:.2f} |")
        report.append(f"\nSpearman rho = **{rho:.3f}**, spread = "
                      f"**{(tab['cont_rate'].iloc[-1]-tab['cont_rate'].iloc[0])*100:+.2f} pts**")

    # ---- temporal stability
    report.append("\n## 6. Temporal stability (ER(20), 5m, split by year)\n")
    dfy = df.copy()
    dfy["year"] = dfy["dt"].dt.year
    ss = build_samples(df, HEAD_N, HEAD_K, HEAD_H, "ER")
    ss["year"] = dfy["year"].to_numpy()
    report.append("| year | n decided | rho | bottom | top | spread |")
    report.append("|---|---|---|---|---|---|")
    for y, g in ss.groupby("year"):
        r = analyse(g.drop(columns=["year"]), block=10 * (HEAD_N + HEAD_H), reps=200, label=str(y))
        if not r:
            report.append(f"| {y} | insufficient | | | | |")
            continue
        t = r["table"]
        report.append(
            f"| {y} | {r['n_total']:,} | {r['rho']:.3f} | {t['cont_rate'].iloc[0]*100:.2f}% | "
            f"{t['cont_rate'].iloc[-1]*100:.2f}% | {r['spread']*100:+.2f} pts |"
        )

    # ---- trade-shaped test 1: consolidation template
    report.append("\n## 7. Trade-shaped test: the CONSOLIDATION template\n")
    report.append(
        "Conditions on position within the n-bar Donchian range rather than on displacement sign. "
        "`revert` = the barrier pointing back toward the range midpoint was struck first. "
        "The claim under test: revert-rate should rise as ER falls."
    )
    rs = build_range_samples(df, HEAD_N, HEAD_K, HEAD_H)
    r = analyse(rs, block=10 * (HEAD_N + HEAD_H), reps=300, label="revert-to-mid rate by ER decile (all range positions)")
    report.append(fmt(r).replace("continuation %", "revert %"))

    report.append("\nSplit by how close price sits to the range extreme:\n")
    report.append("| position in range | ER decile 0 (most consolidative) | ER decile 9 (most directional) | n |")
    report.append("|---|---|---|---|")
    v = rs[rs["valid"]].reset_index(drop=True)
    edges = np.quantile(v["score"], np.linspace(0, 1, 11))
    eb = np.clip(np.digitize(v["score"], edges[1:-1]), 0, 9)
    dec = (~v["ambig"].to_numpy()) & (v["cont"].to_numpy() | v["rev"].to_numpy())
    for lo, hi, name in [(0.90, 1.01, "top 10% of range"), (0.75, 0.90, "75-90%"),
                         (0.40, 0.60, "middle 40-60%"), (0.0, 0.10, "bottom 10% of range")]:
        pm = (v["pos"].to_numpy() >= lo) & (v["pos"].to_numpy() < hi) & dec
        cells = []
        for j in (0, 9):
            m = pm & (eb == j)
            cells.append(f"{v['cont'].to_numpy()[m].mean()*100:.2f}%" if m.sum() > 200 else "n/a")
        report.append(f"| {name} | {cells[0]} | {cells[1]} | {int(pm.sum()):,} |")

    # ---- trade-shaped test 2: direction template
    report.append("\n## 8. Trade-shaped test: the DIRECTION template\n")
    report.append(
        "Target = n-bar Donchian extreme in the displacement direction plus a buffer. "
        "Stop = range midpoint. Asymmetric by construction, so expectancy in R is the "
        "comparable statistic, not the raw win rate. Costs are NOT included."
    )
    bo = analyse_breakout(build_breakout_samples(df, HEAD_N, HEAD_K, HEAD_H))
    report.append("\n| ER decile | score range | n | win rate | mean R:R | expectancy (R) |")
    report.append("|---|---|---|---|---|---|")
    for _, r2 in bo.iterrows():
        report.append(
            f"| {int(r2['bucket'])} | {r2['score_lo']:.3f} to {r2['score_hi']:.3f} | {int(r2['n']):,} | "
            f"{r2['win_rate']*100:.2f}% | {r2['mean_rr']:.2f} | {r2['exp_R']:+.4f} |"
        )

    txt = "\n".join(report)
    with open(os.path.join(OUT, "GATE0_RESULTS.md"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
