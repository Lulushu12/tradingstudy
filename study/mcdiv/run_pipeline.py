"""End-to-end: load data -> indicators -> divergences -> signals for the four
systems (A, B, WTdiv, MFIdiv) -> trade resolution (1R & 2R) -> feature table.

Outputs study/mcdiv/out/trades.parquet (one row per signal with features and
outcomes) plus a census printout.
"""
import os
import numpy as np
import pandas as pd
from mc_indicators import wavetrend, mfi_clone, atr14
from divergence import all_div_events, stack_variant_a, stack_variant_b, Signal
from backtest import resolve_trades
from features import htf_context, build_features

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def enrich(df):
    df = df.reset_index(drop=True).copy()
    df["wt1"], df["wt2"] = wavetrend(df)
    df["mfi"] = mfi_clone(df)
    df["atr14"] = atr14(df)
    return df


def main():
    df15 = enrich(pd.read_parquet(os.path.join(DATA, "15m.parquet")))
    df1h = enrich(pd.read_parquet(os.path.join(DATA, "1h.parquet")))
    df4h = enrich(pd.read_parquet(os.path.join(DATA, "4h.parquet")))

    wt_events, mfi_events = all_div_events(df15)
    print(f"WT div events: {len(wt_events)}  (bull {sum(1 for e in wt_events if e.direction>0)})")
    print(f"MFI div events: {len(mfi_events)}  (bull {sum(1 for e in mfi_events if e.direction>0)})")

    sig_a = stack_variant_a(wt_events, mfi_events)
    sig_b = stack_variant_b(df15, wt_events, mfi_events)
    sig_wt = [Signal("WTdiv", e.direction, e.confirm_i, e, None, "wt", 0, False)
              for e in wt_events]
    sig_mfi = [Signal("MFIdiv", e.direction, e.confirm_i, None, e, "mfi", 0, False)
               for e in mfi_events]
    all_sigs = sig_a + sig_b + sig_wt + sig_mfi
    for name, sigs in (("A", sig_a), ("B", sig_b), ("WTdiv", sig_wt), ("MFIdiv", sig_mfi)):
        by = pd.Series([s.direction for s in sigs])
        print(f"System {name}: {len(sigs)} signals (long {int((by>0).sum())} / short {int((by<0).sum())})")

    trades = resolve_trades(df15, all_sigs).reset_index(drop=True)
    h1 = htf_context(df15, df1h, "h1")
    h4 = htf_context(df15, df4h, "h4")
    feats = build_features(df15, all_sigs, h1, h4).reset_index(drop=True)
    assert len(trades) == len(feats) == len(all_sigs)
    assert (trades["signal_i"].to_numpy() == feats["signal_i"].to_numpy()).all()
    assert (trades["system"].to_numpy() == feats["system"].to_numpy()).all()
    keep = [c for c in trades.columns
            if c not in ("dt", "system", "direction", "signal_i")]
    merged = pd.concat([feats, trades[keep]], axis=1)
    merged["year"] = pd.to_datetime(merged["dt"]).dt.year
    merged.to_parquet(os.path.join(OUT, "trades.parquet"))
    print(f"\nSaved {len(merged)} rows -> out/trades.parquet")

    for name in ("A", "B", "WTdiv", "MFIdiv"):
        m = merged[(merged["system"] == name) & (~merged["skip"])]
        for rr in (1, 2):
            v = m[f"win{rr}"].dropna()
            if len(v):
                wr = v.mean()
                netr = m[f"netR{rr}"].dropna().mean()
                print(f"{name} @{rr}:1  n={len(v)}  winrate={wr:.3f}  avg netR={netr:+.3f}")


if __name__ == "__main__":
    main()
