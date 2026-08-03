"""Does running several systems side by side beat running the best one?

The intuition is right in principle: combining imperfectly correlated positive
edges raises return per unit of risk even when it raises neither edge. The
question is entirely about how correlated these particular systems are, and
whether the benefit survives the constraint that actually binds at Breakout.

THE TRAP THIS FILE IS BUILT TO AVOID. "Take the trades individually on each
system and see where they go" silently raises total exposure. Five systems each
risking 1% is 5% at risk the moment they all fire together, and they WILL fire
together, because they are all short-side rules on twelve correlated perps that
trigger in the same selloffs. Under a STATIC -6% floor that is not a higher
return, it is a different bet with a much larger stake. So every configuration
here is compared at FIXED PEAK RISK: risk per trade = total_risk / max_concurrent.
A combination only wins if it wins after that normalisation.

What is measured:
  1. pairwise correlation of daily net R between systems
  2. how often two systems fire on the same symbol at overlapping times, which is
     one opportunity being counted twice rather than two opportunities
  3. whether the concurrency cap binds, because if it does, adding systems only
     changes WHICH trades fill the slots and cannot add return
  4. every combination vs every single system at fixed peak risk, on return per
     unit of max drawdown and on Breakout 1-step pass rate
"""
import sys, os, pickle, itertools, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from lowrr import core
from lowrr.pooled_test import day_cluster_ci
from lowrr.breakout_sim import sweep

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL_RISK = 0.01          # peak fraction of equity at risk, held constant
CUT = pd.Timestamp("2025-01-01", tz="UTC")

# (label, rule, rr). Only rules already tested across 12 perps are eligible.
SYSTEMS = [
    ("bb0.5",  "S_bb_break_dn",   0.5),
    ("bb1.0",  "S_bb_break_dn",   1.0),
    ("bb2.0",  "S_bb_break_dn",   2.0),
    ("vs0.5",  "S_volspike18_dn", 0.5),
    ("vs1.0",  "S_volspike18_dn", 1.0),
    ("vs2.0",  "S_volspike18_dn", 2.0),
    ("Lvs2.0", "L_volspike18_up", 2.0),
]

def load():
    with open(os.path.join(HERE, "multiasset_store.pkl"), "rb") as f:
        store = pickle.load(f)
    out = {}
    for label, rule, rr in SYSTEMS:
        frames = [d[(rule, rr)] for d in store.values() if (rule, rr) in d]
        if not frames:
            continue
        tr = pd.concat(frames, ignore_index=True).sort_values("entry_time")
        tr = tr.reset_index(drop=True)
        tr["system"] = label
        out[label] = tr
    return out

