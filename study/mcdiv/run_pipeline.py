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
    """WT is computed (port matches TradingView to float precision and is
    cleaner across export-file boundaries). MFI is the spec's clone formula
    per the trader's decision (their own indicator is canonical; note it does
    NOT reproduce TradingView's exported Mny Flow, corr ~0.96, MAE ~4.2)."""
    df = df.reset_index(drop=True).copy()
    # some parquets carry a broken ts column; dt is authoritative
    df["ts"] = (df["dt"].astype("datetime64[ns, UTC]").astype("int64")
                // 10**9).astype("int64")
    df["wt1"], df["wt2"] = wavetrend(df)
    df["mfi"] = mfi_clone(df)
    df["atr14"] = atr14(df)
    return df


def bad_zone_mask(df, after_bars=100, min_gap_s=1800):
    """Bars within after_bars after a time gap (exported-indicator warmup
    desync + indicator-state discontinuity), plus the first 200 bars."""
    ts = df["ts"].to_numpy()
    mask = np.zeros(len(df), bool)
    mask[:200] = True
    gaps = np.where(np.diff(ts) > min_gap_s + 900)[0]
    for g in gaps:
        mask[g + 1: g + 1 + after_bars] = True
    return mask


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
    bad = bad_zone_mask(df15)

    def clean(s):
        if bad[s.signal_i]:
            return False
        for ev in (s.wt_ev, s.mfi_ev):
            if ev is not None and bad[ev.ref_i]:
                return False
        if s.fr_ref_i is not None and bad[s.fr_ref_i]:
            return False
        return True

    n0 = len(all_sigs)
    all_sigs = [s for s in all_sigs if clean(s)]
    print(f"Excluded {n0 - len(all_sigs)} signals in warmup/gap desync zones")
    for name in ("A", "B", "WTdiv", "MFIdiv"):
        by = pd.Series([s.direction for s in all_sigs if s.system == name])
        print(f"System {name}: {len(by)} signals (long {int((by>0).sum())} / short {int((by<0).sum())})")

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
