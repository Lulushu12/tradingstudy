"""Statistical robustness checks on out/trades.parquet.

Tasks (per system in A,B,WTdiv,MFIdiv and per target rr in 1,2):
  1. FDR (Benjamini-Hochberg) control on Mann-Whitney winner-vs-loser p-values.
  2. Per-year stability (2021..2026) for the 3 smallest-p features, split at the
     pooled median.
  3. Direction split (long vs short) for the 6 smallest-p features.
  4. Candidate filter test for Variant B @ 1:1 (x_trig_wt2 below pooled median
     AND direction-normalized mfi_div_osc_delta above pooled median).
  5. All thresholds are chosen on the full pooled sample only (no per-year
     tuning) -- this entire script is in-sample exploration, not out-of-sample
     validation.

Reads out/trades.parquet (read-only). Writes out/robustness.md.
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

SYSTEMS = ("A", "B", "WTdiv", "MFIdiv")
RRS = (1, 2)
YEARS = (2021, 2022, 2023, 2024, 2025, 2026)

# Same feature set as analyze.py FEATURES (direction-normalized, higher = deeper
# in the trade's favor).
FEATURES = [
    "x_trig_wt2", "x_trig_wt1", "x_trig_mfi",
    "x_wt_pivot_osc", "x_wt_anchor_osc", "x_mfi_pivot_osc", "x_mfi_anchor_osc",
    "x_wt_div_delta", "x_mfi_div_delta", "x_wt_div_price", "x_mfi_div_price",
    "wt_anchor_age", "mfi_anchor_age", "gap_bars",
    "x_h1_wt2", "x_h1_mfi", "x_h4_wt2", "x_h4_mfi",
    "x_h1_wt2_wave", "x_h1_mfi_wave", "x_h4_wt2_wave", "x_h4_mfi_wave",
    "h1_wt2_wave_aligned", "h4_wt2_wave_aligned",
    "h1_wt2_wave_age", "h4_wt2_wave_age",
    "atr_pct",
]


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or len(b) == 0:
        return np.nan
    m, n = len(a), len(b)
    allv = np.concatenate([a, b])
    r = pd.Series(allv).rank().to_numpy()
    ra = r[:m].sum()
    u = ra - m * (m + 1) / 2
    return 2 * u / (m * n) - 1


def prep(df):
    df = df.copy()
    d = df["direction"].to_numpy(float)
    df["x_wt_div_delta"] = d * df.get("wt_div_osc_delta", np.nan)
    df["x_mfi_div_delta"] = d * df.get("mfi_div_osc_delta", np.nan)
    df["x_wt_div_price"] = -d * df.get("wt_div_price_pct", np.nan)
    df["x_mfi_div_price"] = -d * df.get("mfi_div_price_pct", np.nan)
    return df


def winner_loser_table(m, rr, min_n=10):
    y = m[f"win{rr}"]
    rows = []
    for f in FEATURES:
        if f not in m.columns:
            continue
        v = m[f].astype(float)
        w, l = v[(y == 1) & v.notna()], v[(y == 0) & v.notna()]
        if len(w) < min_n or len(l) < min_n:
            continue
        try:
            p = mannwhitneyu(w, l, alternative="two-sided").pvalue
        except ValueError:
            p = np.nan
        rows.append(dict(feature=f, n_win=len(w), n_loss=len(l),
                          mean_win=w.mean(), mean_loss=l.mean(),
                          med_win=w.median(), med_loss=l.median(),
                          mw_p=p, cliffs_d=cliffs_delta(w, l)))
    t = pd.DataFrame(rows)
    return t.sort_values("mw_p").reset_index(drop=True) if len(t) else t


def bh_qvalues(pvals):
    """Benjamini-Hochberg FDR q-values. NaNs pass through as NaN."""
    p = np.asarray(pvals, dtype=float)
    n = np.sum(~np.isnan(p))
    q = np.full_like(p, np.nan)
    if n == 0:
        return q
    idx = np.where(~np.isnan(p))[0]
    order = idx[np.argsort(p[idx])]
    ranked_p = p[order]
    m = len(order)
    raw_q = ranked_p * m / (np.arange(m) + 1)
    # enforce monotonicity (step-up): q_i = min(q_i, q_{i+1}, ..., q_m)
    q_adj = np.minimum.accumulate(raw_q[::-1])[::-1]
    q_adj = np.clip(q_adj, 0, 1)
    q[order] = q_adj
    return q


def median_split_winrate(sub, rr, feat, thresh):
    y = sub[f"win{rr}"]
    v = sub[feat].astype(float)
    ok = v.notna() & y.notna()
    hi = y[ok & (v >= thresh)]
    lo = y[ok & (v < thresh)]
    return dict(n_hi=len(hi), wr_hi=hi.mean() if len(hi) else np.nan,
                n_lo=len(lo), wr_lo=lo.mean() if len(lo) else np.nan)


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    if isinstance(x, (int, np.integer)):
        return str(x)
    return f"{x:.{nd}f}"


def df_to_md(df, float_cols=None, nd=3):
    if len(df) == 0:
        return "_(none)_\n"
    d = df.copy()
    float_cols = float_cols or [c for c in d.columns if d[c].dtype.kind == "f"]
    for c in float_cols:
        d[c] = d[c].apply(lambda x: fmt(x, nd))
    cols = list(d.columns)
    lines = ["| " + " | ".join(cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in d.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines) + "\n"


def main():
    raw = pd.read_parquet(os.path.join(OUT, "trades.parquet"))
    m_all = prep(raw)
    m_all = m_all[~m_all["skip"]]

    md = []
    exec_summary_lines = []
    fdr_survivors_all = []  # collect across all system x rr for exec summary

    # ---------------- TASK 1: FDR control ----------------
    md.append("## 1. FDR control (Benjamini-Hochberg, q < 0.10)\n")
    task1_tables = {}  # (system, rr) -> wl table with q added
    for system in SYSTEMS:
        s = m_all[m_all["system"] == system]
        for rr in RRS:
            sub = s[s[f"win{rr}"].notna()]
            if len(sub) < 50:
                continue
            wl = winner_loser_table(sub, rr)
            if len(wl) == 0:
                task1_tables[(system, rr)] = wl
                continue
            wl["q_bh"] = bh_qvalues(wl["mw_p"].to_numpy())
            task1_tables[(system, rr)] = wl
            surv = wl[wl["q_bh"] < 0.10]
            if len(surv):
                for _, r in surv.iterrows():
                    fdr_survivors_all.append(dict(system=system, rr=rr, **r.to_dict()))

    if fdr_survivors_all:
        surv_df = pd.DataFrame(fdr_survivors_all)[
            ["system", "rr", "feature", "n_win", "n_loss", "mw_p", "q_bh", "cliffs_d"]]
        md.append(f"**{len(surv_df)} (system, rr, feature) combination(s) survive q < 0.10:**\n")
        md.append(df_to_md(surv_df, float_cols=["mw_p", "q_bh", "cliffs_d"], nd=4))
        exec_summary_lines.append(
            f"- FDR (q<0.10): {len(surv_df)} feature/system/rr combo(s) survive -- "
            f"see section 1 for the list."
        )
    else:
        md.append("**No feature survives Benjamini-Hochberg q < 0.10 in ANY system x rr "
                   "table.** Every winner-vs-loser gap in the raw stats CSVs is "
                   "consistent with multiple-testing noise once corrected for the "
                   "~26 features tested per table.\n")
        exec_summary_lines.append(
            "- FDR (q<0.10): NOTHING survives in any system x rr table -- all raw "
            "p-value hits are multiple-testing noise."
        )

    # full per-table detail (top rows with p and q) for reference
    md.append("\n### Full per-table detail (all features, sorted by p, with q)\n")
    for system in SYSTEMS:
        for rr in RRS:
            wl = task1_tables.get((system, rr))
            if wl is None or len(wl) == 0:
                continue
            md.append(f"\n**{system} @ {rr}:1** (n_win+n_loss shown per feature)\n")
            disp = wl[["feature", "n_win", "n_loss", "mean_win", "mean_loss",
                       "mw_p", "q_bh", "cliffs_d"]]
            md.append(df_to_md(disp, float_cols=["mean_win", "mean_loss", "mw_p", "q_bh", "cliffs_d"], nd=4))

    # ---------------- TASK 2: per-year stability ----------------
    md.append("\n## 2. Per-year stability (top-3 smallest-p features per system x rr)\n")
    md.append("Split at the POOLED median (computed once on the full system x rr "
               "sample, not per year). 'Stable' requires the sign of "
               "(winrate_above - winrate_below) to be consistent in at least 4 "
               "of the 6 years (2021-2026).\n")
    stable_findings = []
    for system in SYSTEMS:
        s = m_all[m_all["system"] == system]
        for rr in RRS:
            sub = s[s[f"win{rr}"].notna()]
            if len(sub) < 50:
                continue
            wl = task1_tables.get((system, rr))
            if wl is None or len(wl) == 0:
                continue
            top3 = wl.head(3)["feature"].tolist()
            md.append(f"\n**{system} @ {rr}:1** -- top-3 by p: {top3}\n")
            for feat in top3:
                thresh = sub[feat].astype(float).median()
                rows = []
                signs = []
                for yr in YEARS:
                    yrsub = sub[sub["year"] == yr]
                    if len(yrsub) == 0:
                        rows.append(dict(year=yr, n_hi=0, wr_hi=np.nan, n_lo=0, wr_lo=np.nan, diff=np.nan))
                        continue
                    r = median_split_winrate(yrsub, rr, feat, thresh)
                    diff = (r["wr_hi"] - r["wr_lo"]) if (r["n_hi"] and r["n_lo"]) else np.nan
                    rows.append(dict(year=yr, n_hi=r["n_hi"], wr_hi=r["wr_hi"],
                                      n_lo=r["n_lo"], wr_lo=r["wr_lo"], diff=diff))
                    if not np.isnan(diff):
                        signs.append(np.sign(diff))
                pos = sum(1 for x in signs if x > 0)
                neg = sum(1 for x in signs if x < 0)
                consistent = max(pos, neg)
                stable = consistent >= 4
                md.append(f"pooled median({feat}) = {thresh:.4g}; "
                           f"sign consistency = {consistent}/6 years "
                           f"({'STABLE' if stable else 'not stable'})\n")
                yt = pd.DataFrame(rows)
                md.append(df_to_md(yt, float_cols=["wr_hi", "wr_lo", "diff"], nd=3))
                if stable:
                    stable_findings.append(dict(system=system, rr=rr, feature=feat,
                                                 consistency=f"{consistent}/6"))
    if stable_findings:
        md.append("\n**Features qualifying as stable (>=4/6 years consistent sign):**\n")
        md.append(df_to_md(pd.DataFrame(stable_findings)))
        exec_summary_lines.append(
            f"- Per-year stability: {len(stable_findings)} feature(s) show a "
            f"consistent-sign split across >=4/6 years -- see section 2."
        )
    else:
        md.append("\n**No feature among the top-3-by-p in any system x rr table shows "
                   "a consistent-sign winrate split across >=4 of 6 years.** "
                   "Even the nominally best p-value features flip sign year to year.\n")
        exec_summary_lines.append(
            "- Per-year stability: NONE of the top-3-by-p features hold a consistent "
            "sign across >=4/6 years."
        )

    # ---------------- TASK 3: direction split ----------------
    md.append("\n## 3. Direction split (long vs short) for top-6 smallest-p features\n")
    one_sided_flags = []
    for system in SYSTEMS:
        s = m_all[m_all["system"] == system]
        for rr in RRS:
            sub = s[s[f"win{rr}"].notna()]
            if len(sub) < 50:
                continue
            wl = task1_tables.get((system, rr))
            if wl is None or len(wl) == 0:
                continue
            top6 = wl.head(6)["feature"].tolist()
            md.append(f"\n**{system} @ {rr}:1** -- top-6 by pooled p: {top6}\n")
            rows = []
            for feat in top6:
                pooled_row = wl[wl["feature"] == feat].iloc[0]
                for side_name, side_val in (("long", 1), ("short", -1)):
                    d = sub[sub["direction"] == side_val]
                    y = d[f"win{rr}"]
                    v = d[feat].astype(float)
                    w = v[(y == 1) & v.notna()]
                    l = v[(y == 0) & v.notna()]
                    if len(w) < 10 or len(l) < 10:
                        rows.append(dict(feature=feat, side=side_name, n_win=len(w),
                                          n_loss=len(l), mean_win=np.nan, mean_loss=np.nan,
                                          mw_p=np.nan, cliffs_d=np.nan, note="insufficient n"))
                        continue
                    try:
                        p = mannwhitneyu(w, l, alternative="two-sided").pvalue
                    except ValueError:
                        p = np.nan
                    cd = cliffs_delta(w, l)
                    rows.append(dict(feature=feat, side=side_name, n_win=len(w),
                                      n_loss=len(l), mean_win=w.mean(), mean_loss=l.mean(),
                                      mw_p=p, cliffs_d=cd, note=""))
                # flag: pooled p<0.05 but one side p>=0.05 or opposite-sign cliffs_d between sides
                dr = [r for r in rows if r["feature"] == feat]
                long_r = next((r for r in dr if r["side"] == "long"), None)
                short_r = next((r for r in dr if r["side"] == "short"), None)
                if long_r and short_r and pooled_row["mw_p"] < 0.05:
                    lp, sp = long_r.get("mw_p"), short_r.get("mw_p")
                    lcd, scd = long_r.get("cliffs_d"), short_r.get("cliffs_d")
                    one_side_only = False
                    reason = ""
                    if (lp is not None and not np.isnan(lp) and sp is not None and not np.isnan(sp)):
                        if (lp < 0.05) != (sp < 0.05):
                            one_side_only = True
                            reason = f"significant on {'long' if lp < 0.05 else 'short'} only (p_long={lp:.3f}, p_short={sp:.3f})"
                        elif not np.isnan(lcd) and not np.isnan(scd) and np.sign(lcd) != np.sign(scd) and abs(lcd) > 0.05 and abs(scd) > 0.05:
                            one_side_only = True
                            reason = f"opposite-sign effect (cliffs_d long={lcd:.3f}, short={scd:.3f})"
                    else:
                        one_side_only = True
                        reason = "insufficient n on one side to even test"
                    if one_side_only:
                        one_sided_flags.append(dict(system=system, rr=rr, feature=feat, reason=reason))
            dtab = pd.DataFrame(rows)
            md.append(df_to_md(dtab, float_cols=["mean_win", "mean_loss", "mw_p", "cliffs_d"], nd=4))

    if one_sided_flags:
        md.append("\n**Patterns flagged as one-side-only:**\n")
        md.append(df_to_md(pd.DataFrame(one_sided_flags)))
        exec_summary_lines.append(
            f"- Direction split: {len(one_sided_flags)} pattern(s) flagged as "
            f"existing on only one side (long or short) -- see section 3."
        )
    else:
        md.append("\n**No pooled-significant pattern (p<0.05) among the top-6 features "
                   "was flagged as one-side-only; where data allowed testing both sides, "
                   "effects were directionally consistent (or neither side was significant).**\n")
        exec_summary_lines.append(
            "- Direction split: no flagged one-side-only patterns among top-6 features."
        )

    # ---------------- TASK 4: candidate filter test (Variant B @ 1:1) ----------------
    md.append("\n## 4. Candidate filter test -- Variant B @ 1:1\n")
    md.append("Filter: `x_trig_wt2 < pooled_median(x_trig_wt2)` AND "
               "`x_mfi_div_delta > pooled_median(x_mfi_div_delta)` "
               "(x_mfi_div_delta = direction-normalized mfi_div_osc_delta, per analyze.py prep()).\n")
    md.append("Thresholds are fixed once on the FULL pooled Variant-B/1:1 sample "
               "(sanity guard, task 5) and then only *applied* per year -- never "
               "re-tuned per year.\n")

    sB = m_all[m_all["system"] == "B"]
    subB1 = sB[sB["win1"].notna()]
    med_trig = subB1["x_trig_wt2"].astype(float).median()
    med_mfi = subB1["x_mfi_div_delta"].astype(float).median()
    md.append(f"pooled median x_trig_wt2 = {med_trig:.4g}; "
               f"pooled median x_mfi_div_delta = {med_mfi:.4g}\n")

    mask = (subB1["x_trig_wt2"].astype(float) < med_trig) & \
           (subB1["x_mfi_div_delta"].astype(float) > med_mfi)
    filt = subB1[mask]
    baseline_wr, baseline_netR = 0.523, -0.038

    n_f = len(filt)
    wr_f = filt["win1"].mean() if n_f else np.nan
    netR_f = filt["netR1"].mean() if n_f else np.nan
    fee_f = filt["fee_r"].mean() if n_f else np.nan
    fee_all = subB1["fee_r"].mean()

    breakeven_nofee = 0.5
    breakeven_withfee_filt = 0.5 + fee_f / 2 if n_f and not np.isnan(fee_f) else np.nan
    breakeven_withfee_all = 0.5 + fee_all / 2

    summ = pd.DataFrame([dict(
        n=n_f, winrate=wr_f, avg_netR1=netR_f, avg_fee_r=fee_f,
        baseline_winrate=baseline_wr, baseline_netR=baseline_netR,
    )])
    md.append(df_to_md(summ, float_cols=["winrate", "avg_netR1", "avg_fee_r",
                                          "baseline_winrate", "baseline_netR"], nd=4))

    md.append(f"\nBreakeven winrate at 1:1 with no fees = **{breakeven_nofee:.3f}**. "
               f"Breakeven winrate at 1:1 given the FILTERED subset's avg fee_r "
               f"({fmt(fee_f, 4)}) = **{fmt(breakeven_withfee_filt, 4)}** "
               f"(for reference, using the whole Variant-B/1:1 avg fee_r "
               f"{fee_all:.4f}, breakeven = {breakeven_withfee_all:.4f}).\n")
    if n_f and not np.isnan(wr_f):
        clears = wr_f >= breakeven_withfee_filt
        md.append(f"Filtered winrate {wr_f:.4f} "
                   f"{'CLEARS' if clears else 'does NOT clear'} the fee-adjusted "
                   f"breakeven of {breakeven_withfee_filt:.4f} "
                   f"(observed avg_netR1 = {fmt(netR_f, 4)}, "
                   f"{'>' if netR_f is not None and not np.isnan(netR_f) and netR_f > 0 else '<='} 0, "
                   f"as expected).\n")
    else:
        md.append("Filtered subset is empty or has no valid win1 -- cannot evaluate.\n")

    md.append("\n### Per-year breakdown of the filtered subset\n")
    yr_rows = []
    for yr in YEARS:
        g = filt[filt["year"] == yr]
        yr_rows.append(dict(year=yr, n=len(g),
                             winrate=g["win1"].mean() if len(g) else np.nan,
                             avg_netR1=g["netR1"].mean() if len(g) else np.nan,
                             avg_fee_r=g["fee_r"].mean() if len(g) else np.nan))
    yr_df = pd.DataFrame(yr_rows)
    md.append(df_to_md(yr_df, float_cols=["winrate", "avg_netR1", "avg_fee_r"], nd=4))

    if n_f:
        exec_summary_lines.append(
            f"- Variant B @1:1 filter: n={n_f}, winrate={fmt(wr_f,3)}, "
            f"avg_netR1={fmt(netR_f,3)} vs baseline (n={len(subB1)}, wr=0.523, "
            f"netR=-0.038); fee-adjusted breakeven wr={fmt(breakeven_withfee_filt,3)}."
        )
    else:
        exec_summary_lines.append(
            "- Variant B @1:1 filter: the combined filter selects ZERO trades -- "
            "cannot evaluate."
        )

    # ---------------- assemble file ----------------
    header = ["# Statistical Robustness Report\n",
              f"Generated by robustness.py from `out/trades.parquet` "
              f"({len(m_all)} non-skip rows, systems={SYSTEMS}, rr={RRS}, "
              f"years={YEARS[0]}-{YEARS[-1]}).\n",
              "\n## Executive summary\n"]
    header += [l + "\n" for l in exec_summary_lines]
    header.append(
        "- **Sanity guard**: everything below is IN-SAMPLE exploration on the full "
        "history. All thresholds/medians were fixed on the full pooled sample "
        "before being applied per year or per direction -- none were re-tuned "
        "per year. Nothing here has been validated out-of-sample.\n"
    )

    with open(os.path.join(OUT, "robustness.md"), "w") as fh:
        fh.write("".join(header) + "\n" + "\n".join(md))

    print("".join(header))
    print(f"\n[wrote out/robustness.md, {os.path.getsize(os.path.join(OUT, 'robustness.md'))} bytes]")


if __name__ == "__main__":
    main()
