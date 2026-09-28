"""Stage-2: pool scan results across symbols and apply survival filters."""
import glob
import sys

import numpy as np
import pandas as pd

KEY = ["tf", "family", "variant", "htf", "bias", "exit"]
YEARS = ["y2020", "y2021", "y2022", "y2023", "y2024", "y2025"]


def load(tf):
    return pd.concat([pd.read_parquet(f) for f in glob.glob(f"../results/scan1_*_{tf}.parquet")], ignore_index=True)


def pool(df):
    df = df.assign(is_pos=(df.is_sum > 0).astype(int), oos_pos=(df.oos_sum > 0).astype(int))
    g = df.groupby(KEY)
    a = g[["is_n", "is_sum", "is_sq", "is_win", "oos_n", "oos_sum", "oos_sq", "oos_win", "is_pos", "oos_pos"] + YEARS].sum()
    a["n_sym"] = g.size()
    a["sl_pct"] = g.sl_pct.median()
    for p in ("is", "oos"):
        n = a[f"{p}_n"].clip(lower=1)
        m = a[f"{p}_sum"] / n
        var = (a[f"{p}_sq"] / n - m ** 2).clip(lower=1e-9)
        a[f"{p}_avg"] = m
        a[f"{p}_t"] = m / np.sqrt(var / n)
        a[f"{p}_wr"] = a[f"{p}_win"] / n
    a["yrs_pos"] = (a[YEARS] > 0).sum(axis=1)
    # R per month summed over all symbols (IS 48 months, OOS 21 months)
    a["is_rpm"] = a.is_sum / 48
    a["oos_rpm"] = a.oos_sum / 21
    a["oos_tpm"] = a.oos_n / 21
    return a.reset_index()


def survivors(a, min_avg=0.03):
    return a[(a.is_avg > min_avg) & (a.oos_avg > min_avg) & (a.is_t > 2.5) & (a.oos_t > 1.5)
             & (a.is_pos >= 4) & (a.oos_pos >= 4) & (a.yrs_pos >= 5)]


if __name__ == "__main__":
    tf = sys.argv[1] if len(sys.argv) > 1 else "5m"
    a = pool(load(tf))
    a.to_parquet(f"../results/pooled_{tf}.parquet")
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_rows", 200)
    cols = KEY[1:] + ["n_sym", "is_n", "is_avg", "is_t", "oos_n", "oos_avg", "oos_t", "is_pos", "oos_pos",
                      "yrs_pos", "oos_rpm", "oos_tpm", "sl_pct"]
    print("configs tested:", len(a))
    print("positive IS avg:", (a.is_avg > 0).mean().round(3), " positive OOS avg:", (a.oos_avg > 0).mean().round(3))
    s = survivors(a)
    print("survivors:", len(s))
    print(s.sort_values("oos_rpm", ascending=False)[cols].head(80).round(3).to_string())
    print("\nBy family: best pooled OOS avg R among configs with IS avg>0 and >=4 positive symbols")
    b = a[(a.is_avg > 0) & (a.is_pos >= 4)]
    print(b.sort_values("oos_avg", ascending=False).groupby("family").head(1)[cols].round(3).to_string())
