"""Diagnostic E006 (declared in LEDGER.md before running): next-day odds from the daily timeframe. Descriptive only.
Usage: uv run python -m tradingstudy.phase3.daily
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.config import DEV_END, DEV_START, REPORTS, SYMBOLS
from tradingstudy.data.guard import load_bars, load_funding
from tradingstudy.features import context, ta
from tradingstudy.phase2.baselines import m1_arrays

OUT = REPORTS / "phase3" / "DAILY_ODDS.md"
SPLIT = pd.Timestamp("2024-01-01", tz="UTC")
DAY_NS = 86400 * 10**9


@nb.njit(cache=True)
def _first_touch(ts, h, l, start, open_px, x):
    """+1 if open+x is touched before open-x within the day, -1 if the reverse, 0 if neither or same minute."""
    n = start.shape[0]
    out = np.zeros(n, dtype=np.int8)
    for k in range(n):
        j = start[k]
        if j >= ts.shape[0]:
            continue
        t_end = ts[j] + DAY_NS
        for i in range(j, ts.shape[0]):
            if ts[i] >= t_end:
                break
            up = h[i] >= open_px[k] + x[k]
            dn = l[i] <= open_px[k] - x[k]
            if up and dn:
                break
            if up:
                out[k] = 1
                break
            if dn:
                out[k] = -1
                break
    return out


def coin_days(sym: str, A: dict) -> pd.DataFrame:
    d = load_bars(sym, "1D", "dev_warmup")
    atr = pd.Series(ta.atr(d["high"], d["low"], d["close"], 14), index=d.index)
    rng = (d["high"] - d["low"]).replace(0, np.nan)
    f = pd.DataFrame(index=d.index)
    f["P1_close_loc"] = pd.cut((d["close"] - d["low"]) / rng, [-0.01, 0.33, 0.67, 1.01], labels=["low", "mid", "high"])
    wick = ((d["high"] - d[["open", "close"]].max(axis=1)) - (d[["open", "close"]].min(axis=1) - d["low"])) / rng
    f["P2_wick_imbalance"] = pd.cut(wick, [-1.01, -0.2, 0.2, 1.01], labels=["lower wick bigger", "balanced", "upper wick bigger"])
    f["P3_day_dir"] = np.where(d["close"] > d["open"], "up day", "down day")
    nxt = d.index + pd.Timedelta(days=1)
    f["P4_next_weekend"] = np.where(nxt.day_of_week >= 5, "weekend", "weekday")
    fz = context.funding_features(load_funding(sym, "dev_warmup"), d.index, 1440)["funding_z"]
    f["P5_funding"] = pd.cut(fz, [-np.inf, -1.5, 1.5, np.inf], labels=["z < -1.5", "middle", "z > +1.5"])
    f["atr"] = atr
    # targets about the NEXT day
    nd = d.shift(-1)
    f["T2_up_ext"] = ((nd["high"] - nd["open"]) > (nd["open"] - nd["low"])).astype(float)
    f.loc[nd["open"].isna(), "T2_up_ext"] = np.nan
    f["next_open"] = nd["open"]
    f["next_day"] = nxt
    f = f[(f.index >= DEV_START) & (f["next_day"] + pd.Timedelta(days=1) <= DEV_END)].dropna(subset=["next_open", "atr"])
    start = np.searchsorted(A["ts"], f["next_day"].dt.as_unit("ns").astype("int64").to_numpy(), side="left").astype(np.int64)
    for x in (0.25, 0.5):
        f[f"T1_first_{x}"] = _first_touch(A["ts"], A["h"], A["l"], start, f["next_open"].to_numpy(), (x * f["atr"]).to_numpy())
    f["coin"] = sym
    f["date"] = f.index
    return f.reset_index(drop=True)


def boot_z(df: pd.DataFrame, col: str, target: str, lo, hi, reps: int = 1000, seed: int = 0) -> tuple[float, float]:
    """Difference P(up | hi bin) - P(up | lo bin) and its z from a day-clustered bootstrap."""
    x = df[df[col].isin([lo, hi])][["date", col, target]]
    diff = x[x[col] == hi][target].mean() - x[x[col] == lo][target].mean()
    dates = x["date"].unique()
    g = {k: v for k, v in x.groupby("date")}
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(reps):
        s = pd.concat([g[dd] for dd in rng.choice(dates, len(dates))])
        sims.append(s[s[col] == hi][target].mean() - s[s[col] == lo][target].mean())
    sd = np.nanstd(sims)
    return diff, diff / sd if sd > 0 else np.nan


def main() -> None:
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    D = pd.concat([coin_days(s, arrays[s]) for s in SYMBOLS], ignore_index=True)
    # T1 as up-first probability among resolved days
    for x in (0.25, 0.5):
        c = D[f"T1_first_{x}"]
        D[f"T1_up_{x}"] = np.where(c == 1, 1.0, np.where(c == -1, 0.0, np.nan))
    targets = {"T1 up first (0.25 ATR)": "T1_up_0.25", "T1 up first (0.5 ATR)": "T1_up_0.5", "T2 bigger up-extension": "T2_up_ext"}
    preds = {"P1_close_loc": ("low", "high"), "P2_wick_imbalance": ("lower wick bigger", "upper wick bigger"),
             "P3_day_dir": ("down day", "up day"), "P4_next_weekend": ("weekday", "weekend"), "P5_funding": ("z < -1.5", "z > +1.5")}
    pct = lambda v: f"{100 * v:.1f}%"
    md = ["# E006: next-day odds from the daily timeframe (descriptive, declared before running)", "",
          f"{D['date'].nunique()} days x 9 coins = {len(D)} coin-days in the dev period (SUI from 2023-05). Unconditional rates: "
          + ", ".join(f"{k} {pct(D[v].mean())}" for k, v in targets.items()) + ".", "",
          "Difference = P(up | second bin) - P(up | first bin). z from a day-clustered bootstrap. Halves: 2022-2023 / 2024-2025.", ""]
    verdicts = []
    for p, (lo, hi) in preds.items():
        md += [f"## {p}", "", "| Target | Bin | Days | P(up) full | P(up) 2022-23 | P(up) 2024-25 |", "|---|---|---|---|---|---|"]
        for tname, t in targets.items():
            for b in D[p].dropna().unique():
                s = D[D[p] == b]
                md.append(f"| {tname} | {b} | {s[t].notna().sum()} | {pct(s[t].mean())} | {pct(s[s.date < SPLIT][t].mean())} | {pct(s[s.date >= SPLIT][t].mean())} |")
        md += ["", f"| Target | Difference ({hi} minus {lo}) full | 2022-23 | 2024-25 | z | Promising? |", "|---|---|---|---|---|---|"]
        for tname, t in targets.items():
            diff, z = boot_z(D, p, t, lo, hi)
            h1 = D[D.date < SPLIT]; h2 = D[D.date >= SPLIT]
            d1 = h1[h1[p] == hi][t].mean() - h1[h1[p] == lo][t].mean()
            d2 = h2[h2[p] == hi][t].mean() - h2[h2[p] == lo][t].mean()
            nmin = min(D[D[p] == lo][t].notna().sum(), D[D[p] == hi][t].notna().sum())
            ok = abs(d1) >= 0.06 and abs(d2) >= 0.06 and np.sign(d1) == np.sign(d2) and abs(z) >= 3 and nmin >= 300
            if ok and t == "T1_up_0.5":
                best = max(D[D[p] == lo][t].mean(), D[D[p] == hi][t].mean(), key=lambda v: abs(v - 0.5))
                ok = best >= 0.55 or best <= 0.45
            verdicts.append((p, tname, ok))
            md.append(f"| {tname} | {100 * diff:+.1f} pts | {100 * d1:+.1f} | {100 * d2:+.1f} | {z:+.2f} | {'YES' if ok else 'no'} |")
        md.append("")
        print("done", p, flush=True)
    n_ok = sum(v[2] for v in verdicts)
    md += ["## Verdict against the declared rule", "",
           f"Predictor/target pairs meeting the rule: {n_ok} of {len(verdicts)}."
           + ("" if n_ok == 0 else " Promising: " + ", ".join(f"{p} / {t}" for p, t, ok in verdicts if ok) + ".")]
    OUT.write_text("\n".join(md) + "\n")
    D.to_parquet(REPORTS.parent / "data" / "results" / "phase3" / "daily_odds.parquet") if (REPORTS.parent / "data" / "results" / "phase3").exists() else None
    print("wrote", OUT, "| promising:", n_ok)


if __name__ == "__main__":
    main()
