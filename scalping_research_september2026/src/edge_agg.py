"""Pool gross-edge results across symbols."""
import glob, sys
import numpy as np, pandas as pd

K = ["tf", "family", "variant", "htf", "bias", "H"]

def pooled(tf, wave="w1"):
    df = pd.concat([pd.read_parquet(f) for f in glob.glob(f"../results/edge_*_{tf}_{wave}.parquet")])
    df = df.assign(is_pos=(df.is_sum > 0).astype(int), oos_pos=(df.oos_sum > 0).astype(int))
    g = df.groupby(K)
    a = g[["is_n", "is_sum", "is_sq", "oos_n", "oos_sum", "oos_sq", "is_pos", "oos_pos"]].sum()
    a["n_sym"] = g.size()
    for p in ("is", "oos"):
        n = a[f"{p}_n"].clip(lower=1); m = a[f"{p}_sum"] / n
        a[f"{p}_mean"] = m
        a[f"{p}_t"] = m / np.sqrt((a[f"{p}_sq"] / n - m**2).clip(lower=1e-12) / n)
    return a.reset_index()

if __name__ == "__main__":
    tf = sys.argv[1]
    a = pooled(tf)
    pd.set_option("display.width", 250, "display.max_rows", 200)
    print(tf, "configs:", len(a), "symbols:", a.n_sym.max())
    for thr in (0.0, 0.06, 0.12, 0.20):
        m = (a.is_mean > thr) & (a.oos_mean > thr)
        print(f"gross mean > {thr:.2f}% in BOTH IS and OOS: {m.sum()}  (with >=5 syms positive both: {(m & (a.is_pos>=5) & (a.oos_pos>=5)).sum()})")
    cols = K[1:] + ["n_sym", "is_n", "is_mean", "is_t", "oos_n", "oos_mean", "oos_t", "is_pos", "oos_pos"]
    s = a[(a.is_mean > 0.12) & (a.oos_mean > 0.12) & (a.is_pos >= a.n_sym - 1) & (a.oos_pos >= a.n_sym - 1) & (a.oos_n >= 100)]
    print(s.sort_values("oos_t", ascending=False)[cols].head(60).round(3).to_string())
    print("\nBest per family (IS mean > 0.12 & all-but-one syms positive IS), ranked by OOS mean:")
    b = a[(a.is_mean > 0.12) & (a.is_pos >= a.n_sym - 1) & (a.oos_n >= 100)]
    print(b.sort_values("oos_mean", ascending=False).groupby("family").head(1)[cols].head(40).round(3).to_string())
