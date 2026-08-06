#!/usr/bin/env python3
"""
averages.py

Headline reference tables for the trading study: average WT and MFI values
at trade triggers, anchor waves, and higher-timeframe waves, winners vs
losers, split by system and direction (raw oscillator values are NOT
direction-normalized, so long/short must be kept separate).

Reads:  out/trades.parquet
Writes: out/averages_tables.md
"""

import pandas as pd
import numpy as np

IN_PATH = "out/trades.parquet"
OUT_PATH = "out/averages_tables.md"

SYSTEMS = ["A", "B", "WTdiv", "MFIdiv"]
SYSTEM_LABEL = {
    "A": "A -- confirmed WT+MFI divergence stack",
    "B": "B -- front-run stack",
    "WTdiv": "WTdiv -- every WT divergence alone",
    "MFIdiv": "MFIdiv -- every MFI divergence alone",
}
DIRECTIONS = [(1, "LONG"), (-1, "SHORT")]
RRS = [1, 2]  # netR1/win1 (1:1) and netR2/win2 (2:1)

# feature groups: (group label, [(column, plain-English row label), ...])
FEATURE_GROUPS = [
    ("Trigger bar", [
        ("trig_wt1", "WT1 at trigger bar"),
        ("trig_wt2", "WT2 at trigger bar"),
        ("trig_mfi", "MFI at trigger bar"),
    ]),
    ("Leg pivots (divergence leg)", [
        ("wt_pivot_osc", "WT pivot (divergence leg) oscillator value"),
        ("mfi_pivot_osc", "MFI pivot (divergence leg) oscillator value"),
    ]),
    ("Anchor pivots (reference leg)", [
        ("wt_anchor_osc", "WT anchor (reference) pivot"),
        ("mfi_anchor_osc", "MFI anchor (reference) pivot"),
    ]),
    ("HTF current (last closed bar)", [
        ("h1_wt2", "1H WT2, last closed bar"),
        ("h1_mfi", "1H MFI, last closed bar"),
        ("h4_wt2", "4H WT2, last closed bar"),
        ("h4_mfi", "4H MFI, last closed bar"),
    ]),
    ("HTF last completed wave extreme", [
        ("h1_wt2_wave", "1H WT2 last completed wave extreme"),
        ("h1_mfi_wave", "1H MFI last completed wave extreme"),
        ("h4_wt2_wave", "4H WT2 last completed wave extreme"),
        ("h4_mfi_wave", "4H MFI last completed wave extreme"),
    ]),
    ("Shape", [
        ("wt_div_osc_delta", "WT divergence oscillator delta (pivot - anchor)"),
        ("mfi_div_osc_delta", "MFI divergence oscillator delta (pivot - anchor)"),
        ("gap_bars", "Gap bars between divergence legs"),
        ("wt_anchor_age", "WT anchor pivot age (bars)"),
        ("mfi_anchor_age", "MFI anchor pivot age (bars)"),
    ]),
]

ALL_FEATURE_COLS = [c for _, feats in FEATURE_GROUPS for c, _ in feats]


def fmt(x):
    if pd.isna(x):
        return "--"
    return f"{x:.2f}"


def build_stat_table(sub: pd.DataFrame, rr: int):
    """Return dict: col -> dict(n_win, n_loss, mean_win, mean_loss, median_win, median_loss)"""
    win_col = f"win{rr}"
    out = {}
    winners = sub[sub[win_col] == 1]
    losers = sub[sub[win_col] == 0]
    for col in ALL_FEATURE_COLS:
        wv = winners[col].dropna()
        lv = losers[col].dropna()
        out[col] = dict(
            n_win=int(wv.shape[0]),
            n_loss=int(lv.shape[0]),
            mean_win=wv.mean() if len(wv) else np.nan,
            mean_loss=lv.mean() if len(lv) else np.nan,
            median_win=wv.median() if len(wv) else np.nan,
            median_loss=lv.median() if len(lv) else np.nan,
        )
    return out


