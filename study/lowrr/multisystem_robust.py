"""Is the multi-system gain real, or an artifact of arbitrary tie-breaking?

The concurrency cap turns away 40 to 91 percent of offered signals, so the
portfolio is really a QUEUE and the result depends on who gets served. Worse,
several "systems" here share an entry and differ only in target, so their trades
carry the SAME entry timestamp on the SAME symbol. With a one-position-per-symbol
rule, which of them gets in is decided by nothing more principled than sort order.

If shuffling that order moves the answer around, the headline number was a
coin flip dressed as a portfolio effect. This runs each configuration under many
random tie-break orderings and reports the spread.

Also runs the honest control: allow the laddered targets to coexist on one symbol
(one position per symbol PER SYSTEM rather than per symbol), which is what target
laddering actually means, versus the arbitrary pick-one behaviour.
"""
import sys, os, pickle, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from lowrr.multisystem import load, TOTAL_RISK

HERE = os.path.dirname(os.path.abspath(__file__))

def portfolio_seeded(sys_tr, labels, max_conc, seed, per_system_symbol=False,
                     total_risk=TOTAL_RISK):
    risk = total_risk / max_conc
    tr = pd.concat([sys_tr[l] for l in labels], ignore_index=True)
    rng = np.random.default_rng(seed)
    tr = tr.assign(_j=rng.random(len(tr))).sort_values(["entry_time", "_j"])
    tr = tr.reset_index(drop=True)
    open_pos = []
    taken = []
    for r in tr.itertuples():
        open_pos = [p for p in open_pos if p[0] > r.entry_time]
        if len(open_pos) >= max_conc:
            continue
        if per_system_symbol:
            if any(p[1] == r.sym and p[2] == r.system for p in open_pos):
                continue
        else:
            if any(p[1] == r.sym for p in open_pos):
                continue
        open_pos.append((r.exit_time, r.sym, r.system))
        taken.append(r)
    u = pd.DataFrame(taken).sort_values("exit_time").reset_index(drop=True)
    eq = 1.0; peak = 1.0; mdd = 0.0
    for x in u["net_R"].values:
        eq += risk * eq * x
        peak = max(peak, eq); mdd = min(mdd, (eq - peak) / peak)
    yrs = (u["exit_time"].iloc[-1] - u["exit_time"].iloc[0]) / (365.25 * 86400)
    daily = u.groupby(u["exit_time"] // 86400)["net_R"].sum() * risk
    cagr = eq ** (1 / yrs) - 1
    return dict(n=len(u), expR=u["net_R"].mean(), cagr=cagr, maxdd=mdd,
                cdd=cagr / abs(mdd) if mdd else np.nan, worst_day=daily.min(),
                tpm=len(u) / (yrs * 12))

CONFIGS = [
    ("bb0.5", ("bb0.5",), 2), ("bb0.5", ("bb0.5",), 8),
    ("vs1.0", ("vs1.0",), 8), ("vs2.0", ("vs2.0",), 2),
    ("bbLadder", ("bb0.5", "bb1.0", "bb2.0"), 2),
    ("bbLadder", ("bb0.5", "bb1.0", "bb2.0"), 8),
    ("ALL4", ("bb0.5", "vs0.5", "bb1.0", "vs1.0"), 8),
    ("ALL6", ("bb0.5", "vs0.5", "bb1.0", "vs1.0", "bb2.0", "vs2.0"), 2),
    ("ALL6", ("bb0.5", "vs0.5", "bb1.0", "vs1.0", "bb2.0", "vs2.0"), 8),
    ("ALL7", ("bb0.5", "vs0.5", "bb1.0", "vs1.0", "bb2.0", "vs2.0", "Lvs2.0"), 8),
]
NSEED = 25

def main():
    sys_tr = load()
    for per_sys in (False, True):
        mode = ("one position per symbol PER SYSTEM (true target laddering)"
                if per_sys else "one position per symbol (arbitrary pick-one)")
        print(f"\n{'='*96}\n{mode}\n{'='*96}")
        print(f"{'config':<12}{'cap':>4}{'n(med)':>8}{'CAGR/DD mean':>14}{'sd':>7}"
              f"{'min':>7}{'max':>7}{'maxDD mean':>12}{'wDay mean':>11}{'t/mo':>7}")
        for name, labels, cap in CONFIGS:
            labels = tuple(l for l in labels if l in sys_tr)
            res = [portfolio_seeded(sys_tr, labels, cap, s, per_sys)
                   for s in range(NSEED)]
            cdd = np.array([r["cdd"] for r in res])
            dd = np.array([r["maxdd"] for r in res])
            wd = np.array([r["worst_day"] for r in res])
            n = np.array([r["n"] for r in res])
            tpm = np.array([r["tpm"] for r in res])
            print(f"{name:<12}{cap:>4}{np.median(n):>8.0f}{cdd.mean():>14.2f}"
                  f"{cdd.std():>7.2f}{cdd.min():>7.2f}{cdd.max():>7.2f}"
                  f"{dd.mean():>12.1%}{wd.mean():>11.2%}{tpm.mean():>7.1f}", flush=True)

if __name__ == "__main__":
    main()
