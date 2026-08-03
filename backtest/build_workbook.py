"""Assemble the deliverable workbook.

xlsxwriter is used rather than openpyxl purely for scale: the three trade logs
carry ~28,500 rows x 38 columns and openpyxl's cell objects make that a
multi-gigabyte proposition. Everything the workbook computes is a live formula
against the trade-log sheets, so filtering or editing a log updates the summary.

Numbers that were computed by the analysis scripts rather than by the sheet
(max drawdown, buy & hold, the sensitivity grids) are labelled with their
source script wherever they appear.
"""

import csv
import json
import os

import xlsxwriter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# Two files, deliberately.
#
# The six full trade logs carry 28,497 rows whose thesis column averages ~600
# characters - 8.8 MB that is slow to open and awkward to scroll. Splitting keeps
# the analysis file at ~2 MB so it opens instantly, while the prose logs stay
# available in full for anyone auditing individual trades. The analysis file
# carries every live formula plus a compact numeric mirror of the trades.
OUT_STUDY = os.path.join(HERE, "ETH_LINK_SOL_trading_study.xlsx")
OUT_LOGS = os.path.join(HERE, "ETH_LINK_SOL_trade_logs.xlsx")

# Compact mirror used by the Summary formulas: outcome fields only, no prose.
STATS_HEADERS = [
    ("trade_id", "Trade ID", 12), ("symbol", "Symbol", 11),
    ("entry_time_utc", "Entry (UTC)", 16), ("setup", "Setup", 16),
    ("direction", "Side", 7), ("conviction", "Conviction /10", 13),
    ("selective", "In Selective Book", 15), ("exit_reason", "Exit Reason", 13),
    ("bars_held", "Bars Held", 10), ("status", "Status", 9),
    ("r_multiple", "R Multiple", 11), ("pnl_usd", "P&L ($1k risk)", 14),
    ("mae_r", "MAE (R)", 9), ("mfe_r", "MFE (R)", 9),
]
SCOL = {k: i for i, (k, _, _) in enumerate(STATS_HEADERS)}

SYMBOLS = [("ETHUSDT", "ETH"), ("LINKUSDT", "LINK"), ("SOLUSDT", "SOL")]
FONT = "Arial"

# Columns whose CSV value is "percent as a number" and must be stored as a fraction.
PCT_COLS = {"stop_pct", "target_pct", "atr_pct", "gross_pct", "cost_pct", "net_pct",
            "vol_regime_pct"}

HEADERS = [
    ("trade_id", "Trade ID", 12), ("symbol", "Symbol", 10),
    ("entry_time_utc", "Entry (UTC)", 16), ("bar_index", "Bar #", 8),
    ("setup", "Setup", 16), ("direction", "Side", 7),
    ("conviction", "Conviction /10", 13), ("selective", "In Selective Book", 15),
    ("entry_price", "Entry", 12), ("stop_loss", "Stop Loss", 12),
    ("take_profit", "Take Profit", 12), ("stop_pct", "Stop Dist %", 11),
    ("target_pct", "Target Dist %", 12), ("planned_rr", "Planned R:R", 11),
    ("stop_logic", "Stop Placement Logic", 26), ("target_logic", "Target Placement Logic", 26),
    ("time_stop_bars", "Time Stop (h)", 12),
    ("atr_pct", "ATR %", 9), ("adx", "ADX", 8), ("rsi", "RSI", 8),
    ("stretch_atr", "Stretch (ATR)", 12), ("vol_regime_pct", "Vol Regime %ile", 14),
    ("ema21", "EMA21", 12), ("ema55", "EMA55", 12), ("ema200", "EMA200", 12),
    ("exit_time_utc", "Exit (UTC)", 16), ("exit_price", "Exit", 12),
    ("exit_reason", "Exit Reason", 13), ("bars_held", "Bars Held", 10),
    ("status", "Status", 9), ("gross_pct", "Gross %", 10),
    ("cost_pct", "Costs %", 10), ("net_pct", "Net %", 10),
    ("r_multiple", "R Multiple", 11), ("pnl_usd", "P&L ($1k risk)", 14),
    ("mae_r", "MAE (R)", 9), ("mfe_r", "MFE (R)", 9),
    ("thesis", "Trade Thesis", 120),
]
COL = {k: i for i, (k, _, _) in enumerate(HEADERS)}
CUM_COL = len(HEADERS)  # appended "Cumulative R" formula column


def load_trades(symbol):
    with open(os.path.join(DATA, f"{symbol}_trades.csv")) as fh:
        return list(csv.DictReader(fh))


