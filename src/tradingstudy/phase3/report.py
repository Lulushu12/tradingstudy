"""Phase 3 report and ledger rows (P3-xxx).
Usage: uv run python -m tradingstudy.phase3.report
"""
from __future__ import annotations

import json

import numpy as np

from tradingstudy.config import REPORTS, ROOT
from tradingstudy.phase2.report import criteria, fmt

IN = REPORTS / "phase3" / "discovery_results.json"
OUT = REPORTS / "phase3" / "DISCOVERY_REPORT.md"
COINS = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE", "SUI", "LINK", "AVAX"]


def main() -> None:
    D = json.loads(IN.read_text())
    R = D["results"]
    md = ["# Phase 3: discovery results", "",
          "Walk-forward rule search (<= 2 conditions, fixed feature list, thresholds from each fold's training data, "
          "7-day embargo and purge). Out-of-sample = the 6 test folds 2023-01-01 to 2025-11-14, full engine and portfolio "
          f"rules. Deflated Sharpe uses N = {D['n_trials_total']} (all configurations so far).", "",
          "## 1. Procedures (structure stop, 2R)", "",
          "| id | Family | TF | Var | OOS trades | Per day | Win | Gross R | Net exp R | PF | Folds + | Coins + | DSR | Rule stability | Final rule |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        w = r["wf"]; f = r.get("folds", {})
        fp = sum(1 for v in f.values() if v is not None and np.isfinite(v) and v > 0)
        md.append(f"| {r['id']} | {r['family']} | {r['tf']} | {r['variant']} | {w.get('n', 0)} | {w.get('trades_per_day', np.nan):.2f} | "
                  f"{fmt(w.get('win_rate'), pct=True)} | {fmt(w.get('gross_R'))} | {fmt(w.get('exp_R'))} | {w.get('pf', np.nan):.2f} | "
                  f"{fp}/6 | {r.get('coins_positive', 0)}/9 | {r.get('dsr', np.nan):.2f} | {r['rule_stability']}/6 | {r['final_rule']} |")
    md += ["", "## 2. Rule chosen in each fold (training data only)", ""]
    for r in R:
        md.append(f"**{r['id']} {r['family']} {r['tf']} {r['variant']}**")
        md.append("")
        md.append("| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |")
        md.append("|---|---|---|---|---|---|---|")
        for fr in r["fold_rules"]:
            te = r["folds"].get(fr["fold"])
            md.append(f"| {fr['fold']} | {fr['rule']} | {fr['train_n']} | {fmt(fr['train_exp'])} | {fr['test_signals']} | "
                      f"{fr['test_selected']} | {fmt(te)} |")
        md.append("")
    for r in R:
        r["crit"] = criteria(r)
        r["crit"]["S10"] = r["rule_stability"] >= 4
    md += ["## 3. Protocol criteria", ""]
    for r in R:
        fails = [k for k, v in r["crit"].items() if not v]
        md.append(f"- {r['id']}: {'meets S1-S5, S7-S10 (S6 stability neighbours still to run)' if not fails else 'fails ' + ', '.join(fails)}")
    OUT.write_text("\n".join(md) + "\n")
    lines = ["", "## Phase 3 discovery procedures (counts: yes, 12 configurations)",
             f"- Date: 2026-11-16. Split: walk-forward, rule chosen on each fold's purged training data, OOS 2023-01-01..2025-11-14."
             f" DSR with N = {D['n_trials_total']}.", "",
             "| id | hypothesis | configuration | n | exp R | gross R | PF | folds+ | coins+ | DSR | stability | final rule | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        w = r["wf"]; f = r.get("folds", {})
        fp = sum(1 for v in f.values() if v is not None and np.isfinite(v) and v > 0)
        fails = [k for k, v in r["crit"].items() if not v]
        lines.append(f"| {r['id']} | A <=2-condition context filter makes the {r['family']} events profitable out of sample | "
                     f"{r['family']} {r['tf']} {r['variant']} structure stop 2R, walk-forward rule search | {w.get('n', 0)} | "
                     f"{fmt(w.get('exp_R'))} | {fmt(w.get('gross_R'))} | {w.get('pf', np.nan):.2f} | {fp}/6 | {r.get('coins_positive', 0)}/9 | "
                     f"{r.get('dsr', np.nan):.2f} | {r['rule_stability']}/6 | {r['final_rule']} | "
                     f"{'candidate' if not fails else 'fails ' + ','.join(fails)} |")
    led = ROOT / "LEDGER.md"
    s = led.read_text()
    if "## Phase 3 discovery procedures" not in s:
        led.write_text(s + "\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
