"""Compose the study's two best findings, then size by conviction.

Findings developed separately and never combined:
  - auxiliary data (funding / open interest / positioning / basis) lifted
    walk-forward return from +0.108%/mo to +0.384%/mo at 1h
  - moving the stop to a 15m divergence pivot roughly halves drawdown

Under Breakout rules monthly return is 0.06/maxDD x monthly_R, so halving
drawdown on a better signal should roughly double permitted size. That
composition is tested here, together with two sizing schemes:

  FIXED       equal risk on every trade (everything in the study so far)
  CONVICTION  risk proportional to the model's predicted R, normalised so the
              average risk matches FIXED. Same trades, more capital on the ones
              the model rates higher. This only helps if the predictions are
              genuinely ranked, so decile monotonicity is reported first.

All predictions are purged, embargoed walk-forward. Nothing here sees its own
future.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auxml as AX        # noqa: E402
import exits as X         # noqa: E402
import run_exits as RE    # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def signals_from_model(tf="4h", hold=60, thr=0.2):
    """Walk-forward aux-model predictions turned into directional signals."""
    d = AX.build(tf=tf, hold=hold)
    base, aux, allf = AX.split_features(d)
    pl = AX.walkforward(d, allf, "r_long")
    ps = AX.walkforward(d, allf, "r_short")
    score = np.where(pl >= ps, pl, ps)
    side = np.where(pl >= ps, 1, -1)
    take = np.isfinite(score) & (score >= thr)
    step = pd.Timedelta(tf)
    sig = pd.DataFrame({
        "close_dt": pd.to_datetime(d.loc[take, "dt"].values, utc=True) + step,
        "side": side[take],
        "atr": d.loc[take, "atr"].values,
        "conviction": score[take],
        "symbol": d.loc[take, "symbol"].values,
    })
    return sig, d


def decile_check(sig, realised):
    """Are the model's predictions actually ranked? If conviction deciles are
    not monotone in realised R, conviction sizing cannot help."""
    q = pd.qcut(sig["conviction"], 10, labels=False, duplicates="drop")
    t = pd.DataFrame({"q": q, "r": realised})
    g = t.groupby("q")["r"].agg(["mean", "count"])
    rho = np.corrcoef(g.index.values, g["mean"].values)[0, 1]
    return g, float(rho)


def apply_sizing(r, conviction, scheme, cap=3.0):
    if scheme == "FIXED":
        w = np.ones(len(r))
    else:
        c = np.asarray(conviction, float)
        c = np.clip(c, 0, None)
        w = c / np.nanmean(c) if np.nanmean(c) > 0 else np.ones(len(r))
        w = np.clip(w, 0, cap)
        w = w / np.nanmean(w)          # keep average risk equal to FIXED
    return np.asarray(r) * w, w


def stats(r, months):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 50:
        return None
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(cum) - cum))
    moR = r.sum() / months
    return {"n": len(r), "expR": float(r.mean()), "moR": moR, "maxDD_R": dd,
            "monthly_ret": min(0.06 / dd, 0.02) * moR if dd > 0 else 0.0}


def main(tf="4h", hold=60, thr=0.2, ltf="15min"):
    print(f"building walk-forward aux-model signals ({tf}, thr={thr}) ...")
    sig, d = signals_from_model(tf, hold, thr)
    print(f"  {len(sig):,} signals across {sig.symbol.nunique()} symbols")
    if len(sig) < 300:
        print("  too few signals")
        return

    rows = []
    per_variant = {}
    for name, code in (("BASE", 0), ("TIGHTEN", 1), ("SEQ_TIGHT", 5),
                       ("PARTIAL", 6), ("PARTIAL_TIGHT", 7)):
        parts = []
        for sym in sorted(sig.symbol.unique()):
            ss = sig[sig.symbol == sym]
            try:
                _, m1 = RE.RM.htf_signals(sym, tf)
                ev = RE.ltf_events(sym, ltf)
            except Exception:                       # noqa: BLE001
                continue
            for side in (1, -1):
                s2 = ss[ss.side == side]
                if not len(s2):
                    continue
                e = ev[side]
                out = X.run(s2, m1, e["div_dt"], e["div_lvl"], e["dot_dt"],
                            mode=code, buf_frac=0.05)
                if len(out):
                    out = out.reset_index(drop=True)
                    out["conviction"] = s2["conviction"].values[:len(out)]
                    out["symbol"] = sym
                    parts.append(out)
        if not parts:
            continue
        T = pd.concat(parts).sort_values("close_dt").reset_index(drop=True)
        per_variant[name] = T
        months = ((pd.Timestamp(T.close_dt.max())
                   - pd.Timestamp(T.close_dt.min())).days / 30.44)
        for scheme in ("FIXED", "CONVICTION"):
            rr, w = apply_sizing(T["r"].values, T["conviction"].values, scheme)
            st = stats(rr, months)
            if st:
                st.update({"variant": name, "sizing": scheme})
                rows.append(st)

    res = pd.DataFrame(rows)
    print(f"\n{'variant':<16}{'sizing':<12}{'n':>7}{'expR':>9}"
          f"{'mo R':>9}{'maxDD':>9}{'%/mo':>8}")
    for _, r in res.iterrows():
        print(f"{r.variant:<16}{r.sizing:<12}{int(r.n):>7}{r.expR:>9.4f}"
              f"{r.moR:>9.2f}{r.maxDD_R:>9.1f}{100*r.monthly_ret:>7.2f}%")

    if "BASE" in per_variant:
        T = per_variant["BASE"]
        g, rho = decile_check(T, T["r"].values)
        print(f"\nconviction decile check (does the model rank trades?):")
        print(f"  decile mean R: "
              + " ".join(f"{v:+.2f}" for v in g["mean"].values))
        print(f"  rank correlation decile -> realised R = {rho:+.3f}  "
              f"({'ranked' if rho > 0.4 else 'NOT reliably ranked'})")

    res.to_csv(os.path.join(REP, "combine.csv"), index=False)
    best = res.sort_values("monthly_ret", ascending=False).head(5)
    print("\n=== best combinations ===")
    for _, r in best.iterrows():
        print(f"  {r.variant:<16}{r.sizing:<12}{100*r.monthly_ret:+.2f}%/mo  "
              f"expR {r.expR:+.4f}  maxDD {r.maxDD_R:.1f}R")
    return res, per_variant


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--hold", type=int, default=60)
    p.add_argument("--thr", type=float, default=0.2)
    a = p.parse_args()
    main(a.tf, a.hold, a.thr)
