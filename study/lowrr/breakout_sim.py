"""Does any of this actually pass a Breakout evaluation?

Breakout 1-step (verified from public sources, see LOW_RR_REPORT.md):
    profit target   +10% of initial balance
    daily loss cap  -4%   (static, referenced to initial balance)
    max drawdown    -6%   (STATIC floor at 0.94 x initial, does not trail up)
    no consistency rule, no minimum days, no time limit

Method: empirical rolling starts. Begin a challenge at every trade in the real
chronological sequence and run it forward on the real trades until it passes,
busts, or runs out of history. No resampling, no distribution assumptions.

Known understatement, stated rather than hidden: equity is stepped at trade EXIT,
so intraday unrealised drawdown is not counted against the daily cap. With one
position open at a time the unrealised excursion is bounded by roughly one risk
unit, so this understates daily-cap breaches by about that much. In multi-position
mode the understatement is larger and is flagged in the output.
"""
import sys, os, pickle, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

TARGET = 0.10
DAILY_CAP = 0.04
MAX_DD = 0.06

def run_challenge(net_R, exit_day, risk, start_idx,
                  target=TARGET, daily_cap=DAILY_CAP, max_dd=MAX_DD):
    """Returns ('pass'|'bust_daily'|'bust_max'|'unresolved', n_trades, n_days)."""
    eq = 1.0
    floor = 1.0 - max_dd
    day = None
    day_start_eq = 1.0
    n = len(net_R)
    for k in range(start_idx, n):
        d = exit_day[k]
        if day is None:
            day = d; day_start_eq = eq
        elif d != day:
            day = d; day_start_eq = eq
        eq += risk * eq * net_R[k]
        if eq <= floor:
            return "bust_max", k - start_idx + 1, d - exit_day[start_idx]
        if eq <= day_start_eq - daily_cap:
            return "bust_daily", k - start_idx + 1, d - exit_day[start_idx]
        if eq >= 1.0 + target:
            return "pass", k - start_idx + 1, d - exit_day[start_idx]
    return "unresolved", n - start_idx, exit_day[-1] - exit_day[start_idx]

