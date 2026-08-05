"""Task 2 — resolve the 4H star trades on the TRUE 15m price path.

The 4H sims resolve same-bar stop-vs-target collisions with the nearest-open
heuristic. Here every star trade is replayed on the 15m path:

  - fixed 1R/2R/3R: stop/target touches checked per 15m bar (collision inside a
    single 15m bar resolved nearest-open at 15m granularity — minimal residual bias);
  - half@1R -> breakeven + 3-ATR trail: the tp1/stop/breakeven sequencing plays out
    on 15m bars; the chandelier trail still ratchets only at completed 4H boundaries
    (using the 4H ATR and the extreme of all 15m bars up to that boundary), exactly
    matching the causal semantics of the 4H version.

If the WR/expR survive this, the exit numbers are not an intrabar artifact.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from engine import FEE_RT
from research import breakeven_wr
from sfp_divergence import sfp_divergence
from sfp_walkforward import yearly

H4 = 14400

def star_signals(df4):
    m = sfp_divergence(df4)
    dn = (df4["close"] < df4["ema200"]).values
    star = (m["bear0"] | m["bear1"]) & dn
    bull = (m["bull0"] | m["bull1"]) & ~dn
    return star, bull

def _sigs(df4, L, S):
    atrv = df4["atr14"].values
    idx = np.arange(len(df4))
    sig = [(i, +1) for i in idx if L[i] and np.isfinite(atrv[i]) and atrv[i] > 0] + \
          [(i, -1) for i in idx if S[i] and np.isfinite(atrv[i]) and atrv[i] > 0]
    sig.sort()
    return sig

def fixed_15m(df4, L, S, f, rr, atr_mult=1.5, max_bars4=300):
    ft = f["time"].values; fh = f["high"].values; fl = f["low"].values
    fo = f["open"].values; fc = f["close"].values
    o4 = df4["open"].values; t4 = df4["time"].values; atrv = df4["atr14"].values
    rows = []
    for i, s in _sigs(df4, L, S):
        ei = i+1
        if ei >= len(df4):
            continue
        entry = o4[ei]; rdist = atr_mult*atrv[i]; sf = rdist/entry
        stop = entry - s*rdist; tgt = entry + s*rr*rdist
        t0 = t4[ei]
        j0 = np.searchsorted(ft, t0, side="left")
        j1 = min(np.searchsorted(ft, t0 + max_bars4*H4, side="right"), len(ft))
        outcome = None; j = j0
        for j in range(j0, j1):
            hs = (fl[j] <= stop) if s > 0 else (fh[j] >= stop)
            ht = (fh[j] >= tgt) if s > 0 else (fl[j] <= tgt)
            if hs and ht:
                outcome = "stop" if abs(fo[j]-stop) <= abs(fo[j]-tgt) else "target"; break
            elif hs: outcome = "stop"; break
            elif ht: outcome = "target"; break
        if outcome is None:
            j = j1-1; gross = s*(fc[j]-entry)/rdist; outcome = "timeout"
        else:
            gross = rr if outcome == "target" else -1.0
        rows.append(dict(entry_time=t0, exit_time=ft[j], side=s, outcome=outcome,
                         net_R=gross - FEE_RT/sf))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def trail_15m(df4, L, S, f, k=3.0, atr_mult=1.5, max_bars4=400):
    ft = f["time"].values; fh = f["high"].values; fl = f["low"].values
    fo = f["open"].values; fc = f["close"].values
    o4 = df4["open"].values; t4 = df4["time"].values; atrv = df4["atr14"].values
    t4close = t4 + H4
    rows = []
    for i, s in _sigs(df4, L, S):
        ei = i+1
        if ei >= len(df4):
            continue
        entry = o4[ei]; rdist = atr_mult*atrv[i]; sf = rdist/entry
        r_of = lambda p: s*(p-entry)/rdist
        tp1 = entry + s*rdist; stop = entry - s*rdist
        t0 = t4[ei]
        j0 = np.searchsorted(ft, t0, side="left")
        j1 = min(np.searchsorted(ft, t0 + max_bars4*H4, side="right"), len(ft))
        pos = 1.0; realized = 0.0; filled1 = False
        extreme = entry; done = False; j = j0
        for j in range(j0, j1):
            # ratchet trail at each completed 4H boundary (only after tp1)
            if filled1 and j > j0 and (ft[j]-t0) // H4 > (ft[j-1]-t0) // H4:
                i4 = np.searchsorted(t4close, ft[j], side="right") - 1
                ka = atrv[i4] if (i4 >= 0 and np.isfinite(atrv[i4])) else atrv[i]
                stop = max(stop, extreme - k*ka) if s > 0 else min(stop, extreme + k*ka)
            hs = (fl[j] <= stop) if s > 0 else (fh[j] >= stop)
            ht = (not filled1) and ((fh[j] >= tp1) if s > 0 else (fl[j] <= tp1))
            if hs and (not ht or abs(fo[j]-stop) <= abs(fo[j]-tp1)):
                realized += pos*r_of(stop); pos = 0.0; done = True; break
            if ht:
                realized += 0.5*pos*r_of(tp1); pos *= 0.5
                filled1 = True; stop = entry
                # stop can still be hit later in this same 15m bar's remainder:
                # unknowable ordering -> defer to next bar (consistent, tiny bar)
            extreme = max(extreme, fh[j]) if s > 0 else min(extreme, fl[j])
        if not done:
            realized += pos*r_of(fc[j])
        rows.append(dict(entry_time=t0, exit_time=ft[j], side=s,
                         outcome="done" if done else "timeout",
                         net_R=realized - FEE_RT/sf))
    return pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

def tt(tag, tr):
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    out = []
    for lab, sub in [("TR", tr[tr.entry_time < cut]), ("TE", tr[tr.entry_time >= cut])]:
        R = sub["net_R"].values
        out.append(f"{lab}: n={len(sub):3d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f}")
    print(f"  {tag:34} | " + " | ".join(out))

def main():
    df4 = ind.enrich(pd.read_parquet("data/4H.parquet"))
    f = pd.read_parquet("data/15m.parquet").sort_values("time").reset_index(drop=True)
    star, bull = star_signals(df4)
    Lz = np.zeros(len(df4), bool)
    print("===== 4H star resolved on the true 15m path (vs 4H nearest-open sims) =====")
    for rr in [1.0, 2.0, 3.0]:
        tt(f"star fixed {rr:.0f}R [15m path]", fixed_15m(df4, Lz, star, f, rr))
    tt("star half@1R->BE+trail [15m path]", trail_15m(df4, Lz, star, f, k=3.0))
    tt("bull half@1R->BE+trail [15m path]", trail_15m(df4, bull, Lz, f, k=3.0))
    print()
    yearly("star half@1R->BE+trail [15m path]", trail_15m(df4, Lz, star, f, k=3.0))
    yearly("star fixed 3R [15m path]", fixed_15m(df4, Lz, star, f, 3.0))

if __name__ == "__main__":
    main()
