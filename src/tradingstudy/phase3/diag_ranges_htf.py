"""Descriptive diagnostics E004 (range edges) and E005 (HTF entries with LTF structure stops). Declared in LEDGER.md
before running. No strategy is selected here; nothing counts against the budget.
Usage: uv run python -m tradingstudy.phase3.diag_ranges_htf
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.backtest.signals import stack_mask
from tradingstudy.backtest.stats import WF_END, WF_START
from tradingstudy.config import DEV_START, REPORTS, SYMBOLS, TIMEFRAMES
from tradingstudy.data.guard import load_bars
from tradingstudy.features import mcb, ta
from tradingstudy.features.build import bars_any
from tradingstudy.features.divergence import mf_fractal_divergences_v2, wt_dot_divergences_v2
from tradingstudy.features.macro import macro_bias
from tradingstudy.phase2.baselines import m1_arrays
from tradingstudy.structure.ranges import range_setups_v2
from tradingstudy.structure.swings import zigzag

OUT = REPORTS / "phase3" / "RANGE_HTF_DIAGNOSTICS.md"
MIN_NS = 60 * 10**9
FEE = 0.0008


# ---------------------------------------------------------------- E004: range edges
@nb.njit(cache=True)
def _race(ts, h, l, start, entry, target, fail, d, t_end):
    """Per event: +1 target (mid) first, -1 fail level first (same minute = fail), 0 unresolved by t_end."""
    n = start.shape[0]
    out = np.zeros(n, dtype=np.int8)
    for k in range(n):
        for i in range(start[k], ts.shape[0]):
            if ts[i] >= t_end[k]:
                break
            if d[k] == 1:
                if l[i] <= fail[k]:
                    out[k] = -1; break
                if h[i] >= target[k]:
                    out[k] = 1; break
            else:
                if h[i] >= fail[k]:
                    out[k] = -1; break
                if l[i] <= target[k]:
                    out[k] = 1; break
    return out


def range_edges(sym: str, tf: str, A: dict) -> tuple[pd.DataFrame, dict]:
    m = TIMEFRAMES[tf]
    b = load_bars(sym, tf, "dev_warmup")
    sw = zigzag(b, 3)
    st, _, rg = range_setups_v2(b, sw)
    atr = st["atr14"].to_numpy()
    act, hi, lo = st["range_active"].to_numpy(), st["range_high"].to_numpy(), st["range_low"].to_numpy()
    c, h, l = b["close"].to_numpy(), b["high"].to_numpy(), b["low"].to_numpy()
    dev = b.index >= DEV_START
    # D1
    rd = rg[(b.index[rg["confirm"].to_numpy()] >= DEV_START)]
    life_h = (rd["end"] - rd["confirm"]).to_numpy() * m / 60.0
    d1 = {"ranges": len(rd), "life_h": life_h, "inside_share": float(act[dev].mean())}
    # D2 touches (range known as of the previous bar)
    rows = []
    for t in np.nonzero(dev)[0]:
        if t < 1 or not act[t - 1]:
            continue
        a, H, L = atr[t - 1], hi[t - 1], lo[t - 1]
        mid = (H + L) / 2
        if l[t] <= L + 0.25 * a and c[t - 1] > L + 0.25 * a:
            rows.append((t, 1, c[t], mid, L - 0.25 * a))
        if h[t] >= H - 0.25 * a and c[t - 1] < H - 0.25 * a:
            rows.append((t, -1, c[t], mid, H + 0.25 * a))
    if not rows:
        return pd.DataFrame(), d1
    e = pd.DataFrame(rows, columns=["bar", "d", "entry", "target", "fail"])
    e["time"] = b.index[e["bar"].to_numpy()] + pd.Timedelta(minutes=m)
    # already beyond fail or at target on the touch close
    beyond = (e.d * (e.entry - e.fail)) <= 0
    at_mid = (e.d * (e.target - e.entry)) <= 0
    e = e[~at_mid].copy()
    t_ns = e["time"].dt.as_unit("ns").astype("int64").to_numpy()
    start = np.searchsorted(A["ts"], t_ns, side="left").astype(np.int64)
    res = _race(A["ts"], A["h"], A["l"], start, e.entry.to_numpy(), e.target.to_numpy(), e.fail.to_numpy(),
                e.d.to_numpy(np.int64), t_ns + 200 * m * MIN_NS)
    e["res"] = res
    e.loc[beyond[~at_mid].to_numpy(), "res"] = -1
    R = e.d * (e.entry - e.fail)
    e["bench"] = np.clip(R / (e.d * (e.target - e.fail)), 0, 1)
    e["gross_R"] = np.where(e.res == 1, (e.d * (e.target - e.entry)) / R, np.where(e.res == -1, -1.0, np.nan))
    e.loc[beyond[~at_mid].to_numpy(), "gross_R"] = np.nan  # no sensible R when already beyond the fail level
    e["fee_R"] = FEE * e.entry / R.where(R > 0)
    e["coin"] = sym
    return e, d1


# ---------------------------------------------------------------- E005: HTF entries, LTF structure stops
@nb.njit(cache=True)
def _first_touch(ts, h, l, start, entry, R, d, barriers, horizon_ns):
    n = start.shape[0]
    nb_ = barriers.shape[0]
    first = np.zeros((n, nb_), dtype=np.int8)
    for k in range(n):
        if start[k] >= ts.shape[0]:
            continue
        t_end = ts[start[k]] + horizon_ns
        done = np.zeros(nb_, dtype=np.bool_)
        for i in range(start[k], ts.shape[0]):
            if ts[i] >= t_end:
                break
            f = (h[i] - entry[k]) / R[k] if d[k] == 1 else (entry[k] - l[i]) / R[k]
            a = (entry[k] - l[i]) / R[k] if d[k] == 1 else (h[i] - entry[k]) / R[k]
            for j in range(nb_):
                if not done[j]:
                    if a >= barriers[j]:
                        first[k, j] = -1; done[j] = True
                    elif f >= barriers[j]:
                        first[k, j] = 1; done[j] = True
    return first


def ltf_stops(sym: str, times: pd.DatetimeIndex, entry: np.ndarray, d: np.ndarray, m15: pd.DataFrame, sw15: pd.DataFrame,
              atr15: np.ndarray) -> np.ndarray:
    """Most recent confirmed 15m zigzag swing beyond the entry (long: swing low below entry), known by the signal
    time, plus 1 x ATR(15m) of the last 15m bar closed by then."""
    known = (sw15["confirm_time"] + pd.Timedelta(minutes=15)).dt.as_unit("ns").astype("int64").to_numpy()
    px, ty = sw15["price"].to_numpy(), sw15["type"].to_numpy()
    close_t = (m15.index + pd.Timedelta(minutes=15)).as_unit("ns").asi8
    out = np.full(len(times), np.nan)
    tn = times.as_unit("ns").asi8
    for k in range(len(times)):
        nk = np.searchsorted(known, tn[k], side="right")
        ia = np.searchsorted(close_t, tn[k], side="right") - 1
        if ia < 0:
            continue
        want = -1 if d[k] == 1 else 1
        for j in range(nk - 1, max(nk - 60, -1), -1):
            if ty[j] == want and d[k] * (entry[k] - px[j]) > 0:
                out[k] = px[j] - d[k] * atr15[ia]
                break
    return out


def htf_signals(sym: str, tf: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    m = TIMEFRAMES[tf]
    b = load_bars(sym, tf, "dev_warmup")
    wt = mcb.wavetrend(b)
    mf = mcb.mf_pine_ha(b, smooth=1)
    df = pd.concat([wt_dot_divergences_v2(wt, b), mf_fractal_divergences_v2(mf, b)], axis=1)
    bias = macro_bias(bars_any(sym, m * 10, "dev_warmup"), m * 10, b.index)["bias_lean"].to_numpy()
    sigs = {}
    for name in ("stack A", "WT div"):
        if name == "stack A":
            bull, bear = stack_mask(df, "bull", "A"), stack_mask(df, "bear", "A")
        else:
            bull, bear = df["wtdiv_bull_reg"].to_numpy(bool), df["wtdiv_bear_reg"].to_numpy(bool)
        d = np.where(bull & ~bear, 1, np.where(bear & ~bull, -1, 0))
        for gate in ("ungated", "Macro View lean"):
            dd = d if gate == "ungated" else np.where(bias == d, d, 0)
            idx = np.nonzero(dd)[0]
            sigs[(name, gate)] = pd.DataFrame({"time": b.index[idx] + pd.Timedelta(minutes=m), "entry": b["close"].to_numpy()[idx],
                                               "d": dd[idx], "atr_htf": ta.atr(b.high, b.low, b.close, 14)[idx]})
    rng = np.random.default_rng(abs(hash((sym, tf))) % 2**32)
    pos = np.sort(rng.choice(np.arange(500, len(b)), size=min(400, len(b) - 500), replace=False))
    sigs[("CONTROL random", "ungated")] = pd.DataFrame({"time": b.index[pos] + pd.Timedelta(minutes=m), "entry": b["close"].to_numpy()[pos],
                                                        "d": rng.choice([-1, 1], size=len(pos)),
                                                        "atr_htf": ta.atr(b.high, b.low, b.close, 14)[pos]})
    return sigs


def main() -> None:
    arrays = {s: m1_arrays(s) for s in SYMBOLS}
    pct = lambda x: f"{100 * x:.1f}%"
    md = ["# Diagnostics E004 (range edges) and E005 (HTF entries with LTF structure stops)", "",
          "Descriptive, declared in LEDGER.md before running. No strategy selected; nothing counted against the budget.", ""]
    # ---- E004
    md += ["## E004: do range edges hold?", "",
           "D1 = ranges confirmed in the dev period, their life after confirmation, and the share of time price sits inside a "
           "confirmed range. D2 = first touches of an active range edge from inside; from the touch bar's close, does price "
           "reach the range midpoint before trading 0.25 ATR beyond the edge (1m path, same minute = fail)? Benchmark = "
           "driftless random walk for the same distances. Implied R = fade to mid with the stop 0.25 ATR beyond the edge.", "",
           "| TF | Ranges | Median life after confirm (h) | Time inside | Touches | Resolved | Mid first | Random-walk benchmark | Difference | Gross R | Fee R | Net R |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    e4 = {}
    for tf in ("15m", "24m", "1h", "4h"):
        ev, d1s = [], []
        for s in SYMBOLS:
            e, d1 = range_edges(s, tf, arrays[s])
            ev.append(e); d1s.append(d1)
        E = pd.concat([x for x in ev if len(x)], ignore_index=True)
        life = np.concatenate([d["life_h"] for d in d1s])
        r = E[E.res != 0]
        ok = r.dropna(subset=["gross_R"])
        e4[tf] = E
        md.append(f"| {tf} | {sum(d['ranges'] for d in d1s)} | {np.median(life):.1f} | {pct(np.mean([d['inside_share'] for d in d1s]))} | "
                  f"{len(E)} | {len(r)} | {pct((r.res == 1).mean())} | {pct(r.bench.mean())} | {100 * ((r.res == 1).mean() - r.bench.mean()):+.1f} pts | "
                  f"{ok.gross_R.mean():+.3f} | {ok.fee_R.mean():.3f} | {(ok.gross_R - ok.fee_R).mean():+.3f} |")
        print("E004", tf, flush=True)
    md += ["", "By edge (bottom = long fade, top = short fade):", "", "| TF | Edge | Resolved | Mid first | Benchmark | Net R |", "|---|---|---|---|---|---|"]
    for tf, E in e4.items():
        for d, nm in ((1, "bottom"), (-1, "top")):
            r = E[(E.res != 0) & (E.d == d)]
            ok = r.dropna(subset=["gross_R"])
            md.append(f"| {tf} | {nm} | {len(r)} | {pct((r.res == 1).mean())} | {pct(r.bench.mean())} | {(ok.gross_R - ok.fee_R).mean():+.3f} |")
    # ---- E005
    md += ["", "## E005: HTF entries with a 15m structure stop (+1 ATR)", "",
           "From the HTF signal bar's close, on 1m bars over 24 h (1h signals) or 48 h (4h signals): share of signals touching "
           "+x R before -x R (same minute = adverse; neither = excluded). R = distance to the most recent confirmed 15m swing "
           "beyond the entry plus 1 x ATR(15m). Walk-forward test period 2023-01-01 to 2025-11-14.", "",
           "| Signal TF | Entries | Gate | Signals | Median stop (HTF ATR) | +0.5R first | +1R first | +2R first | +3R first | Fee R |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    bars_ = np.array([0.5, 1.0, 2.0, 3.0])
    for tf, hz in (("1h", 24), ("4h", 48)):
        groups = {}
        for s in SYMBOLS:
            m15 = load_bars(s, "15m", "dev_warmup")
            sw15 = zigzag(m15, 3)
            atr15 = ta.atr(m15.high, m15.low, m15.close, 14)
            for key, sg in htf_signals(s, tf).items():
                sg = sg[(sg.time >= WF_START) & (sg.time < WF_END)].reset_index(drop=True)
                if sg.empty:
                    continue
                stop = ltf_stops(s, pd.DatetimeIndex(sg.time), sg.entry.to_numpy(), sg.d.to_numpy(), m15, sw15, atr15)
                sg["R"] = sg.d * (sg.entry - stop)
                sg = sg[sg.R > 0].reset_index(drop=True)
                A = arrays[s]
                start = np.searchsorted(A["ts"], sg.time.dt.as_unit("ns").astype("int64").to_numpy(), side="left").astype(np.int64)
                ft = _first_touch(A["ts"], A["h"], A["l"], start, sg.entry.to_numpy(), sg.R.to_numpy(), sg.d.to_numpy(np.int64),
                                  bars_, hz * 60 * MIN_NS)
                for j, x in enumerate(bars_):
                    sg[f"f{x}"] = ft[:, j]
                sg["fee_R"] = FEE * sg.entry / sg.R
                sg["stop_htf_atr"] = sg.R / sg.atr_htf
                groups.setdefault(key, []).append(sg)
        for (name, gate), parts in groups.items():
            G = pd.concat(parts, ignore_index=True)
            cells = []
            for x in bars_:
                c = G[f"f{x}"]
                cells.append(pct((c == 1).sum() / max((c != 0).sum(), 1)))
            md.append(f"| {tf} | {name} | {gate} | {len(G)} | {G.stop_htf_atr.median():.2f} | " + " | ".join(cells) + f" | {G.fee_R.mean():.3f} |")
        print("E005", tf, flush=True)
    OUT.write_text("\n".join(md) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
