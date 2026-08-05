"""Task 4 — maker-entry variant of the SFP star.

Baseline entries are market at next 4H open (taker in + taker out = 0.08% RT).
Here: a LIMIT at the signal bar's close (short: sell limit, fills only if the
next bar trades back UP through it; long mirror). Round-trip fee drops to 0.06%
(0.02% maker entry + 0.04% taker exit). Optional retracement offset places the
limit `off` R beyond the close (better fill price, lower fill rate).

Fill model (conservative):
  - fill window = the next bar only; unfilled signals are skipped;
  - short fills at max(open, limit) (opening above the limit fills at the open);
  - if the fill bar also reaches the STOP, the trade counts as stopped (the fill
    path already moved adversely through the limit toward the stop);
  - the tp1 partial may fill in the fill bar only when the stop was not touched.

Adverse selection is the known cost: the best signals (immediate dump) never
fill. This measures whether fee savings + better entries beat the missed wins.
Exits: fixed 2R/3R and half@1R->BE + 3-ATR trail. 4H star + bull mirror, and the
1h star (does the fee cut revive 1h? breakeven @1:1 drops 53.6% -> ~52.9%).
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from trend_runner import run_fixed
from sfp_divergence import sfp_divergence
from sfp_exits import run_half1R_trail

MAKER_RT = 0.0006

def _sigs(df, L, S):
    atrv = df["atr14"].values
    idx = np.arange(len(df))
    sig = [(i, +1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i] > 0] + \
          [(i, -1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i] > 0]
    sig.sort()
    return sig

def maker_trades(df, L, S, exit_kind="trail", rr=2.0, k=3.0, off=0.0,
                 atr_mult=1.5, max_bars=400):
    """exit_kind: 'fixed' (rr target) or 'trail' (half@1R->BE + k-ATR trail)."""
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    c = df["close"].values; atrv = df["atr14"].values; t = df["time"].values
    n = len(df)
    rows = []; n_sig = 0
    for i, s in _sigs(df, L, S):
        ei = i + 1
        if ei >= n:
            continue
        n_sig += 1
        rdist = atr_mult*atrv[i]
        limit = c[i] - s*off*rdist            # short: off*R ABOVE close (retracement)
        filled = (h[ei] >= limit) if s < 0 else (l[ei] <= limit)
        if not filled:
            continue
        entry = max(o[ei], limit) if s < 0 else min(o[ei], limit)
        sf = rdist/entry
        r_of = lambda p: s*(p-entry)/rdist
        stop = entry - s*rdist
        tp1 = entry + s*rdist
        tgt = entry + s*rr*rdist
        pos = 1.0; realized = 0.0; filled1 = False
        extreme = entry; done = False; ej = ei
        for j in range(ei, min(ei+max_bars, n)):
            ej = j
            stop_hit = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            if j == ei and stop_hit:          # fill bar reached stop: conservative loss
                realized += pos*r_of(stop); pos = 0.0; done = True; break
            if exit_kind == "fixed":
                tgt_hit = (h[j] >= tgt) if s > 0 else (l[j] <= tgt)
                if stop_hit and tgt_hit and abs(o[j]-stop) <= abs(o[j]-tgt):
                    tgt_hit = False
                if stop_hit and not tgt_hit:
                    realized += pos*r_of(stop); pos = 0.0; done = True; break
                if tgt_hit:
                    realized += pos*r_of(tgt); pos = 0.0; done = True; break
            else:
                tp_hit = (not filled1) and ((h[j] >= tp1) if s > 0 else (l[j] <= tp1))
                if stop_hit and (j > ei) and (not tp_hit or abs(o[j]-stop) <= abs(o[j]-tp1)):
                    realized += pos*r_of(stop); pos = 0.0; done = True; break
                if tp_hit:
                    realized += 0.5*pos*r_of(tp1); pos *= 0.5
                    filled1 = True; stop = entry
                ka = atrv[j] if np.isfinite(atrv[j]) else atrv[i]
                if s > 0:
                    extreme = max(extreme, h[j])
                    if filled1: stop = max(stop, extreme - k*ka)
                else:
                    extreme = min(extreme, l[j])
                    if filled1: stop = min(stop, extreme + k*ka)
        if not done:
            realized += pos*r_of(c[ej])
        rows.append(dict(entry_time=t[ei], exit_time=t[ej], side=s,
                         outcome="done" if done else "timeout",
                         net_R=realized - MAKER_RT/sf))
    tr = pd.DataFrame(rows)
    if len(tr):
        tr = tr.sort_values("entry_time").reset_index(drop=True)
    return tr, n_sig

def tt(tag, tr, extra=""):
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    out = []
    for lab, sub in [("TR", tr[tr.entry_time < cut]), ("TE", tr[tr.entry_time >= cut])]:
        if not len(sub):
            out.append(f"{lab}: (none)"); continue
        R = sub["net_R"].values
        out.append(f"{lab}: n={len(sub):3d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f}")
    print(f"  {tag:36} | " + " | ".join(out) + extra)

def run_tf(tf):
    df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
    n = len(df)
    m = sfp_divergence(df)
    dn = (df["close"] < df["ema200"]).values
    star = (m["bear0"] | m["bear1"]) & dn
    bull = (m["bull0"] | m["bull1"]) & ~dn
    Lz = np.zeros(n, bool)
    print(f"\n################ TF={tf} ################")
    print("-- star short: taker baseline (all signals, 0.08% RT) --")
    tt("taker fixed 2R", run_fixed(df, Lz, star, rr=2.0))
    tt("taker half@1R->BE+trail", run_half1R_trail(df, Lz, star, k=3.0))
    for off in [0.0, 0.2]:
        print(f"-- star short: maker limit at close + {off:.1f}R (0.06% RT) --")
        for kind, lab in [("fixed", "maker fixed 2R"), ("trail", "maker half@1R+trail")]:
            tr, n_sig = maker_trades(df, Lz, star, exit_kind=kind, rr=2.0, off=off)
            fill = len(tr)/n_sig if n_sig else 0
            tt(f"{lab} off={off:.1f}", tr, f"   fill={fill:.0%}")
    if tf == "4H":
        print("-- bull mirror: maker limit at close (trail exit) --")
        tt("taker half@1R->BE+trail", run_half1R_trail(df, bull, Lz, k=3.0))
        tr, n_sig = maker_trades(df, bull, Lz, exit_kind="trail", off=0.0)
        tt("maker half@1R+trail off=0.0", tr, f"   fill={len(tr)/n_sig:.0%}")

if __name__ == "__main__":
    for tf in ["4H", "1h"]:
        run_tf(tf)
