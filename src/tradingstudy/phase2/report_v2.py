"""Gate 2 re-run report (Amendment 1 definitions) and ledger rows P2-213..P2-378.
Usage: uv run python -m tradingstudy.phase2.report_v2
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from tradingstudy.config import REPORTS, ROOT
from tradingstudy.phase2.report import criteria, fmt

IN = REPORTS / "phase2" / "baseline_v2_results.json"
OUT = REPORTS / "phase2" / "BASELINE_V2_REPORT.md"
COINS = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE", "SUI", "LINK", "AVAX"]
HYP = {"B1v2": "Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy",
       "B2v2": "Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy",
       "B4": "Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy",
       "B3v2": "HTF layer filter improves divergence stack v2"}


def name(r) -> str:
    lab = f"{r['rtf']}>{r['tf']}" if r["family"] == "B4" else r["tf"]
    h = f" +{r['htf']}" if r.get("htf") else ""
    return f"{r['family']} {lab} {r['variant']}{h}"


def cell(d, k):
    v = d.get(k) or (d.get("-0.0") if k == "0.0" else None)
    return f"{v['exp_R']:+.3f} ({v['n']})" if v else "n/a"


def main() -> None:
    D = json.loads(IN.read_text())
    R = D["results"]
    for r in R:
        r["crit"] = criteria(r)
        r["name"] = name(r)
    ref = [r for r in R if r["target"] == "2R"]
    md = ["# Gate 2 re-run: baselines with the corrected definitions (PROTOCOL Amendment 1)", "",
          f"Walk-forward test period 2023-01-01 to 2025-11-14, 9 coins, structure stops, fees, slippage, limit fills and "
          f"portfolio guards on. {len(R)} configurations (P2-213 to P2-378). Deflated Sharpe uses N = {D['n_trials_total']} "
          "(all Phase 2 configurations so far). Gross R = before fees (slippage included).", "",
          "## 1. Headline: 2R target", "",
          "| Config | Signals | Skipped (stop < 0.5 ATR) | Trades | Per day | Win | Gross R | Net exp R | PF | Fee R | Folds + | Coins + | DSR | P(breach 90d) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in ref:
        w = r["wf"]; f = r.get("folds", {})
        fp = sum(1 for v in f.values() if v is not None and np.isfinite(v) and v > 0)
        md.append(f"| {r['name']} | {r['signals']} | {r['signals_skipped_stop']} | {w.get('n', 0)} | {w.get('trades_per_day', np.nan):.2f} | "
                  f"{fmt(w.get('win_rate'), pct=True)} | {fmt(w.get('gross_R'))} | {fmt(w.get('exp_R'))} | {w.get('pf', np.nan):.2f} | "
                  f"{w.get('fee_R', np.nan):.3f} | {fp}/6 | {r.get('coins_positive', 0)}/9 | {r.get('dsr', np.nan):.2f} | "
                  f"{fmt(r.get('mc', {}).get('p_any_breach_90d'), pct=True)} |")
    T = pd.DataFrame([{"name": r["name"], "family": r["family"], "target": r["target"], "n": r["wf"].get("n", 0),
                       "exp": r["wf"].get("exp_R", np.nan), "gross": r["wf"].get("gross_R", np.nan), "id": r["id"]} for r in R])
    md += ["", "## 2. All targets: spread of net expectancy", "",
           "| Config | Targets | Positive | Min | Median | Max (target, trades) |", "|---|---|---|---|---|---|"]
    for nm, g in T[T.family != "B3v2"].groupby("name", sort=False):
        b = g.loc[g.exp.idxmax()]
        md.append(f"| {nm} | {len(g)} | {(g.exp > 0).sum()} | {fmt(g.exp.min())} | {fmt(g.exp.median())} | {fmt(b.exp)} ({b.target}, {b.n}) |")
    md += ["", "## 3. Trend regime breakdown (2R target; expectancy R (trades))", "",
           "| Config | R1 with | R1 against | R1 mixed | R2 trend with | R2 trend against | R2 no trend |", "|---|---|---|---|---|---|---|"]
    for r in ref:
        a, b = r["regime_r1"], r["regime_r2"]
        md.append(f"| {r['name']} | {cell(a, '1.0')} | {cell(a, '-1.0')} | {cell(a, '0.0')} | {cell(b, '1.0')} | {cell(b, '-1.0')} | {cell(b, '0.0')} |")
    md += ["", "## 4. By coin (2R target, expectancy R)", "", "| Config | " + " | ".join(COINS) + " |", "|---|" + "---|" * len(COINS)]
    for r in ref:
        if r["family"] == "B3v2":
            continue
        c = r["coins"]
        md.append(f"| {r['name']} | " + " | ".join(f"{c[k]['exp_R']:+.2f} ({c[k]['n']})" if k in c else "n/a" for k in COINS) + " |")
    md += ["", "## 5. By session and fold (2R target)", "", "| Config | asia | europe | us | late | " + " | ".join(ref[0]["folds"]) + " |",
           "|---|---|---|---|---|" + "---|" * 6]
    for r in ref:
        if r["family"] == "B3v2":
            continue
        s = r["session"]
        md.append(f"| {r['name']} | " + " | ".join(cell(s, k) for k in ("asia", "europe", "us", "late")) + " | "
                  + " | ".join(fmt(v) for v in r["folds"].values()) + " |")
    crit = pd.DataFrame([r["crit"] for r in R])
    md += ["", "## 6. Protocol criteria", "",
           "Configurations meeting each: " + ", ".join(f"{k} {int(crit[k].sum())}/{len(crit)}" for k in crit.columns),
           f"\nMeeting all of S1-S5, S7-S9: {int(crit.all(axis=1).sum())}."]
    best = max(R, key=lambda r: r["wf"].get("exp_R", -9))
    md.append(f"\nHighest net expectancy of the {len(R)}: {best['id']} {best['name']} target {best['target']} at "
              f"{fmt(best['wf'].get('exp_R'))} R over {best['wf'].get('n')} trades, DSR {best.get('dsr', np.nan):.2f}.")
    OUT.write_text("\n".join(md) + "\n")
    lines = ["", "## Phase 2 re-run with Amendment 1 definitions (counts: yes, 166 configurations)",
             f"- Date: 2026-11-16. Split: walk-forward test period 2023-01-01..2025-11-14, fixed rules, 9 coins, structure stops."
             f" DSR with N = {D['n_trials_total']}.", "",
             "| id | hypothesis | configuration | n | exp R | gross R | PF | fee R | folds+ | coins+ | DSR | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        w = r["wf"]; f = r.get("folds", {})
        fp = sum(1 for v in f.values() if v is not None and np.isfinite(v) and v > 0)
        fails = [k for k, v in r["crit"].items() if not v]
        lines.append(f"| {r['id']} | {HYP[r['family']]} | {r['name']} target {r['target']} | {w.get('n', 0)} | {fmt(w.get('exp_R'))} | "
                     f"{fmt(w.get('gross_R'))} | {w.get('pf', np.nan):.2f} | {w.get('fee_R', np.nan):.3f} | {fp}/6 | "
                     f"{r.get('coins_positive', 0)}/9 | {r.get('dsr', np.nan):.2f} | "
                     f"{'meets S1-S5,S7-S9' if not fails else 'fails ' + ','.join(fails)} |")
    led = ROOT / "LEDGER.md"
    s = led.read_text()
    if "## Phase 2 re-run with Amendment 1" not in s:
        led.write_text(s + "\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