def make_formats(wb):
    base = {"font_name": FONT, "font_size": 10}
    f = {
        "title": wb.add_format({**base, "font_size": 16, "bold": True, "font_color": "#1F3864"}),
        "sub": wb.add_format({**base, "font_size": 11, "italic": True, "font_color": "#555555"}),
        "h1": wb.add_format({**base, "font_size": 12, "bold": True, "font_color": "#1F3864",
                             "bottom": 2, "border_color": "#1F3864"}),
        "hdr": wb.add_format({**base, "bold": True, "bg_color": "#1F3864", "font_color": "white",
                              "align": "center", "valign": "vcenter", "text_wrap": True,
                              "border": 1, "border_color": "#0F1F3D"}),
        "text": wb.add_format({**base, "valign": "top"}),
        "wrap": wb.add_format({**base, "text_wrap": True, "valign": "top"}),
        "label": wb.add_format({**base, "bold": True}),
        "note": wb.add_format({**base, "font_size": 9, "italic": True, "font_color": "#777777",
                               "text_wrap": True, "valign": "top"}),
        "num2": wb.add_format({**base, "num_format": "0.00"}),
        "num3": wb.add_format({**base, "num_format": "0.000"}),
        "num1": wb.add_format({**base, "num_format": "0.0"}),
        "int": wb.add_format({**base, "num_format": "#,##0"}),
        "px": wb.add_format({**base, "num_format": "#,##0.0000"}),
        "pct2": wb.add_format({**base, "num_format": "0.00%;(0.00%);-"}),
        "pct1": wb.add_format({**base, "num_format": "0.0%;(0.0%);-"}),
        "usd": wb.add_format({**base, "num_format": "$#,##0;($#,##0);-"}),
        "ctr": wb.add_format({**base, "align": "center"}),
        "good": wb.add_format({**base, "num_format": "0.000", "font_color": "#006100",
                               "bg_color": "#C6EFCE"}),
        "bad": wb.add_format({**base, "num_format": "0.000", "font_color": "#9C0006",
                              "bg_color": "#FFC7CE"}),
        "key": wb.add_format({**base, "bold": True, "bg_color": "#FFF2CC", "border": 1,
                              "border_color": "#BF8F00"}),
    }
    return f


def col_fmt(field, f):
    if field in PCT_COLS:
        return f["pct2"]
    return {
        "conviction": f["num1"], "planned_rr": f["num2"],
        "entry_price": f["px"], "stop_loss": f["px"], "take_profit": f["px"],
        "exit_price": f["px"], "ema21": f["px"], "ema55": f["px"], "ema200": f["px"],
        "adx": f["num1"], "rsi": f["num1"], "stretch_atr": f["num2"],
        "r_multiple": f["num3"], "pnl_usd": f["usd"],
        "mae_r": f["num2"], "mfe_r": f["num2"],
        "bar_index": f["int"], "bars_held": f["int"], "time_stop_bars": f["int"],
        "direction": f["ctr"], "selective": f["ctr"], "status": f["ctr"],
        "thesis": f["wrap"],
    }.get(field, f["text"])


def write_log(wb, f, name, rows):
    ws = wb.add_worksheet(name)
    ws.freeze_panes(1, 3)
    ws.set_row(0, 30)
    for i, (field, label, width) in enumerate(HEADERS):
        ws.write(0, i, label, f["hdr"])
        ws.set_column(i, i, width, col_fmt(field, f))
    ws.write(0, CUM_COL, "Cumulative R", f["hdr"])
    ws.set_column(CUM_COL, CUM_COL, 13, f["num1"])

    running = [0.0]
    for r, row in enumerate(rows, start=1):
        for field, _, _ in HEADERS:
            v = row[field]
            c = COL[field]
            if v == "" or v is None:
                continue
            if field in PCT_COLS:
                ws.write_number(r, c, float(v) / 100.0)
            elif field in ("bar_index", "bars_held", "time_stop_bars"):
                ws.write_number(r, c, int(v))
            elif field in ("conviction", "entry_price", "stop_loss", "take_profit",
                           "planned_rr", "adx", "rsi", "stretch_atr", "ema21", "ema55",
                           "ema200", "exit_price", "r_multiple", "pnl_usd", "mae_r", "mfe_r"):
                ws.write_number(r, c, float(v))
            else:
                ws.write(r, c, v)
        # Running total of realised R, written as a value.
        #
        # This was originally a chain of 28,497 incremental formulas across the
        # six logs. LibreOffice could not recalculate that in 10 minutes, and a
        # workbook that cannot be verified is worse than one carrying a
        # documented computed column. The Summary tab's statistics remain live
        # formulas, which is where recalculation actually earns its keep.
        if row["status"] == "CLOSED":
            running[0] += float(row["r_multiple"])
        ws.write_number(r, CUM_COL, round(running[0], 4))

    ws.autofilter(0, 0, len(rows), CUM_COL)
    return ws


