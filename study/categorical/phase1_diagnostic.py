"""Why did Phase 1 collapse from Gate 0's +0.1196 R to -0.0005 R at zero cost?

Phase 1 is negative before a single basis point of cost is charged, so friction is
not the cause. Something between the Gate 0 measurement and the frozen Phase 1
spec destroyed the gross edge. This attributes the drop to specific rule changes.

This is diagnosis, NOT resurrection. CATEGORICAL_SPEC.md is frozen and the system
is dead as specified regardless of what this finds. The question being answered is
narrower and it matters: did the edge die because of a modelling choice I made, or
because the edge was never tradeable in the first place?

Tightenings applied between Gate 0 and Phase 1:
  A. threshold: pooled full-sample decile edge -> causal expanding 10th percentile
  B. threshold population: quantile over filtered valid signals -> over all bars
  C. both-touched bars: excluded -> resolved as full losses
  D. position management: every signal taken -> one position at a time
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate0  # noqa: E402
import phase1  # noqa: E402
from classifiers import atr, efficiency_ratio  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))


def signal_frame(df):
    """Every bar's fade setup, before any threshold or position rule is applied."""
    a = df["atr"].to_numpy()
    er = df["er"].to_numpy()
    thr = df["er_thr"].to_numpy()
    r_hi, r_lo, mid = df["r_hi"].to_numpy(), df["r_lo"].to_numpy(), df["mid"].to_numpy()
    disp = df["disp"].to_numpy()
    entry = df["open"].shift(-1).to_numpy()

    side = np.where(disp > 0, -1, 1)
    stop = np.where(side == -1, r_hi + phase1.ATR_BUF * a, r_lo - phase1.ATR_BUF * a)
    tgt = mid
    up, dn = np.maximum(tgt, stop), np.minimum(tgt, stop)
    res = gate0.barrier_race(
        df, np.nan_to_num(up, nan=np.inf), np.nan_to_num(dn, nan=-np.inf), phase1.MAX_HOLD
    )
    tgt_up = tgt > stop
    won = np.where(tgt_up, res == gate0.UP, res == gate0.DOWN)
    lost = np.where(tgt_up, res == gate0.DOWN, res == gate0.UP)
    both = res == gate0.BOTH

    reward, risk = np.abs(tgt - entry), np.abs(entry - stop)
    rr = reward / np.where(risk > 0, risk, np.nan)
    geom_ok = (
        np.isfinite(rr) & (disp != 0) & np.isfinite(entry) & np.isfinite(a)
        & (reward > 0.5 * a) & (risk > 0.5 * a) & (rr < 20)
        & np.where(side == 1, tgt > entry, tgt < entry)
    )
    return pd.DataFrame({
        "er": er, "thr": thr, "won": won, "lost": lost, "both": both,
        "rr": rr, "geom_ok": geom_ok, "resolved": res != gate0.PENDING,
    })


def exp_R(sf, mask, both_to_stop):
    """Gross expectancy in R over the selected signals."""
    m = mask & sf["geom_ok"].to_numpy() & sf["resolved"].to_numpy()
    won, lost, both = sf["won"].to_numpy(), sf["lost"].to_numpy(), sf["both"].to_numpy()
    rr = sf["rr"].to_numpy()
    if both_to_stop:
        sel = m & (won | lost | both)
        w = won[sel] & ~both[sel]
        r = np.where(w, rr[sel], -1.0)
    else:
        sel = m & (won | lost)
        r = np.where(won[sel], rr[sel], -1.0)
    return len(r), (won[sel] & ~(both[sel] if both_to_stop else False)).mean(), r.mean()


