"""H-MV report and ledger rows. Usage: uv run python -m tradingstudy.phase3.hmv_report"""
from __future__ import annotations

import json

import numpy as np

from tradingstudy.config import REPORTS, ROOT
from tradingstudy.phase2.report import criteria, fmt

IN = REPORTS / "phase3" / "hmv_results.json"
OUT = REPORTS / "phase3" / "HMV_REPORT.md"


def main() -> None:
    D = json.loads(IN.read_text())
    R = D["results"]
    base = {}  # ungated stack v2 / same entry at 2R from the v2 baselines, for comparison
    for r in json.loads((REPORTS / "phase2" / "baseline_v2_results.json").read_text())["results"]:
        if r["family"] == "B1v2" and r["target"] == "2R":
            base[(r["tf"], "stack" + r["variant"])] = r["wf"].get("exp_R")
    md = ["# Hypothesis H-MV: MCB entries gated by the user's Macro View (10 x TF)", "",
          "Declared in PROTOCOL Amendment 2 before running. Walk-forward test period 2023-01-01 to 2025-11-14, 9 coins, "
          f"structure stop, 2R, fees, slippage, limit fills, portfolio guards. Deflated Sharpe N = {D['n_trials_total']}.", "",
          "| id | TF | Entry | Bias | Trades | Per day | Win | Gross R | Net exp R | Ungated net R | PF | Folds + | Coins + | DSR |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        w = r["wf"]
        fp = sum(1 for v in r["folds"].values() if v is not None and np.isfinite(v) and v > 0)
        ug = base.get((r["tf"], r["entry"]))
        md.append(f"| {r['id']} | {r['tf']} | {r['entry']} | {r['bias']} | {w.get('n', 0)} | {w.get('trades_per_day', np.nan):.2f} | "
                  f"{fmt(w.get('win_rate'), pct=True)} | {fmt(w.get('gross_R'))} | {fmt(w.get('exp_R'))} | {fmt(ug) if ug is not None else 'n/a'} | "
                  f"{w.get('pf', np.nan):.2f} | {fp}/6 | {r.get('coins_positive', 0)}/9 | {r.get('dsr', np.nan):.2f} |")
    pos = [r for r in R if r["wf"].get("exp_R", -1) > 0]
    md += ["", f"Configurations with positive out-of-sample net expectancy: {len(pos)} of {len(R)}. "
           "Per the declared plan, the target grid and stability neighbours run only if at least one is positive, so they were not run."]
    OUT.write_text("\n".join(md) + "\n")
    lines = ["", "## Hypothesis H-MV, Macro View gate (counts: yes, 27 configurations)",
             f"- Date: 2026-11-16. Declared in PROTOCOL Amendment 2. Split: walk-forward test period 2023-01-01..2025-11-14, "
             f"fixed rules, 9 coins, structure stop, 2R. DSR with N = {D['n_trials_total']}.", "",
             "| id | hypothesis | configuration | n | exp R | gross R | PF | folds+ | coins+ | DSR | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        w = r["wf"]; c = criteria(r)
        fp = sum(1 for v in r["folds"].values() if v is not None and np.isfinite(v) and v > 0)
        fails = [k for k, v in c.items() if not v]
        lines.append(f"| {r['id']} | MCB entries taken only with the 10x Macro View bias are profitable | {r['tf']} {r['entry']} bias {r['bias']} "
                     f"(len {r['mv_len']}, thr {r['mv_thresh']}, x{r['mv_mult']}) 2R | {w.get('n', 0)} | {fmt(w.get('exp_R'))} | "
                     f"{fmt(w.get('gross_R'))} | {w.get('pf', np.nan):.2f} | {fp}/6 | {r.get('coins_positive', 0)}/9 | {r.get('dsr', np.nan):.2f} | "
                     f"{'candidate' if not fails else 'fails ' + ','.join(fails)} |")
    led = ROOT / "LEDGER.md"
    s = led.read_text()
    if "## Hypothesis H-MV" not in s:
        led.write_text(s + "\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
