"""H4 - deleveraging reversion. See PREREGISTRATION_H4.md.

Treatment and control are run together and reported side by side. The
open-interest condition has to earn its place: if the two arms behave alike,
H4 fails even when the treatment arm makes money.

Levels are imported from hypothesis_h3 so the exit geometry is provably
identical to H3 and only the entry differs.
"""

import csv
import json
import os

import numpy as np

import indicators
import limit_entry
from hypothesis_h3 import STOP_ATR, TARGET_R, TIME_STOP

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DERIV = os.path.join(DATA, "deriv")
WEEK_MS = 7 * 24 * 3600 * 1000

# ---- Pre-registered parameters. Do not tune. ----
MOVE_ATR = 1.0          # |bar return| must exceed this many ATR
PCTL_WINDOW = 500       # trailing window for the dOI percentile
TREAT_PCTL = 0.10       # bottom decile of dOI = positions closing
CTRL_PCTL = 0.90        # top decile = positions opening
WARMUP = 500
# ------------------------------------------------

rng = np.random.default_rng(11)


def load_perp(sym):
    ts, o, h, l, c, v, tb = [], [], [], [], [], [], []
    with open(os.path.join(DERIV, f"{sym}_perp1h.csv")) as fh:
        for r in csv.DictReader(fh):
            ts.append(int(r["open_time"]))
            o.append(float(r["open"]))
            h.append(float(r["high"]))
            l.append(float(r["low"]))
            c.append(float(r["close"]))
            v.append(float(r["volume"]))
            tb.append(float(r["taker_buy_volume"]))
    return (np.array(ts), np.array(o), np.array(h), np.array(l),
            np.array(c), np.array(v), np.array(tb))


def load_oi(sym):
    hours, oi = [], []
    with open(os.path.join(DERIV, f"{sym}_oi1h.csv")) as fh:
        for r in csv.DictReader(fh):
            hours.append(int(r["hour"]))
            oi.append(float(r["open_interest"]))
    return np.array(hours), np.array(oi)


def align(sym):
    """Perp bars restricted to hours with an open-interest observation."""
    ts, o, h, l, c, v, tb = load_perp(sym)
    hrs, oi = load_oi(sym)
    lookup = dict(zip(hrs.tolist(), oi.tolist()))
    keep = np.array([t in lookup for t in ts.tolist()])
    if keep.sum() < 5000:
        return None
    oi_series = np.array([lookup[t] for t in ts[keep].tolist()])
    return (ts[keep], o[keep], h[keep], l[keep], c[keep], v[keep],
            tb[keep], oi_series)


def trailing_pctl(x, window):
    """Rank of x[i] within the preceding `window` values, in [0, 1]."""
    out = np.full(len(x), np.nan)
    for i in range(window, len(x)):
        seg = x[i - window:i]
        out[i] = float(np.mean(seg < x[i]))
    return out


def book(sym, arm):
    a = align(sym)
    if a is None:
        return None
    ts, o, h, l, c, v, tb, oi = a
    n = len(c)
    f = indicators.build(o, h, l, c, v)

    ret = np.zeros(n)
    ret[1:] = (c[1:] - c[:-1]) / c[:-1]
    doi = np.zeros(n)
    doi[1:] = np.where(oi[:-1] > 0, (oi[1:] - oi[:-1]) / oi[:-1], 0.0)
    pct = trailing_pctl(doi, PCTL_WINDOW)

    with np.errstate(divide="ignore", invalid="ignore"):
        flow = np.where(v > 0, 2.0 * tb / v - 1.0, 0.0)

    rows = []
    start = max(WARMUP, PCTL_WINDOW + 1)
    for i in range(start, n - 1):
        atr = f["atr"][i]
        if np.isnan(atr) or atr <= 0 or np.isnan(pct[i]):
            continue
        move = ret[i] * c[i - 1] / atr  # bar move in ATR units
        if abs(move) < MOVE_ATR:
            continue
        if arm == "treatment" and pct[i] > TREAT_PCTL:
            continue
        if arm == "control" and pct[i] < CTRL_PCTL:
            continue

        d = -1 if move > 0 else 1           # fade the move
        res = limit_entry.simulate(i, d, "MARKET", c[i], STOP_ATR * atr, TARGET_R,
                                   TIME_STOP, 0.25, 6, atr, o, h, l, c, n)
        if res is None:
            continue
        rows.append({"symbol": sym, "t": int(ts[i]), "r": res["r_multiple"],
                     "doi": float(doi[i]), "move_atr": float(move),
                     "flow": float(flow[i]), "cost_share": res["cost_share"],
                     "exit": res["exit_reason"]})
    return rows


def summarize(rows):
    r = np.array([x["r"] for x in rows])
    w = r[r > 0]
    loss = r[r <= 0]
    gl = abs(loss.sum())
    aw = w.mean() if len(w) else 0.0
    al = abs(loss.mean()) if len(loss) else 0.0
    return {"n": len(r), "win": 100 * len(w) / len(r),
            "be": 100 * al / (aw + al) if (aw + al) > 0 else float("nan"),
            "avg": float(r.mean()), "tot": float(r.sum()),
            "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
            "cost": 100 * float(np.mean([x["cost_share"] for x in rows])),
            "mean_doi": 100 * float(np.mean([x["doi"] for x in rows]))}