def daily_series(tr):
    s = tr.groupby(tr["exit_time"] // 86400)["net_R"].sum()
    return s

def correlations(sys_tr):
    labs = list(sys_tr)
    d = pd.DataFrame({k: daily_series(v) for k, v in sys_tr.items()}).fillna(0.0)
    print("\n=== pairwise correlation of daily net R ===")
    print("(all short-side rules on 12 correlated perps, so expect this to be high)")
    print(d.corr().round(2).to_string())
    return d.corr()

def overlap_matrix(sys_tr):
    print("\n=== signal overlap: share of A's trades that sit inside a B trade "
          "on the SAME symbol ===")
    labs = list(sys_tr)
    M = pd.DataFrame(index=labs, columns=labs, dtype=float)
    for a in labs:
        ta = sys_tr[a]
        for b in labs:
            if a == b:
                M.loc[a, b] = 1.0
                continue
            tb = sys_tr[b]
            hit = 0
            for sym, ga in ta.groupby("sym"):
                gb = tb[tb["sym"] == sym]
                if len(gb) == 0:
                    continue
                en = ga["entry_time"].values
                s = gb["entry_time"].values; e = gb["exit_time"].values
                order = np.argsort(s); s, e = s[order], e[order]
                pos = np.searchsorted(s, en, side="right") - 1
                ok = (pos >= 0) & (e[np.clip(pos, 0, len(e) - 1)] > en)
                hit += int(ok.sum())
            M.loc[a, b] = hit / len(ta)
    print(M.round(2).to_string())
    return M

def portfolio(sys_tr, labels, max_conc=4, total_risk=TOTAL_RISK,
              one_per_symbol=True):
    """Fixed PEAK risk: each trade risks total_risk/max_conc."""
    risk = total_risk / max_conc
    tr = pd.concat([sys_tr[l] for l in labels], ignore_index=True)
    tr = tr.sort_values("entry_time").reset_index(drop=True)
    open_pos = []
    taken = []
    skipped_cap = 0
    skipped_sym = 0
    for r in tr.itertuples():
        open_pos = [p for p in open_pos if p[0] > r.entry_time]
        if len(open_pos) >= max_conc:
            skipped_cap += 1
            continue
        if one_per_symbol and any(p[1] == r.sym for p in open_pos):
            skipped_sym += 1
            continue
        open_pos.append((r.exit_time, r.sym))
        taken.append(r)
    u = pd.DataFrame(taken).sort_values("exit_time").reset_index(drop=True)
    eq = 1.0; peak = 1.0; mdd = 0.0
    for x in u["net_R"].values:
        eq += risk * eq * x
        peak = max(peak, eq); mdd = min(mdd, (eq - peak) / peak)
    yrs = (u["exit_time"].iloc[-1] - u["exit_time"].iloc[0]) / (365.25 * 86400)
    daily = u.groupby(u["exit_time"] // 86400)["net_R"].sum() * risk
    streak = mx = 0
    for w in (u["net_R"] > 0).values:
        if w: streak = 0
        else: streak += 1; mx = max(mx, streak)
    return dict(
        n=len(u), tpm=len(u) / (yrs * 12), expR=u["net_R"].mean(),
        Rmo=u["net_R"].sum() / (yrs * 12), risk=risk,
        cagr=eq ** (1 / yrs) - 1, maxdd=mdd,
        cdd=(eq ** (1 / yrs) - 1) / abs(mdd) if mdd else np.nan,
        worst_day=daily.min(), streak=mx,
        cap_block=skipped_cap / len(tr), sym_block=skipped_sym / len(tr),
        offered=len(tr)), u

def main():
    sys_tr = load()
    print(f"systems loaded: {list(sys_tr)}")
    print(f"\n=== each system alone, pooled over 12 perps ===")
    print(f"{'system':<8}{'n':>7}{'expR':>8}{'day CI':>18}{'R/mo(uncapped)':>16}")
    for k, v in sys_tr.items():
        lo, hi, p = day_cluster_ci(v, block_days=5)
        yrs = (v["exit_time"].iloc[-1] - v["exit_time"].iloc[0]) / (365.25 * 86400)
        print(f"{k:<8}{len(v):>7}{v['net_R'].mean():>+8.3f}"
              f"{f'{lo:+.3f} {hi:+.3f}':>18}{v['net_R'].sum()/(yrs*12):>+16.2f}")

    correlations(sys_tr)
    overlap_matrix(sys_tr)

    print(f"\n\n=== single systems vs combinations, FIXED PEAK RISK = "
          f"{TOTAL_RISK:.0%} of equity ===")
    print("cap = max concurrent positions; risk/trade = total_risk/cap")
    print(f"{'portfolio':<26}{'cap':>4}{'r/trd':>7}{'n':>6}{'t/mo':>6}{'expR':>8}"
          f"{'R/mo':>7}{'CAGR':>7}{'maxDD':>8}{'CAGR/DD':>8}{'wDay':>7}"
          f"{'strk':>5}{'capBlk':>8}")
    combos = []
    for l in sys_tr:
        combos.append((l,))
    combos += [("bb0.5", "vs0.5"), ("bb1.0", "vs1.0"), ("bb2.0", "vs2.0"),
               ("vs0.5", "vs1.0", "vs2.0"),
               ("bb0.5", "bb1.0", "bb2.0"),
               ("bb0.5", "vs0.5", "bb1.0", "vs1.0"),
               ("bb1.0", "vs1.0", "Lvs2.0"),
               ("bb0.5", "vs0.5", "bb1.0", "vs1.0", "bb2.0", "vs2.0"),
               tuple(sys_tr)]
    rows = []
    for labels in combos:
        labels = tuple(l for l in labels if l in sys_tr)
        if not labels:
            continue
        for cap in (2, 4, 8):
            m, u = portfolio(sys_tr, labels, max_conc=cap)
            name = "+".join(labels) if len(labels) <= 3 else f"ALL{len(labels)}"
            rows.append(dict(name=name, labels=labels, cap=cap, **m))
            print(f"{name:<26}{cap:>4}{m['risk']:>7.3%}{m['n']:>6}{m['tpm']:>6.1f}"
                  f"{m['expR']:>+8.3f}{m['Rmo']:>+7.2f}{m['cagr']:>+7.1%}"
                  f"{m['maxdd']:>8.1%}{m['cdd']:>8.2f}{m['worst_day']:>+7.2%}"
                  f"{m['streak']:>5}{m['cap_block']:>8.1%}")
    res = pd.DataFrame(rows)
    res.drop(columns=["labels"]).to_csv(os.path.join(HERE, "multisystem_results.csv"),
                                        index=False)

    print("\n\n=== Breakout 1-step pass rates, best few by CAGR/maxDD ===")
    print("target +10%, daily cap 4%, static -6% floor, rolling starts")
    print(f"{'portfolio':<26}{'cap':>4}{'P(pass)':>9}{'P(daily)':>9}{'P(maxDD)':>9}"
          f"{'medDays':>9}{'unres':>7}")
    best = res.sort_values("cdd", ascending=False).head(6)
    for _, r in best.iterrows():
        _, u = portfolio(sys_tr, r["labels"], max_conc=int(r["cap"]))
        s = sweep(u, [r["risk"]], r["name"]).iloc[0]
        md = f"{s['med_days']:.0f}" if np.isfinite(s["med_days"]) else "-"
        print(f"{r['name']:<26}{int(r['cap']):>4}{s['p_pass']:>9.1%}"
              f"{s['p_daily']:>9.1%}{s['p_max']:>9.1%}{md:>9}{s['unresolved']:>7.1%}")

if __name__ == "__main__":
    main()