def main():
    df = phase1.prepare()
    sf = signal_frame(df)
    er = sf["er"].to_numpy()
    thr = sf["thr"].to_numpy()
    geom = sf["geom_ok"].to_numpy() & sf["resolved"].to_numpy()

    L = ["# Phase 1 diagnostic: what destroyed the gross edge", ""]
    L.append(
        "Phase 1 returns -0.0005 R at zero cost against Gate 0's +0.1196 R. Friction is not the "
        "cause. Each row below applies one more tightening, so the drop can be attributed."
    )
    L.append("\n| step | configuration | signals | win rate | gross exp (R) |")
    L.append("|---|---|---|---|---|")

    # Step 1: Gate 0 exactly. Pooled decile edge over the FILTERED valid population.
    valid_er = er[geom & np.isfinite(er)]
    pooled_edge = np.quantile(valid_er, 0.10)
    m1 = np.isfinite(er) & (er <= pooled_edge)
    n, wr, e = exp_R(sf, m1, both_to_stop=False)
    L.append(f"| 1 | Gate 0 baseline: pooled edge on filtered set, both-hits excluded | {n} | {wr*100:.1f}% | **{e:+.4f}** |")

    # Step 2: pooled edge, but quantile taken over ALL bars rather than filtered ones.
    all_edge = np.nanquantile(er, 0.10)
    m2 = np.isfinite(er) & (er <= all_edge)
    n, wr, e = exp_R(sf, m2, both_to_stop=False)
    L.append(f"| 2 | + threshold population = all bars, not filtered | {n} | {wr*100:.1f}% | **{e:+.4f}** |")

    # Step 3: causal expanding percentile instead of a pooled edge.
    m3 = np.isfinite(er) & np.isfinite(thr) & (er <= thr)
    n, wr, e = exp_R(sf, m3, both_to_stop=False)
    L.append(f"| 3 | + CAUSAL expanding 10th percentile | {n} | {wr*100:.1f}% | **{e:+.4f}** |")

    # Step 4: both-touched bars resolve as full losses.
    n, wr, e = exp_R(sf, m3, both_to_stop=True)
    L.append(f"| 4 | + both-touched resolves to the stop | {n} | {wr*100:.1f}% | **{e:+.4f}** |")

    # Step 5: the frozen spec, sequential, one position at a time, at ZERO cost.
    tr, curve, skipped = phase1.simulate(df, comm=0.0, slip=0.0)
    R = tr["R"].to_numpy()
    L.append(f"| 5 | + one position at a time (frozen spec, zero cost) | {len(tr)} | "
             f"{(R>0).mean()*100:.1f}% | **{R.mean():+.4f}** |")

    # Step 6: the frozen spec with costs, for reference.
    tr2, _, _ = phase1.simulate(df)
    R2 = tr2["R"].to_numpy()
    L.append(f"| 6 | + costs 0.12% round trip (headline Phase 1) | {len(tr2)} | "
             f"{(R2>0).mean()*100:.1f}% | **{R2.mean():+.4f}** |")

    # How different are the two thresholds in practice?
    L.append("\n## Threshold comparison\n")
    L.append(f"- Pooled 10th percentile over the filtered valid set: **{pooled_edge:.4f}**")
    L.append(f"- Pooled 10th percentile over all bars: **{all_edge:.4f}**")
    fin = np.isfinite(thr)
    L.append(f"- Causal expanding threshold: mean **{np.nanmean(thr[fin]):.4f}**, "
             f"range {np.nanmin(thr[fin]):.4f} to {np.nanmax(thr[fin]):.4f}")
    L.append(f"- Signals selected: pooled-filtered {int(m1.sum())}, pooled-all {int(m2.sum())}, "
             f"causal {int(m3.sum())}")

    # Selection effect of the position cap.
    L.append("\n## Position-cap selection effect\n")
    L.append(
        f"Of the qualifying signals, **{len(tr)} were taken and {skipped} were skipped** because a "
        "position was already open. If the taken subset performs materially worse than the full "
        "qualifying set, the cap is not merely discarding signals, it is selecting the bad ones."
    )
    n3, wr3, e3 = exp_R(sf, m3, both_to_stop=True)
    L.append(f"\n- All qualifying signals (step 4): {n3} signals, {e3:+.4f} R")
    L.append(f"- Taken subset under the cap (step 5): {len(tr)} trades, {R.mean():+.4f} R")
    L.append(f"- Difference attributable to the cap: **{R.mean()-e3:+.4f} R**")

    txt = "\n".join(L)
    with open(os.path.join(OUT, "PHASE1_DIAGNOSTIC.md"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