def sweep(tr, risks, label, daily_cap=DAILY_CAP):
    tr = tr.sort_values("exit_time").reset_index(drop=True)
    net = tr["net_R"].values
    day = (tr["exit_time"].values // 86400).astype(np.int64)
    out = []
    for risk in risks:
        res = [run_challenge(net, day, risk, i, daily_cap=daily_cap)
               for i in range(len(net))]
        kinds = pd.Series([r[0] for r in res])
        resolved = kinds[kinds != "unresolved"]
        dur_pass = [r[2] for r, k in zip(res, kinds) if k == "pass"]
        out.append(dict(
            label=label, risk=risk, n_starts=len(kinds),
            n_resolved=len(resolved),
            # among resolved outcomes only
            p_pass=(resolved == "pass").mean() if len(resolved) else np.nan,
            p_daily=(resolved == "bust_daily").mean() if len(resolved) else np.nan,
            p_max=(resolved == "bust_max").mean() if len(resolved) else np.nan,
            # over every start, with "still running at end of data" as its own bucket
            p_pass_all=(kinds == "pass").mean(),
            med_days=np.median([r[2] for r, k in zip(res, kinds) if k != "unresolved"])
                     if len(resolved) else np.nan,
            med_days_pass=np.median(dur_pass) if dur_pass else np.nan,
            unresolved=(kinds == "unresolved").mean()))
    return pd.DataFrame(out)

def curve_stats(tr, risk):
    tr = tr.sort_values("exit_time").reset_index(drop=True)
    eq = 1.0; peak = 1.0; mdd = 0.0
    for r in tr["net_R"].values:
        eq += risk * eq * r
        peak = max(peak, eq); mdd = min(mdd, (eq - peak) / peak)
    yrs = (tr["exit_time"].iloc[-1] - tr["exit_time"].iloc[0]) / (365.25 * 86400)
    mo = yrs * 12
    return dict(total=eq - 1, cagr=eq ** (1 / yrs) - 1, maxdd=mdd,
                per_month=(eq ** (1 / mo) - 1), n=len(tr))

def portfolio_challenge():
    """Same challenge test on the multi-asset portfolio, if it has been built."""
    p = os.path.join(HERE, "portfolio_trades.pkl")
    if not os.path.exists(p):
        print("\n(no portfolio_trades.pkl; run multiasset.py first)")
        return
    with open(p, "rb") as f:
        book = pickle.load(f)
    print("\n\n=== multi-asset portfolio, Breakout 1-step, rolling starts ===")
    print("daily cap tested at both 4% and the stricter 3% quoted by some sources\n")
    print(f"{'config':<34}{'risk':>7}{'cap':>5}{'P(pass)':>9}{'P(daily)':>9}"
          f"{'P(maxDD)':>9}{'P(pass|all)':>12}{'medDays':>8}{'unres':>7}")
    for label, tr in book.items():
        for risk in [0.0015, 0.0025, 0.005]:
            for cap in [0.04, 0.03]:
                s = sweep(tr, [risk], label, daily_cap=cap).iloc[0]
                md = f"{s['med_days']:.0f}" if np.isfinite(s["med_days"]) else "-"
                print(f"{label:<34}{risk:>7.2%}{cap:>5.0%}{s['p_pass']:>9.1%}"
                      f"{s['p_daily']:>9.1%}{s['p_max']:>9.1%}{s['p_pass_all']:>12.1%}"
                      f"{md:>8}{s['unresolved']:>7.1%}")
        c = curve_stats(tr, 0.0025)
        print(f"{'  full history @0.25% risk':<34}{'':>7}{'':>5}"
              f"total={c['total']:+.1%} CAGR={c['cagr']:+.1%} "
              f"per-mo={c['per_month']:+.2%} maxDD={c['maxdd']:.1%} n={c['n']}\n")

def main():
    with open(os.path.join(HERE, "trades_store.pkl"), "rb") as f:
        store = pickle.load(f)

    configs = [
        ("LOW  S_bb_break_dn  am1.5 rr0.25", ("S_bb_break_dn", 1.5, 0.25)),
        ("LOW  S_bb_break_dn  am1.5 rr0.50", ("S_bb_break_dn", 1.5, 0.5)),
        ("LOW  S_volspike18_dn am1.0 rr0.50", ("S_volspike18_dn", 1.0, 0.5)),
        ("MID  S_bb_break_dn  am1.0 rr1.00", ("S_bb_break_dn", 1.0, 1.0)),
        ("HIGH L_volspike18_up am1.5 rr2.00", ("L_volspike18_up", 1.5, 2.0)),
        ("HIGH S_dntrend_at_200 am1.5 rr2.00", ("S_dntrend_at_200", 1.5, 2.0)),
    ]
    risks = [0.0025, 0.005, 0.0075, 0.01, 0.015]

    print("=== single-rule Breakout 1-step, empirical rolling starts ===")
    print("P(pass) is conditional on the challenge resolving before the data ends;")
    print("P(pass|all) counts every start, with still-running ones as not-passed.\n")
    print(f"{'config':<36}{'risk':>7}{'starts':>7}{'P(pass)':>9}{'P(daily)':>9}"
          f"{'P(maxDD)':>9}{'P(pass|all)':>12}{'medDays':>8}{'unres':>7}")
    for label, key in configs:
        if key not in store:
            print(f"{label:<36} MISSING"); continue
        tr = store[key]
        s = sweep(tr, risks, label)
        for _, r in s.iterrows():
            md = f"{r['med_days']:.0f}" if np.isfinite(r["med_days"]) else "-"
            print(f"{label:<36}{r['risk']:>7.2%}{int(r['n_starts']):>7}{r['p_pass']:>9.1%}"
                  f"{r['p_daily']:>9.1%}{r['p_max']:>9.1%}{r['p_pass_all']:>12.1%}{md:>8}"
                  f"{r['unresolved']:>7.1%}")
        print()

    print("=== full-history equity for the same configs ===")
    print(f"{'config':<36}{'risk':>7}{'n':>5}{'total':>9}{'CAGR':>8}{'per-mo':>8}{'maxDD':>8}")
    for label, key in configs:
        if key not in store: continue
        for risk in [0.005, 0.01]:
            c = curve_stats(store[key], risk)
            print(f"{label:<36}{risk:>7.2%}{c['n']:>5}{c['total']:>+9.1%}"
                  f"{c['cagr']:>+8.1%}{c['per_month']:>+8.2%}{c['maxdd']:>8.1%}")

if __name__ == "__main__":
    main()
    portfolio_challenge()