def xs_boot(rows, draws=8000):
    r = np.array([x["r"] for x in rows])
    wk = np.array([x["t"] // WEEK_MS for x in rows])
    ub = np.unique(wk)
    by = {w: np.flatnonzero(wk == w) for w in ub}
    m = np.empty(draws)
    for i in range(draws):
        sel = np.concatenate([by[w] for w in rng.choice(ub, size=len(ub), replace=True)])
        m[i] = r[sel].mean()
    return {"lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
            "p_pos": 100 * float((m > 0).mean()), "weeks": len(ub)}


def diff_boot(treat, ctrl, draws=8000):
    """Bootstrap the treatment-minus-control gap on shared week blocks."""
    rt = np.array([x["r"] for x in treat])
    wt = np.array([x["t"] // WEEK_MS for x in treat])
    rc = np.array([x["r"] for x in ctrl])
    wc = np.array([x["t"] // WEEK_MS for x in ctrl])
    ub = np.unique(np.concatenate([wt, wc]))
    bt = {w: np.flatnonzero(wt == w) for w in ub}
    bc = {w: np.flatnonzero(wc == w) for w in ub}
    d = np.empty(draws)
    for i in range(draws):
        pick = rng.choice(ub, size=len(ub), replace=True)
        it = np.concatenate([bt[w] for w in pick])
        ic = np.concatenate([bc[w] for w in pick])
        if len(it) == 0 or len(ic) == 0:
            d[i] = 0.0
        else:
            d[i] = rt[it].mean() - rc[ic].mean()
    return {"gap": float(np.mean(d)), "lo": float(np.percentile(d, 2.5)),
            "hi": float(np.percentile(d, 97.5)),
            "p_pos": 100 * float((d > 0).mean())}


def main():
    syms = sorted(f[:-9] for f in os.listdir(DERIV) if f.endswith("_oi1h.csv"))
    print(f"symbols with open-interest history: {len(syms)}")

    arms, per_asset = {}, {}
    for arm in ("treatment", "control"):
        allrows = []
        for s in syms:
            try:
                rows = book(s, arm)
            except FileNotFoundError:
                continue
            if not rows:
                continue
            if arm == "treatment" and len(rows) >= 20:
                per_asset[s] = summarize(rows)
            allrows += rows
        arms[arm] = allrows

    print("\n" + "=" * 104)
    print("PER ASSET - treatment arm (large move + OI bottom decile, faded)")
    print("=" * 104)
    print(f"{'asset':<12}{'n':>7}{'win%':>8}{'BE%':>8}{'avgR':>9}{'totR':>9}{'PF':>7}{'meanDOI%':>10}")
    for s in sorted(per_asset, key=lambda k: -per_asset[k]["avg"]):
        a = per_asset[s]
        print(f"{s[:-4]:<12}{a['n']:>7}{a['win']:>8.1f}{a['be']:>8.1f}{a['avg']:>9.3f}"
              f"{a['tot']:>9.1f}{a['pf']:>7.2f}{a['mean_doi']:>10.2f}")
    npos = sum(1 for a in per_asset.values() if a["avg"] > 0)
    print(f"\n  {npos}/{len(per_asset)} assets positive "
          f"({100 * npos / max(len(per_asset), 1):.0f}%)")

    print("\n" + "=" * 104)
    print("ARMS")
    print("=" * 104)
    print(f"{'arm':<14}{'n':>7}{'win%':>8}{'BE%':>8}{'cost%R':>9}{'meanDOI%':>10}"
          f"{'avgR':>9}{'PF':>7}{'95% CI':>22}{'P(>0)':>8}")
    res = {}
    for arm in ("treatment", "control"):
        st = summarize(arms[arm])
        bs = xs_boot(arms[arm])
        res[arm] = {**st, **bs}
        print(f"{arm:<14}{st['n']:>7}{st['win']:>8.1f}{st['be']:>8.1f}{st['cost']:>9.1f}"
              f"{st['mean_doi']:>10.2f}{st['avg']:>9.3f}{st['pf']:>7.2f}"
              f"   [{bs['lo']:+.3f}, {bs['hi']:+.3f}]{bs['p_pos']:>8.1f}")

    gap = diff_boot(arms["treatment"], arms["control"])
    res["gap"] = gap
    print(f"\n  treatment - control gap: {gap['gap']:+.4f} R   "
          f"95% CI [{gap['lo']:+.4f}, {gap['hi']:+.4f}]   P(gap>0) = {gap['p_pos']:.1f}%")

    t = res["treatment"]
    frac = npos / max(len(per_asset), 1)
    beats = t["avg"] > res["control"]["avg"]
    print("\n" + "=" * 104)
    print("VERDICT against the pre-registered H4 criteria")
    print("=" * 104)
    if t["n"] < 1500:
        print(f"  UNDERPOWERED - {t['n']} treatment trades, below the floor of 1,500.")
    elif t["avg"] > 0 and t["lo"] > 0 and frac >= 0.60 and beats:
        print(f"  SUPPORTED - treatment {t['avg']:+.4f} R, 95% CI excludes zero, "
              f"{frac * 100:.0f}% assets positive, and it beats control.")
    elif t["avg"] > 0 and frac >= 0.60 and beats:
        print(f"  SUGGESTIVE - treatment {t['avg']:+.4f} R beats control and "
              f"{frac * 100:.0f}% of assets are positive, but the CI includes zero.")
    else:
        why = []
        if t["avg"] <= 0:
            why.append("treatment mean not positive")
        if t["lo"] <= 0:
            why.append("95% CI includes zero")
        if frac < 0.60:
            why.append(f"only {frac * 100:.0f}% of assets positive")
        if not beats:
            why.append("treatment does NOT beat control - the OI condition is inert")
        print("  NOT SUPPORTED - " + "; ".join(why) + ".")

    json.dump({"arms": res, "per_asset": per_asset, "symbols": syms},
              open(os.path.join(DATA, "hypothesis_h4.json"), "w"), indent=2, default=float)
    print("\nwrote hypothesis_h4.json")


if __name__ == "__main__":
    main()