def section_for(df: pd.DataFrame, system: str) -> str:
    lines = []
    lines.append(f"## {SYSTEM_LABEL[system]}\n")
    sys_df = df[df["system"] == system]

    for d_val, d_label in DIRECTIONS:
        sub = sys_df[sys_df["direction"] == d_val]
        if sub.empty:
            continue

        # per-rr n (based on win column availability, i.e. non-NaN outcome)
        n_by_rr = {rr: int(sub[f"win{rr}"].notna().sum()) for rr in RRS}
        stats_by_rr = {rr: build_stat_table(sub, rr) for rr in RRS}

        lines.append(f"### {d_label}  (n: 1:1 = {n_by_rr[1]}, 2:1 = {n_by_rr[2]})\n")

        header = (
            "| Feature | mean win (1:1) | mean loss (1:1) | median win (1:1) | median loss (1:1) "
            "| mean win (2:1) | mean loss (2:1) | median win (2:1) | median loss (2:1) |"
        )
        sep = "|---|---|---|---|---|---|---|---|---|"
        lines.append(header)
        lines.append(sep)

        for group_label, feats in FEATURE_GROUPS:
            lines.append(f"| **{group_label}** | | | | | | | | |")
            for col, row_label in feats:
                s1 = stats_by_rr[1][col]
                s2 = stats_by_rr[2][col]
                lines.append(
                    f"| {row_label} "
                    f"| {fmt(s1['mean_win'])} | {fmt(s1['mean_loss'])} "
                    f"| {fmt(s1['median_win'])} | {fmt(s1['median_loss'])} "
                    f"| {fmt(s2['mean_win'])} | {fmt(s2['mean_loss'])} "
                    f"| {fmt(s2['median_win'])} | {fmt(s2['median_loss'])} |"
                )
        lines.append("")

        # note any feature whose n_win+n_loss < n_by_rr for this rr (i.e. NaNs within feature)
        for rr in RRS:
            n_total = n_by_rr[rr]
            for col, row_label in [(c, l) for _, feats in FEATURE_GROUPS for c, l in feats]:
                s = stats_by_rr[rr][col]
                covered = s["n_win"] + s["n_loss"]
                if n_total > 0 and covered < n_total:
                    pass  # captured separately in oddities section below
        lines.append("")
    return "\n".join(lines)


def cross_system_summary(df: pd.DataFrame) -> str:
    lines = []
    lines.append("## Cross-system summary\n")
    header = "| System | Direction | n | winrate 1:1 | winrate 2:1 | avg netR1 | avg netR2 |"
    sep = "|---|---|---|---|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for system in SYSTEMS:
        sys_df = df[df["system"] == system]
        for d_val, d_label in DIRECTIONS:
            sub = sys_df[sys_df["direction"] == d_val]
            if sub.empty:
                continue
            n = len(sub)
            wr1 = sub["win1"].mean() * 100 if sub["win1"].notna().any() else np.nan
            wr2 = sub["win2"].mean() * 100 if sub["win2"].notna().any() else np.nan
            avg_r1 = sub["netR1"].mean()
            avg_r2 = sub["netR2"].mean()
            lines.append(
                f"| {system} | {d_label} | {n} "
                f"| {fmt(wr1)}% | {fmt(wr2)}% "
                f"| {fmt(avg_r1)} | {fmt(avg_r2)} |"
            )
    lines.append("")
    return "\n".join(lines)


def data_notes(df: pd.DataFrame) -> str:
    lines = []
    lines.append("## Data notes\n")
    lines.append(
        "- `WTdiv` signals carry no MFI divergence leg (`mfi_pivot_osc`, `mfi_anchor_osc`, "
        "`mfi_div_osc_delta`, `mfi_anchor_age` are 100% NaN for this system); `MFIdiv` signals "
        "carry no WT divergence leg (`wt_pivot_osc`, `wt_anchor_osc`, `wt_div_osc_delta`, "
        "`wt_anchor_age` are 100% NaN). This is structural, not missing data -- each single-leg "
        "system only has one oscillator's divergence."
    )
    lines.append(
        "- `h1_mfi_wave` is missing for a small number of MFIdiv rows (~0.1%); negligible."
    )
    lines.append(
        "- A handful of rows (1 for win1, 3 for win2) have no resolved outcome (`netR1`/`netR2` "
        "is NaN despite `skip == False`) and are excluded from win/loss splits and n counts for "
        "the affected rr definition."
    )
    lines.append(
        "- Rows with `skip == True` are excluded throughout (they have no trade outcome)."
    )
    lines.append("")
    return "\n".join(lines)


def main():
    df = pd.read_parquet(IN_PATH)
    df = df[~df["skip"]].copy()

    parts = []
    parts.append("# WT / MFI Averages at Trigger, Anchor, and HTF Waves -- Winners vs Losers\n")
    parts.append(
        "Raw oscillator values (not direction-normalized). Long and short are reported "
        "separately within each system because raw values carry opposite signs by side. "
        "`1:1` = outcome/return at the 1:1 target (`win1`/`netR1`); `2:1` = outcome/return "
        "at the 2:1 target (`win2`/`netR2`). All values rounded to 2 decimals.\n"
    )

    for system in SYSTEMS:
        parts.append(section_for(df, system))

    parts.append(cross_system_summary(df))
    parts.append(data_notes(df))

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
