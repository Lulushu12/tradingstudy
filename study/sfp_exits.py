"""Exit engineering for the SFP-timed divergence entries (see sfp_divergence.py).

The 4H with-trend SFP-divergence short has a real edge at fixed 1:1 / 2:1. Here we ask
whether exits can extract more R per signal:

  1. Higher fixed targets: rr = 2, 3, 4, 5, 6 (run_fixed).
  2. Hybrid reference from the earlier study: half @2R + half 3-ATR chandelier trail.
  3. Partial-TP ladder ("R"): 50% off at +1R and stop -> entry; then 50% of the
     REMAINING position at each further R multiple (+2R, +3R, ...), stop ratcheting
     to the previous milestone after every fill (locking each rung in).
  4. Partial-TP ladder ("level"): same 1R/50%/breakeven first step, but the later
     rungs sit at SIGNIFICANT LEVELS instead of R multiples: the confirmed swing
     pivots (fractal left/right=3) beyond the 1R price that were already known at
     entry time. Stop ratchets the same way.

Causality: pivot levels are taken only from pivots CONFIRMED by the signal bar.
Intrabar resolution: one adverse event per bar with the repo's nearest-open rule --
if both the stop and the next rung are inside one bar, the level closer to that
bar's open fills first; after a rung fills, the freshly ratcheted stop cannot also
fire until the next bar (the intrabar path is unknowable). Multiple rungs may fill
in one big favorable bar. Fees = FEE_RT on full round-trip notional, as everywhere
else in the study. Entry next bar open, initial stop 1.5*ATR(14). Train<2025 / Test.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from engine import FEE_RT
from research import breakeven_wr
from trend_runner import run_fixed
from hybrid_exit import run_hybrid
from sfp_divergence import sfp_divergence, make_30m

MAX_RUNGS = 12          # R-ladder depth cap (12R is beyond any realistic 4H move)
MAX_LEVELS = 8          # level-ladder rung cap
LEVEL_LOOKBACK = 300    # bars of pivot history eligible as significant levels
MAX_BARS = 400

def _pivot_levels(df):
    """(conf_idx, value) arrays for confirmed pivot highs/lows."""
    ph = df["piv_h"].values; pl = df["piv_l"].values
    hi = [(i, ph[i]) for i in range(len(df)) if not np.isnan(ph[i])]
    lo = [(i, pl[i]) for i in range(len(df)) if not np.isnan(pl[i])]
    return hi, lo

def run_ladder(df, L, S, mode="R", atr_mult=1.5, max_bars=MAX_BARS):
    """User's partial-TP scheme. mode="R": rungs at +1R,+2R,...  mode="level":
    rung 1 at +1R, later rungs at confirmed pivot levels beyond it. At every rung:
    sell 50% of remaining, stop -> previous rung (entry after rung 1)."""
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    c = df["close"].values; atrv = df["atr14"].values; t = df["time"].values
    n = len(df)
    piv_hi, piv_lo = _pivot_levels(df) if mode == "level" else ([], [])
    idx = np.arange(n)
    sig = [(i, +1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i] > 0] + \
          [(i, -1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i] > 0]
    sig.sort(); rows = []
    for i, s in sig:
        ei = i + 1
        if ei >= n:
            continue
        entry = o[ei]; rdist = atr_mult*atrv[i]; sf = rdist/entry
        r_of = lambda p: s*(p-entry)/rdist
        # build rung price list (beyond +1R), farthest rung last
        first_tp = entry + s*rdist
        if mode == "R":
            rungs = [entry + s*k*rdist for k in range(1, MAX_RUNGS+1)]
        else:
            piv = piv_hi if s > 0 else piv_lo
            lv = [v for (ci, v) in piv
                  if ci <= i and ci >= i-LEVEL_LOOKBACK and r_of(v) > 1.0]
            lv.sort(key=r_of)                       # nearest beyond 1R first
            dedup = []
            for v in lv:                            # merge rungs closer than 0.3R
                if not dedup or abs(r_of(v)-r_of(dedup[-1])) >= 0.3:
                    dedup.append(v)
            rungs = [first_tp] + dedup[:MAX_LEVELS]
        stop = entry - s*rdist
        prev_rung = entry                            # stop target once rung 1 fills
        pos = 1.0; realized = 0.0; k = 0; ej = ei; done = False; outcome = None
        for j in range(ei, min(ei+max_bars, n)):
            ej = j
            stop_hit = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            rung_hit = k < len(rungs) and ((h[j] >= rungs[k]) if s > 0 else (l[j] <= rungs[k]))
            if stop_hit and rung_hit and abs(o[j]-stop) <= abs(o[j]-rungs[k]):
                realized += pos*r_of(stop); pos = 0.0
                outcome = "stop_run" if k else "stop"; done = True; break
            if not rung_hit and stop_hit:
                realized += pos*r_of(stop); pos = 0.0
                outcome = "stop_run" if k else "stop"; done = True; break
            while k < len(rungs) and ((h[j] >= rungs[k]) if s > 0 else (l[j] <= rungs[k])):
                realized += 0.5*pos*r_of(rungs[k]); pos *= 0.5
                stop = prev_rung; prev_rung = rungs[k]; k += 1
            if k >= len(rungs) and mode == "level" and pos > 0:
                realized += pos*r_of(prev_rung)      # rungs exhausted: assume flat
                pos = 0.0                            # at the last level (conservative)
                outcome = "levels_done"; done = True; break
        if not done:
            realized += pos*r_of(c[ej]); outcome = outcome or "timeout"
        net = realized - FEE_RT/sf
        rows.append(dict(entry_time=t[ei], exit_time=t[ej], side=s, outcome=outcome,
                         rungs_filled=k, R=realized, net_R=net,
                         bars=ej-ei, stop_dist_frac=sf, entry_i=0, exit_i=0))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def run_half1R_trail(df, L, S, k=3.0, atr_mult=1.5, max_bars=MAX_BARS):
    """User-scheme variant: 50% off at +1R and stop -> ENTRY (breakeven); the other
    half rides a k-ATR chandelier trail (never below breakeven) with no target."""
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    c = df["close"].values; atrv = df["atr14"].values; t = df["time"].values
    n = len(df); idx = np.arange(n)
    sig = [(i, +1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i] > 0] + \
          [(i, -1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i] > 0]
    sig.sort(); rows = []
    for i, s in sig:
        ei = i + 1
        if ei >= n:
            continue
        entry = o[ei]; rdist = atr_mult*atrv[i]; sf = rdist/entry
        r_of = lambda p: s*(p-entry)/rdist
        tp1 = entry + s*rdist; stop = entry - s*rdist
        extreme = entry; pos = 1.0; realized = 0.0; filled1 = False
        ej = ei; done = False
        for j in range(ei, min(ei+max_bars, n)):
            ej = j
            stop_hit = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            tp_hit = (not filled1) and ((h[j] >= tp1) if s > 0 else (l[j] <= tp1))
            if stop_hit and (not tp_hit or abs(o[j]-stop) <= abs(o[j]-tp1)):
                realized += pos*r_of(stop); pos = 0.0; done = True; break
            if tp_hit:
                realized += 0.5*pos*r_of(tp1); pos *= 0.5
                filled1 = True; stop = entry           # breakeven
            ka = atrv[j] if np.isfinite(atrv[j]) else atrv[i]
            if s > 0:
                extreme = max(extreme, h[j])
                if filled1: stop = max(stop, extreme - k*ka)
            else:
                extreme = min(extreme, l[j])
                if filled1: stop = min(stop, extreme + k*ka)
        if not done:
            realized += pos*r_of(c[ej])
        net = realized - FEE_RT/sf
        rows.append(dict(entry_time=t[ei], exit_time=t[ej], side=s,
                         outcome="done" if done else "timeout", R=realized, net_R=net,
                         bars=ej-ei, stop_dist_frac=sf, entry_i=0, exit_i=0))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def entry_sets(df):
    m = sfp_divergence(df)
    up = (df["close"] > df["ema200"]).values; dn = ~up
    star = (m["bear0"] | m["bear1"]) & dn
    dedup = star & ~np.roll(star, 1); dedup[0] = star[0]
    return {
        "SFP bear0|1 & dn (star)":  ("S", star),
        "star dedup (1/swing)":     ("S", dedup),
        "SFP bear0|1 (all shorts)": ("S", m["bear0"] | m["bear1"]),
        "SFP bull0|1 & up":         ("L", (m["bull0"] | m["bull1"]) & up),
    }

def report(tag, tr, p_be=None):
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    out = []
    for lab, sub in [("TR", tr[tr.entry_time < cut]), ("TE", tr[tr.entry_time >= cut])]:
        if not len(sub):
            out.append(f"{lab}: (none)"); continue
        R = sub["net_R"].values
        out.append(f"{lab}: n={len(sub):4d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f} "
                   f"med={np.median(R):+.2f} p90={np.percentile(R,90):+.2f} max={R.max():+.1f}")
    a = tr[tr.entry_time < cut]; b = tr[tr.entry_time >= cut]
    ok = len(a) and len(b) and a["net_R"].mean() > 0 and b["net_R"].mean() > 0
    be = f" (beWR {p_be:.0%})" if p_be else ""
    print(f"  {tag:26}{be:12} | " + " | ".join(out) + ("   <<<" if ok else ""))

def run_tf(tf):
    if tf == "30m":
        make_30m()
    df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    n = len(df)
    sfmean = (1.5*df["atr14"]/df["open"].shift(-1)).mean()
    print(f"\n################ TF={tf}  stop~{sfmean:.3%} feeR~{FEE_RT/sfmean:.2f} "
          f"################")
    for name, (side, mask) in entry_sets(df).items():
        L = mask if side == "L" else np.zeros(n, bool)
        S = mask if side == "S" else np.zeros(n, bool)
        print(f"\n===== entries: {name}  (n={int(mask.sum())}) =====")
        for rr in [2.0, 3.0, 4.0, 5.0, 6.0]:
            report(f"fixed {rr:.0f}R", run_fixed(df, L, S, rr=rr, max_bars=MAX_BARS),
                   breakeven_wr(rr, sfmean))
        report("hybrid half@2R+3ATRtrail", run_hybrid(df, L, S, tp=2.0, k=3.0))
        report("half@1R->BE + 3ATRtrail", run_half1R_trail(df, L, S, k=3.0))
        report("ladder R-multiples", run_ladder(df, L, S, mode="R"))
        report("ladder pivot levels", run_ladder(df, L, S, mode="level"))

if __name__ == "__main__":
    import sys
    for tf in (sys.argv[1:] or ["4H"]):
        run_tf(tf)
