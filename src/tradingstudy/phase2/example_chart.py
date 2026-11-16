"""Annotated chart of one real range-flip example (ETH 15m, dev period) to explain the definition."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tradingstudy.config import REPORTS
from tradingstudy.data.guard import load_bars
from tradingstudy.features import ta
from tradingstudy.structure.ranges import ranges_and_flips
from tradingstudy.structure.swings import zigzag

INK, MUTED, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"


def main(sym="ETH", when="2022-10-05 16:15"):
    b = load_bars(sym, "15m", "dev_warmup")
    sw = zigzag(b, 3)
    _, ev, _ = ranges_and_flips(b, sw)
    e = ev[(ev.time == pd.Timestamp(when, tz="UTC")) & (ev.variant == 0)].iloc[0]
    rs, rc, bk, en = int(e.range_start), int(e.range_confirm), int(e.break_bar), int(e.bar)
    atr = ta.atr(b.high, b.low, b.close, 14)
    lo_, hi_ = rs - 12, en + 6
    w = b.iloc[lo_:hi_]
    x = np.arange(len(w))
    X = lambda bar: bar - lo_
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=150)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    up = w.close >= w.open
    ax.vlines(x, w.low, w.high, color=MUTED, lw=0.8, zorder=2)
    ax.bar(x[up], (w.close - w.open)[up], bottom=w.open[up], width=0.65, color=SURF, edgecolor=MUTED, lw=0.8, zorder=3)
    ax.bar(x[~up], (w.open - w.close)[~up], bottom=w.close[~up], width=0.65, color=MUTED, edgecolor=MUTED, lw=0.8, zorder=3)
    # range box (start of range to breakdown)
    ax.add_patch(plt.Rectangle((X(rs) - 0.5, e.range_low), X(bk) - X(rs), e.range_high - e.range_low, color=BLUE, alpha=0.10, lw=0, zorder=1))
    ax.hlines([e.range_high], X(rs) - 0.5, X(bk), color=BLUE, lw=1.5, zorder=4)
    ax.hlines([e.range_low], X(rs) - 0.5, X(en) + 3, color=BLUE, lw=1.5, ls=(0, (4, 3)), zorder=4)
    ax.text(X(rs), e.range_high, f" range high {e.range_high:.2f}", va="bottom", color=INK, fontsize=9)
    ax.text(X(en) + 3, e.range_low, f" old range low {e.range_low:.2f}\n (support -> resistance)", va="center", color=INK, fontsize=9)
    # the four swings that define the range
    four = sw[sw.confirm_bar <= rc].tail(4)
    for i, s in enumerate(four.itertuples()):
        y = s.price
        lab = ("H" if s.type == 1 else "L") + str(1 + i // 2)
        ax.plot(X(s.pivot_bar), y, "o", ms=8, color=BLUE, mec=SURF, mew=2, zorder=5)
        ax.annotate(lab, (X(s.pivot_bar), y), xytext=(0, 10 if s.type == 1 else -16), textcoords="offset points", ha="center", color=INK, fontsize=10, weight="bold")
    ax.axvline(X(rc), color=MUTED, lw=1, ls=":", zorder=1)
    ymax = w.high.max()
    last = four.iloc[-1]
    lab4 = ("H" if last.type == 1 else "L") + "2"
    move = "fell" if last.type == 1 else "rose"
    ax.text(X(rc), ymax, f" 1. range confirmed here\n (4th swing {lab4} confirmed once\n price {move} 3 ATR from it)", va="top", color=INK, fontsize=9)
    # breakdown
    ax.plot(X(bk), b.close.iloc[bk], "o", ms=9, color=ORANGE, mec=SURF, mew=2, zorder=6)
    ax.annotate("2. breakdown: close more than\n0.25 ATR below range low", (X(bk), b.close.iloc[bk]), xytext=(-150, -45), textcoords="offset points",
                color=INK, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    # lower swing low
    nl = sw[(sw.confirm_bar > bk) & (sw.type == -1) & (sw.price < e.range_low)].iloc[0]
    ax.plot(X(nl.pivot_bar), nl.price, "o", ms=9, color=ORANGE, mec=SURF, mew=2, zorder=6)
    ax.annotate("3. lower swing low (new support),\nconfirmed when price bounced 3 ATR", (X(nl.pivot_bar), nl.price),
                xytext=(X(nl.pivot_bar) - 6, nl.price + 1.0), textcoords="data", ha="right", va="center",
                color=INK, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    # retest zone and entry
    a = atr[en]
    ax.add_patch(plt.Rectangle((X(bk), e.range_low - 0.25 * a), X(en) + 3 - X(bk), 0.25 * a, color=ORANGE, alpha=0.15, lw=0, zorder=1))
    ax.plot(X(en), b.close.iloc[en], "v", ms=11, color=AQUA, mec=SURF, mew=1.5, zorder=7)
    ax.annotate("4-5. price retests the old range low;\na red candle that touched it closes\nback below it = ENTRY (Variant A).\nVariant B enters on the first touch.", (X(en), b.close.iloc[en]),
                xytext=(X(en) + 9, e.range_low - 12), textcoords="data", ha="left", va="center",
                color=INK, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_title(f"How the range flip is detected: real example, {sym} 15m, {b.index[rs]:%Y-%m-%d} (development data)", loc="left", color=INK, fontsize=12)
    ticks = x[::16]
    ax.set_xticks(ticks); ax.set_xticklabels([w.index[i].strftime("%m-%d %H:%M") for i in ticks], fontsize=8, color=MUTED)
    ax.tick_params(axis="y", labelsize=8, colors=MUTED)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(axis="y", color="#e6e5e0", lw=0.6, zorder=0)
    ax.set_xlim(-1, len(w) + 40)
    fig.tight_layout()
    out = REPORTS / "phase2" / "range_flip_example.png"
    fig.savefig(out, facecolor=SURF)
    print(out, "| range bars:", bk - rs, "| breakdown to entry:", en - bk, "| ATR at entry:", round(a, 2),
          "| 4 swings:", [(("H" if t == 1 else "L"), round(p, 2)) for t, p in zip(four.type, four.price)], "| new low:", round(nl.price, 2))


if __name__ == "__main__":
    main()
