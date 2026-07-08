"""Gate 0 steps 5-6: raw signal census per variant per year, and stack
shared-leg statistics for the dedup rule proposal.

NO P&L is computed anywhere in this file. Counts only.

Spec parameters (FROZEN_SPEC.md overrides PineScript defaults):
  stack window   11 (spec 4; Pine default 30 is NOT used)
  preDivMaxAge   50 (spec 4, trader's live setting; Pine default 100 NOT used)
  preDivSwingBuf  5
  pre-div current-turn filters 0.0 (Pine defaults; spec says the current turn
  carries no PIVOT-LEVEL filter; the coded 0.0 zero-line filter is part of
  "the coded logic" the spec defers to -- flagged as an open interpretation
  question in the Gate 0 report)

Variant A (standard): WT regular div (primary -65/45 or secondary -40/15
chain) + MFI regular div (-2.5/2.5), same direction, gap between fractal
CONFIRMATION bars <= 11 (gap 0 valid). Signal bar = the later confirmation.

Variant B (front-run, PRIMARY): leg 1 = either oscillator's confirmed div;
leg 2 = the other oscillator's pre-div raw condition AND a one-bar tick in
the reversal direction at bar t, with leg 1 confirmed by t and
t - leg1_pivot <= 11. Signal bar = t. A (leg1 event, leg2 anchor) pair fires
once: the first bar it completes consumes it.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcb_port import wavetrend, mfi_clone, find_divs, prediv_raw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WINDOW = 11
PRE_DIV_MAX_AGE = 50
SWING_BUF = 5


def load():
    df = pd.read_parquet(os.path.join(ROOT, "audit", "studied_15m.parquet"))
    return df[["time", "dt", "open", "high", "low", "close", "Volume"]].copy()


def build_events(df):
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    o = df["open"].to_numpy(float)
    wt1, wt2 = wavetrend(h, l, c)
    mfi = mfi_clone(o, c)

    wt_prim = find_divs(wt2, h, l, 45.0, -65.0)
    wt_sec = find_divs(wt2, h, l, 15.0, -40.0)
    mfi_div = find_divs(mfi, h, l, 2.5, -2.5)

    pre_wt = prediv_raw(wt2, h, l, wt_prim.is_top, wt_prim.is_bot,
                        PRE_DIV_MAX_AGE, SWING_BUF, 0.0, 0.0)
    pre_mfi = prediv_raw(mfi, h, l, mfi_div.is_top, mfi_div.is_bot,
                         PRE_DIV_MAX_AGE, SWING_BUF, 0.0, 0.0)

    tick_up = {"wt": np.concatenate(([False], wt2[1:] > wt2[:-1])),
               "mfi": np.concatenate(([False], mfi[1:] > mfi[:-1]))}
    tick_dn = {"wt": np.concatenate(([False], wt2[1:] < wt2[:-1])),
               "mfi": np.concatenate(([False], mfi[1:] < mfi[:-1]))}
    return dict(wt2=wt2, mfi=mfi, wt_prim=wt_prim, wt_sec=wt_sec,
                mfi_div=mfi_div, pre_wt=pre_wt, pre_mfi=pre_mfi,
                tick_up=tick_up, tick_dn=tick_dn)


def div_event_bars(ev):
    """Confirmation-bar indices per oscillator and direction."""
    wt_bull = np.where(ev["wt_prim"].bull_div | ev["wt_sec"].bull_div)[0]
    wt_bear = np.where(ev["wt_prim"].bear_div | ev["wt_sec"].bear_div)[0]
    mfi_bull = np.where(ev["mfi_div"].bull_div)[0]
    mfi_bear = np.where(ev["mfi_div"].bear_div)[0]
    return wt_bull, wt_bear, mfi_bull, mfi_bear


def variant_a_signals(ev):
    """(signal_bar, wt_conf_bar, mfi_conf_bar, direction) tuples.

    Enumerated as leg PAIRS: every (WT div, MFI div) same-direction pair with
    confirmation gap <= WINDOW yields one signal at the later confirmation
    bar. This is what the Pine bull/bearStack fires (it re-fires on each new
    leg while the other leg is recent), and it is exactly the shared-leg
    population the dedup rule must resolve.
    """
    wt_bull, wt_bear, mfi_bull, mfi_bear = div_event_bars(ev)
    out = []
    for direction, wts, mfis in (("bull", wt_bull, mfi_bull),
                                 ("bear", wt_bear, mfi_bear)):
        for wb in wts:
            close_mfis = mfis[np.abs(mfis - wb) <= WINDOW]
            for mb in close_mfis:
                out.append((max(wb, mb), wb, mb, direction))
    return sorted(out)


def variant_b_signals(ev, n):
    """(signal_bar, leg1_osc, leg1_conf_bar, leg2_anchor_bar, direction).

    First completion per (leg1 event, leg2 anchor) pair consumes the pair.
    """
    wt_bull, wt_bear, mfi_bull, mfi_bear = div_event_bars(ev)
    legs = {("wt", "bull"): wt_bull, ("wt", "bear"): wt_bear,
            ("mfi", "bull"): mfi_bull, ("mfi", "bear"): mfi_bear}
    out = []
    consumed = set()
    for (leg1_osc, direction), conf_bars in legs.items():
        leg2_osc = "mfi" if leg1_osc == "wt" else "wt"
        pre = ev["pre_mfi"] if leg2_osc == "mfi" else ev["pre_wt"]
        raw = pre.pre_bull if direction == "bull" else pre.pre_bear
        anchor = pre.bull_ref_bar if direction == "bull" else pre.bear_ref_bar
        tick = (ev["tick_up"] if direction == "bull" else ev["tick_dn"])[leg2_osc]
        for u in conf_bars:            # leg1 confirmation bar
            p = u - 2                  # leg1 pivot bar
            for t in range(u, min(p + WINDOW, n - 1) + 1):
                if raw[t] and tick[t]:
                    key = (leg1_osc, direction, u, int(anchor[t]))
                    if key in consumed:
                        continue
                    consumed.add(key)
                    out.append((t, leg1_osc, u, int(anchor[t]), direction))
                    break              # first completion consumes this leg1
    return sorted(out)


def per_year(df, bars):
    years = df["dt"].dt.year.to_numpy()
    return pd.Series(years[bars]).value_counts().sort_index()


def main():
    df = load()
    n = len(df)
    ev = build_events(df)
    wt_bull, wt_bear, mfi_bull, mfi_bear = div_event_bars(ev)

    print("=== RAW DIVERGENCE EVENTS (confirmation bars, studied data) ===")
    tab = pd.DataFrame({
        "WT bull": per_year(df, wt_bull), "WT bear": per_year(df, wt_bear),
        "MFI bull": per_year(df, mfi_bull), "MFI bear": per_year(df, mfi_bear),
    }).fillna(0).astype(int)
    tab.loc["total"] = tab.sum()
    print(tab.to_string())
    print("\nNote: 2021 and 2026 are partial years in the studied span; "
          "2025 is missing Mar-Jun (no export).")

    print("\n=== VARIANT A: leg pairs within window ===")
    a = variant_a_signals(ev)
    a_bars = np.array([s[0] for s in a], dtype=int)
    a_dir = np.array([s[3] for s in a])
    ya = pd.DataFrame({
        "A bull pairs": per_year(df, a_bars[a_dir == "bull"]),
        "A bear pairs": per_year(df, a_bars[a_dir == "bear"]),
    }).fillna(0).astype(int)
    ya.loc["total"] = ya.sum()
    print(ya.to_string())

    # shared-leg statistics for the dedup rule
    wt_leg_counts = pd.Series([s[1] for s in a]).value_counts()
    mfi_leg_counts = pd.Series([s[2] for s in a]).value_counts()
    multi_wt = int((wt_leg_counts > 1).sum())
    multi_mfi = int((mfi_leg_counts > 1).sum())
    print(f"\npairs total: {len(a)}")
    print(f"WT legs used by >1 pair:  {multi_wt} of {len(wt_leg_counts)} "
          f"({multi_wt / max(len(wt_leg_counts), 1):.1%}), max reuse {wt_leg_counts.max() if len(a) else 0}")
    print(f"MFI legs used by >1 pair: {multi_mfi} of {len(mfi_leg_counts)} "
          f"({multi_mfi / max(len(mfi_leg_counts), 1):.1%}), max reuse {mfi_leg_counts.max() if len(a) else 0}")
    # dedup candidate: first pair per signal bar, then cooldown alternatives
    sig_bars_dedup = sorted(set(a_bars.tolist()))
    print(f"unique signal BARS (>=1 pair completing): {len(sig_bars_dedup)}")
    # count clusters: signal bars within WINDOW of the previous signal bar
    sb = np.array(sig_bars_dedup)
    same_dir = {}
    for d in ("bull", "bear"):
        bars_d = np.array(sorted(set(a_bars[a_dir == d].tolist())))
        if len(bars_d):
            fresh = np.concatenate(([True], np.diff(bars_d) > WINDOW))
            same_dir[d] = (len(bars_d), int(fresh.sum()))
    for d, (nb, nf) in same_dir.items():
        print(f"  {d}: {nb} signal bars -> {nf} after '>11-bar gap starts new "
              f"cluster' collapse")

    print("\n=== VARIANT B: front-run signals (first completion per leg pair) ===")
    b = variant_b_signals(ev, n)
    b_bars = np.array([s[0] for s in b], dtype=int)
    b_dir = np.array([s[4] for s in b])
    b_leg1 = np.array([s[1] for s in b])
    yb = pd.DataFrame({
        "B bull": per_year(df, b_bars[b_dir == "bull"]),
        "B bear": per_year(df, b_bars[b_dir == "bear"]),
    }).fillna(0).astype(int)
    yb.loc["total"] = yb.sum()
    print(yb.to_string())
    print(f"\nB signals total: {len(b)}  "
          f"(leg1=WT: {(b_leg1 == 'wt').sum()}, leg1=MFI: {(b_leg1 == 'mfi').sum()})")
    ub = sorted(set(b_bars.tolist()))
    print(f"unique B signal bars: {len(ub)}")
    for d in ("bull", "bear"):
        bars_d = np.array(sorted(set(b_bars[b_dir == d].tolist())))
        if len(bars_d):
            fresh = np.concatenate(([True], np.diff(bars_d) > WINDOW))
            print(f"  {d}: {len(bars_d)} signal bars -> {int(fresh.sum())} after "
                  f"cluster collapse")

    # save event logs for the Gate 0 record (bar indices + timestamps only)
    pd.DataFrame(a, columns=["signal_bar", "wt_conf_bar", "mfi_conf_bar",
                             "direction"]) \
        .assign(dt=lambda x: df["dt"].iloc[x["signal_bar"]].values) \
        .to_csv(os.path.join(ROOT, "audit", "census_variant_a.csv"), index=False)
    pd.DataFrame(b, columns=["signal_bar", "leg1_osc", "leg1_conf_bar",
                             "leg2_anchor_bar", "direction"]) \
        .assign(dt=lambda x: df["dt"].iloc[x["signal_bar"]].values) \
        .to_csv(os.path.join(ROOT, "audit", "census_variant_b.csv"), index=False)
    print("\nevent logs saved to audit/census_variant_a.csv, census_variant_b.csv")


if __name__ == "__main__":
    main()
