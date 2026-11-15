"""Build the Gate 2 baseline report and append every configuration to LEDGER.md.
Usage: uv run python -m tradingstudy.phase2.report
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from tradingstudy.config import REPORTS, ROOT

IN = REPORTS / "phase2" / "baseline_results.json"
OUT = REPORTS / "phase2" / "BASELINE_REPORT.md"
REF_TARGET = "2R"


def ref_stop(tf: str) -> float:
    return 2.0 if tf == "6m" else 1.5


def criteria(r: dict) -> dict:
    w, mc = r["wf"], r.get("mc", {})
    n = w.get("n", 0)
    fn = r.get("folds_n", {})
    folds = [v for v in r.get("folds", {}).values() if v is not None and np.isfinite(v)]
    return {
        "S1": w.get("exp_R", -9) >= 0.10,
        "S2": w.get("pf", 0) >= 1.20,
        "S3": n >= 300 and min(fn.values(), default=0) >= 25 and 0.3 <= w.get("trades_per_day", 0) <= 3,
        "S4": sum(1 for v in folds if v > 0) >= 4,
        "S5": r.get("coins_positive", 0) >= 6 and r.get("nonbtc_positive", 0) >= 5 and (r.get("max_coin_share") or 9) <= 0.35,
        "S7": (r.get("dsr") or 0) >= 0.95,
        "S8": mc.get("p_max_breach_90d", 1) <= 0.10 and mc.get("p_daily_breach_90d", 1) <= 0.05,
        "S9": w.get("months_positive", 0) >= 0.55,
    }


def fmt(x, nd=3, pct=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{100 * x:.0f}%" if pct else f"{x:+.{nd}f}" if nd == 3 else f"{x:.{nd}f}"


def label(r):
    h = f" +HTF {r['htf']}" if r.get("htf") else ""
    return f"{r['family']} {r['tf']} {r['variant']}{h} stop {r['stop']}xATR tgt {r['target']}"


def main() -> None:
    D = json.loads(IN.read_text())
    R = D["results"]
    for r in R:
        r["crit"] = criteria(r)
    rows = []
    for r in R:
        w = r["wf"]
        folds = r.get("folds", {})
        rows.append({"id": r["id"], "family": r["family"], "tf": r["tf"], "variant": r["variant"], "stop": r["stop"],
                     "target": r["target"], "htf": r.get("htf"), "n": w.get("n", 0), "exp": w.get("exp_R", np.nan),
                     "pf": w.get("pf", np.nan), "win": w.get("win_rate", np.nan), "fee": w.get("fee_R", np.nan),
                     "slip": w.get("slip_R", np.nan), "fill": w.get("fill_rate", np.nan), "tpd": w.get("trades_per_day", np.nan),
                     "missed": w.get("missed_fills", 0), "missed_win": w.get("missed_winners", 0),
                     "folds_pos": sum(1 for v in folds.values() if v is not None and np.isfinite(v) and v > 0),
                     "coins_pos": r.get("coins_positive", 0), "nonbtc_pos": r.get("nonbtc_positive", 0),
                     "dsr": r.get("dsr", np.nan), "p_any90": r.get("mc", {}).get("p_any_breach_90d", np.nan),
                     "months_pos": w.get("months_positive", np.nan), "exp_2022": r["y2022"].get("exp_R", np.nan),
                     "n_2022": r["y2022"].get("n", 0), "streak": w.get("max_loss_streak", 0),
                     "passes": sum(r["crit"].values()), "fails": ",".join(k for k, v in r["crit"].items() if not v)})
    T = pd.DataFrame(rows)
    ref = T[(T.target == REF_TARGET) & (T.stop == T.tf.map(ref_stop))]
    md = ["# Gate 2: Baseline Report", "",
          "Walk-forward test period 2023-01-01 to 2025-11-14 (6 folds), all 9 coins, fees, stop slippage, limit fills and "
          "missed fills always on, portfolio guards on. Baselines have no fitted parameters, so the same rule runs in every "
          f"fold. {len(R)} configurations evaluated, all logged in LEDGER.md (P2-001 to P2-{len(R):03d}).", ""]
    md += ["## 1. Headline: reference label (1.5 x ATR stop, 2.0 on 6m; 2R target)", "",
           "| Config | Trades | Per day | Win | Exp R | PF | Fee R | Fill | Missed (winners) | Folds + | Coins + | DSR | P(breach 90d) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, x in ref.iterrows():
        h = f" +{x.htf}" if x.htf else ""
        md.append(f"| {x.family} {x.tf} {x.variant}{h} | {x.n} | {x.tpd:.2f} | {fmt(x.win, pct=True)} | {fmt(x.exp)} | {x.pf:.2f} | "
                  f"{x.fee:.3f} | {fmt(x.fill, pct=True)} | {x.missed} ({x.missed_win}) | {x.folds_pos}/6 | {x.coins_pos}/9 | "
                  f"{x.dsr:.2f} | {fmt(x.p_any90, pct=True)} |")
    md += ["", "## 2. All labels: spread of expectancy across the 7 targets x stops", "",
           "| Family | TF | Variant | Configs | Positive | Min exp R | Median | Max | Best label |", "|---|---|---|---|---|---|---|---|---|"]
    for (fam, tf, var), g in T[T.family != "B3"].groupby(["family", "tf", "variant"], sort=False):
        b = g.loc[g.exp.idxmax()]
        md.append(f"| {fam} | {tf} | {var} | {len(g)} | {(g.exp > 0).sum()} | {fmt(g.exp.min())} | {fmt(g.exp.median())} | "
                  f"{fmt(g.exp.max())} | stop {b.stop} {b.target} (n={b.n}) |")
    byid = {r["id"]: r for r in R}
    md += ["", "## 3. Trend regime breakdown (reference configs)", "",
           "R1 = 4h EMA200 direction relative to the trade (+1 with trend, -1 against, 0 mixed). "
           "R2 = 4h ADX >= 25 with DI direction relative to the trade (0 = no trend). Cells: expectancy R (trades).", "",
           "| Config | R1 with | R1 against | R1 mixed | R2 trend with | R2 trend against | R2 no trend |", "|---|---|---|---|---|---|---|"]
    def cell(d, k):
        v = d.get(k)
        return f"{v['exp_R']:+.3f} ({v['n']})" if v else "n/a"
    for _, x in ref.iterrows():
        r = byid[x.id]
        h = f" +{x.htf}" if x.htf else ""
        md.append(f"| {x.family} {x.tf} {x.variant}{h} | {cell(r['regime_r1'], '1.0')} | {cell(r['regime_r1'], '-1.0')} | "
                  f"{cell(r['regime_r1'], '0.0')} | {cell(r['regime_r2'], '1.0')} | {cell(r['regime_r2'], '-1.0')} | {cell(r['regime_r2'], '0.0')} |")
    coins = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE", "SUI", "LINK", "AVAX"]
    md += ["", "## 4. By coin (reference configs, expectancy R)", "", "| Config | " + " | ".join(coins) + " |", "|---|" + "---|" * len(coins)]
    for _, x in ref[ref.family != "B3"].iterrows():
        c = byid[x.id]["coins"]
        md.append(f"| {x.family} {x.tf} {x.variant} | " + " | ".join(f"{c[k]['exp_R']:+.2f}" if k in c else "n/a" for k in coins) + " |")
    md += ["", "## 5. By session (reference configs, expectancy R (trades))", "", "| Config | asia 0-8 | europe 8-13 | us 13-21 | late 21-24 |", "|---|---|---|---|---|"]
    for _, x in ref[ref.family != "B3"].iterrows():
        s = byid[x.id]["session"]
        md.append(f"| {x.family} {x.tf} {x.variant} | " + " | ".join(cell(s, k) for k in ("asia", "europe", "us", "late")) + " |")
    md += ["", "## 6. By fold (reference configs, expectancy R)", "", "| Config | 2022 (info) | " + " | ".join(byid[ref.iloc[0].id]["folds"]) + " |",
           "|---|---|" + "---|" * 6]
    for _, x in ref[ref.family != "B3"].iterrows():
        f = byid[x.id]["folds"]
        md.append(f"| {x.family} {x.tf} {x.variant} | {fmt(x.exp_2022)} ({x.n_2022}) | " + " | ".join(fmt(v) for v in f.values()) + " |")
    md += ["", "## 7. Protocol criteria (S6 and S10 are not applicable to fixed baselines)", ""]
    crit = pd.DataFrame([r["crit"] for r in R])
    md.append("Configurations meeting each criterion: " + ", ".join(f"{k} {int(crit[k].sum())}/{len(crit)}" for k in crit.columns))
    md.append(f"\nConfigurations meeting all of S1-S5, S7-S9: {int(crit.all(axis=1).sum())}.")
    best = T.loc[T.exp.idxmax()]
    md += ["", f"Highest walk-forward expectancy of all {len(R)}: {best.id} ({best.family} {best.tf} {best.variant} stop {best.stop} "
           f"{best.target}{' +' + best.htf if best.htf else ''}) at {fmt(best.exp)} R over {best.n} trades, DSR {best.dsr:.2f}. "
           "Picking the best of 212 is itself a selection; the DSR is what corrects for it."]
    OUT.write_text("\n".join(md) + "\n")
    T.to_csv(REPORTS / "phase2" / "baseline_table.csv", index=False)
    # ---- ledger ----
    hyp = {"B1": "Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy",
           "B2": "Baseline 2 (plain range flip) has positive net expectancy",
           "B3": "HTF layer filter improves Baseline 1"}
    lines = ["", "## Phase 2 baselines (counts: yes, 212 configurations)",
             "- Date: 2026-11-15. Split: walk-forward test period 2023-01-01..2025-11-14, fixed rules (no fitting), all 9 coins.",
             "- Columns: n = filled trades; exp = net expectancy R; folds+ = positive folds of 6; coins+ = positive coins of 9;"
             " verdict = protocol criteria failed (S6/S10 n/a for fixed baselines).", "",
             "| id | hypothesis | configuration | n | exp R | PF | fee R | folds+ | coins+ | DSR | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, x in T.iterrows():
        v = "meets S1-S5,S7-S9" if not x.fails else f"fails {x.fails}"
        lines.append(f"| {x.id} | {hyp[x.family]} | {label(byid[x.id])} | {x.n} | {fmt(x.exp)} | {x.pf:.2f} | {x.fee:.3f} | "
                     f"{x.folds_pos}/6 | {x.coins_pos}/9 | {x.dsr:.2f} | {v} |")
    led = ROOT / "LEDGER.md"
    s = led.read_text()
    if "## Phase 2 baselines" not in s:
        led.write_text(s + "\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