def xl(row, col):
    """0-indexed (row, col) -> A1 reference."""
    s = ""
    c = col
    while True:
        s = chr(ord("A") + c % 26) + s
        c = c // 26 - 1
        if c < 0:
            break
    return f"{s}{row + 1}"


def colletter(col):
    return xl(0, col)[:-1]


def write_stats_sheet(wb, f, rows):
    """Compact numeric mirror of every trade - the Summary formulas' data source."""
    ws = wb.add_worksheet("Trade Stats")
    ws.freeze_panes(1, 2)
    ws.set_row(0, 30)
    for i, (field, label, width) in enumerate(STATS_HEADERS):
        ws.write(0, i, label, f["hdr"])
        ws.set_column(i, i, width, col_fmt(field, f))
    for r, row in enumerate(rows, start=1):
        for field, _, _ in STATS_HEADERS:
            v = row[field]
            c = SCOL[field]
            if v == "" or v is None:
                continue
            if field == "bars_held":
                ws.write_number(r, c, int(v))
            elif field in ("conviction", "r_multiple", "pnl_usd", "mae_r", "mfe_r"):
                ws.write_number(r, c, float(v))
            elif field == "selective":
                ws.write(r, c, "YES" if v == "True" else "NO")
            else:
                ws.write(r, c, v)
    ws.autofilter(0, 0, len(rows), len(STATS_HEADERS) - 1)
    ws.write(len(rows) + 2, 0,
             "Every row above also appears, with its full written thesis and all indicator and level "
             "detail, in ETH_LINK_SOL_trade_logs.xlsx. This sheet exists because the Summary tab's "
             "formulas need a compact numeric source that recalculates quickly.", f["note"])
    return ws


def main():
    analysis = json.load(open(os.path.join(DATA, "analysis.json")))
    robust = json.load(open(os.path.join(DATA, "robustness.json")))
    sweep = json.load(open(os.path.join(DATA, "sweep.json")))

    all_rows = {sym: load_trades(sym) for sym, _ in SYMBOLS}
    sel_rows = {sym: [r for r in all_rows[sym] if r["selective"] == "True"]
                for sym, _ in SYMBOLS}
    combined = [r for sym, _ in SYMBOLS for r in all_rows[sym]]

    from sheets import (write_readme, write_summary, write_findings,
                        write_breakdown, write_sweep, write_stability, write_equity,
                        write_targets, verify_summary, write_v2)

    n_checks = verify_summary(SYMBOLS, all_rows, sel_rows, analysis)
    print(f"verified {n_checks} Summary values against analyze.py - all agree")

    # ---- File 1: the study (all analysis, all live formulas) ----
    wb = xlsxwriter.Workbook(OUT_STUDY, {"constant_memory": False})
    f = make_formats(wb)
    write_readme(wb, f)
    summary_ws = wb.add_worksheet("Summary")
    findings_ws = wb.add_worksheet("Findings")
    write_breakdown(wb, f, SYMBOLS, analysis)
    write_sweep(wb, f, SYMBOLS, sweep)
    write_targets(wb, f, SYMBOLS)
    write_v2(wb, f, SYMBOLS)
    write_stability(wb, f, SYMBOLS, robust)
    write_equity(wb, f, SYMBOLS, all_rows, sel_rows)
    write_stats_sheet(wb, f, combined)
    write_summary(summary_ws, f, SYMBOLS, len(combined), analysis, all_rows, sel_rows,
                  SCOL, colletter)
    write_findings(findings_ws, f, analysis, robust)
    wb.close()
    print(f"wrote {OUT_STUDY}  ({os.path.getsize(OUT_STUDY) / 1e6:.2f} MB)")

    # ---- File 2: the full trade logs (static, no formulas) ----
    wb2 = xlsxwriter.Workbook(OUT_LOGS, {"constant_memory": True})
    f2 = make_formats(wb2)
    for sym, short in SYMBOLS:
        write_log(wb2, f2, f"{short} All Trades", all_rows[sym])
        write_log(wb2, f2, f"{short} Selective", sel_rows[sym])
    wb2.close()
    print(f"wrote {OUT_LOGS}  ({os.path.getsize(OUT_LOGS) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
