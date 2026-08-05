"""4H OSCILLATOR-state filters for the lower-TF SFP divergence shorts.

The 4H EMA200 gate failed (mtf_stack.py) — it lags and adds correlation, not
information. Here we gate by 4H momentum STATE instead:

  WaveTrend cross recency: a bearish WT cross a few closed 4H bars behind us =
      the down-leg is young; a cross many bars back = leg exhausting; wt1/wt2
      converging from the bear side = a bullish cross is imminent (reversal risk).
  MFI regime: low MFI = money flowing out (trend conviction for shorts);
      mid-zone MFI (~40-60) = chop.
  ADX regime: ADX high = trending market, low = chop; DI- > DI+ = down-trending.

All 4H features are read from the last CLOSED 4H bar (as-of by bar close, causal).
Entries: the star SFP short (bear0|1 & LOCAL downtrend) on 1h/30m/15m.
Exits: fixed 1R, fixed 2R, half@1R->breakeven + 3-ATR trail. Train<2025 / Test.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from engine import FEE_RT
from research import breakeven_wr
from trend_runner import run_fixed
from sfp_exits import run_half1R_trail
from mtf_stack import SEC, asof_flag, load, report

def osc_features(src="4H"):
    """Boolean oscillator-state arrays + the close-time axis for a source TF."""
    df4, _ = load(src)
    n4 = len(df4)
    close4 = df4["time"].values + SEC[src]
    wt1 = df4["wt1"].values; wt2 = df4["wt2"].values
    bear = wt1 < wt2
    cross_dn = bear & ~np.roll(bear, 1); cross_dn[0] = False
    last = np.maximum.accumulate(np.where(cross_dn, np.arange(n4), -1))
    since = np.where(last >= 0, np.arange(n4)-last, 10**6)   # bars since bear cross
    gap = wt2 - wt1                                          # >0 in bear state
    imminent = bear & (gap <= 5)                             # about to cross back up
    mfi4 = df4["mfi14"].values
    adx4 = df4["adx14"].values
    di_dn = df4["di_m"].values > df4["di_p"].values
    F4 = {
        "WT bear state":            bear,
        "WT fresh cross (<=3)":     bear & (since <= 3),
        "WT cross 4-9 back":        bear & (since >= 4) & (since <= 9),
        "WT cross >=10 (late)":     bear & (since >= 10),
        "WT bear, not imminent":    bear & ~imminent,
        "WT fresh & not imminent":  bear & (since <= 3) & ~imminent,
        "MFI<40":                   mfi4 < 40,
        "MFI<30":                   mfi4 < 30,
        "MFI 40-60 (chop check)":   (mfi4 >= 40) & (mfi4 <= 60),
        "ADX>=25":                  adx4 >= 25,
        "ADX>=25 & DI down":        (adx4 >= 25) & di_dn,
        "ADX<20 (chop check)":      adx4 < 20,
        "osc stack (WTfresh&MFI<40&ADX>=25)":
            bear & (since <= 3) & ~imminent & (mfi4 < 40) & (adx4 >= 25),
    }
    return close4, F4

def run_tf(tf, close4, F4, src="4H", rrs=(1.0, 2.0)):
    df, m = load(tf)
    n = len(df)
    close_t = df["time"].values + SEC[tf]
    star = (m["bear0"] | m["bear1"]) & (df["close"] < df["ema200"]).values
    sfmean = (1.5*df["atr14"]/df["open"].shift(-1)).mean()
    print(f"\n################ TF={tf}  src={src}  feeR~{FEE_RT/sfmean:.2f}  "
          f"(star={int(star.sum())}) ################")
    variants = {f"star [ref, no {src} filter]": star}
    for fname, flag4 in F4.items():
        variants[f"star & {src} {fname}"] = star & asof_flag(close4, flag4, close_t)
    Lz = np.zeros(n, bool)
    for vname, mask in variants.items():
        print(f"  -- {vname}  (n={int(mask.sum())})")
        if not mask.any():
            continue
        for rr in rrs:
            report(f"fixed {rr:.0f}R", run_fixed(df, Lz, mask, rr=rr),
                   breakeven_wr(rr, sfmean))
        report("half@1R->BE + 3ATRtrail", run_half1R_trail(df, Lz, mask, k=3.0))

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    src = "4H"
    rrs = (1.0, 2.0)
    if args and args[0].startswith("src="):
        src = args[0][4:]; args = args[1:]
    if args and args[0].startswith("rr="):
        rrs = tuple(float(x) for x in args[0][3:].split(",")); args = args[1:]
    close4, F4 = osc_features(src)
    for tf in (args or ["1h", "30m", "15m"]):
        run_tf(tf, close4, F4, src=src, rrs=rrs)
