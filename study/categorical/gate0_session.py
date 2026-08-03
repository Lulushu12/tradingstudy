"""Gate 0 fairness check: is the effect hiding in a session window?

The main Gate 0 run tests BTCUSDT.P around the clock. The video's actual claim is
narrower than that: NQ futures, 9:33 to 9:50 a.m. ET, in the minutes after the
equity open. A 24/7 crypto average could in principle wash out a real effect that
only exists in a specific high-participation window.

BTC is not NQ and crypto has no opening auction, so this cannot vindicate the NQ
version. But BTC does respond to the US equity open, and if the categorical label
carries ANY session-dependent predictive content this is where it should surface.
If it is absent here too, "it only works at the open" stops being a free excuse and
becomes a claim that needs its own evidence on its own data.

Reports continuation rate by ER decile within each UTC hour bucket, with the
equity-open hour (13:30 UTC = 9:30 ET during US daylight time) called out.
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate0  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))

N_WIN, K_ATR, HORIZON = 20, 1.0, 40


def main():
    df = gate0.load("5m")
    s = gate0.build_samples(df, N_WIN, K_ATR, HORIZON, "ER")
    s["dt"] = df["dt"].to_numpy()
    s = s[s["valid"]].reset_index(drop=True)

    decided = (~s["ambig"].to_numpy()) & (s["cont"].to_numpy() | s["rev"].to_numpy())
    cont = s["cont"].to_numpy()
    edges = np.quantile(s["score"], np.linspace(0, 1, 11))
    dec = np.clip(np.digitize(s["score"], edges[1:-1]), 0, 9)

    hour = pd.to_datetime(s["dt"]).dt.hour.to_numpy()
    minute = pd.to_datetime(s["dt"]).dt.minute.to_numpy()

    lines = ["# Gate 0 session check: does the label work at the US equity open?", ""]
    lines.append(
        "BTCUSDT.P 5m, ER(20), symmetric +/-1.0 x ATR14 barriers, 40-bar horizon. "
        "`continuation` = the barrier in the direction of the 20-bar displacement was struck first. "
        "Under a martingale every cell is 50%."
    )
    lines.append("\n## Continuation rate by UTC hour and ER decile\n")
    lines.append("| UTC hour | ET (DST) | n | ER dec 0 | ER dec 9 | spread | rho |")
    lines.append("|---|---|---|---|---|---|---|")

    for h in range(24):
        hm = (hour == h) & decided
        if hm.sum() < 2000:
            continue
        rates = []
        for j in range(10):
            m = hm & (dec == j)
            rates.append(cont[m].mean() if m.sum() > 200 else np.nan)
        rates = np.array(rates)
        ok = np.isfinite(rates)
        rho = stats.spearmanr(np.arange(10)[ok], rates[ok]).statistic if ok.sum() >= 4 else np.nan
        et = (h - 4) % 24
        flag = "  <-- equity open" if h == 13 else ""
        lines.append(
            f"| {h:02d}:00 | {et:02d}:00{flag} | {int(hm.sum()):,} | {rates[0]*100:.2f}% | "
            f"{rates[9]*100:.2f}% | {(rates[9]-rates[0])*100:+.2f} | {rho:+.3f} |"
        )

    # The tightest analogue of his actual window: first 20 minutes after the open.
    lines.append("\n## The closest analogue of the 9:33-9:50 ET window\n")
    lines.append("| window (UTC) | n | ER dec 0 | ER dec 9 | spread | rho | overall cont |")
    lines.append("|---|---|---|---|---|---|---|")
    windows = {
        "13:30-13:55 (open + 25m)": (hour == 13) & (minute >= 30),
        "13:30-14:30 (first hour)": ((hour == 13) & (minute >= 30)) | (hour == 14),
        "14:30-20:00 (rest of RTH)": (hour >= 14) & (hour < 20),
        "00:00-13:30 (outside RTH)": (hour < 13) | ((hour == 13) & (minute < 30)),
    }
    for name, mask in windows.items():
        wm = mask & decided
        if wm.sum() < 1000:
            lines.append(f"| {name} | {int(wm.sum()):,} | insufficient | | | | |")
            continue
        rates = []
        for j in range(10):
            m = wm & (dec == j)
            rates.append(cont[m].mean() if m.sum() > 100 else np.nan)
        rates = np.array(rates)
        ok = np.isfinite(rates)
        rho = stats.spearmanr(np.arange(10)[ok], rates[ok]).statistic if ok.sum() >= 4 else np.nan
        lines.append(
            f"| {name} | {int(wm.sum()):,} | {rates[0]*100:.2f}% | {rates[9]*100:.2f}% | "
            f"{(rates[9]-rates[0])*100:+.2f} | {rho:+.3f} | {cont[wm].mean()*100:.2f}% |"
        )

    txt = "\n".join(lines)
    with open(os.path.join(OUT, "GATE0_SESSION.md"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
