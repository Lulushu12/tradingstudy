"""
Data loader for the repo's TradingView CSV exports of BINANCE BTCUSDT.P / XRPUSDT.P.

The exports are chunked and overlapping, and several timeframes have gaps where
chunks do not butt up against each other. This module stitches chunks, drops
duplicate timestamps, sorts, and reports gaps honestly rather than silently
forward filling them. A backtest that treats a gap as a contiguous bar sequence
will invent trades that never existed, so gaps are surfaced, not hidden.

All timestamps are unix seconds, UTC. Only OHLCV is retained. The indicator
columns baked into the TradingView exports (Blue Wave, Mny Flow and so on) are
deliberately discarded: everything is recomputed from price here so the source
of every number is this repo, not a chart.
"""

import glob
import os

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bar interval in seconds for each timeframe key.
TF_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
}

# Glob patterns per timeframe, relative to the repo root. Several timeframes are
# spread over more than one directory because of how the exports were taken.
SOURCES = {
    "BTCUSDT": {
        "1m": ["New export/1m/*.csv"],
        "5m": ["5m/**/*.csv", "New export/5m/**/*.csv", "BINANCE_BTCUSDT.P, 5.csv"],
        "15m": ["15/*.csv", "New export/15m/*.csv"],
        "1h": ["1h/*.csv"],
        "4h": ["BINANCE_BTCUSDT.P, 240.csv"],
        "1d": ["BINANCE_BTCUSDT.P, 1D.csv"],
        "1w": ["BINANCE_BTCUSDT.P, 1W.csv"],
    },
    "XRPUSDT": {
        "15m": ["HA SHA MFI/BINANCE_XRPUSDT.P, 15*.csv"],
    },
}

OHLC = ["open", "high", "low", "close"]
OHLCV = OHLC + ["volume"]


def _unix_seconds(index):
    """Unix seconds from a tz-aware DatetimeIndex, independent of its resolution.

    pandas 3 gives these frames datetime64[s] resolution, so a bare
    .astype("int64") already yields seconds while older pandas yields
    nanoseconds. Pinning the unit explicitly keeps this correct either way.
    """
    return index.tz_convert("UTC").tz_localize(None).astype("datetime64[s]").astype("int64")


def _read_one(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    # Duplicate column names (the exports carry two columns both named "plot")
    # make pandas return a DataFrame for df[col]; take the first occurrence.
    out = {}
    for c in ["time"] + OHLC:
        col = df[c]
        out[c] = col.iloc[:, 0] if isinstance(col, pd.DataFrame) else col
    # Some exports (1m, and the XRPUSDT Heikin Ashi set) carry no volume column.
    # Volume stays NaN there rather than being faked, so any volume based
    # strategy fails loudly on those series instead of testing invented data.
    if "volume" in df.columns:
        col = df["volume"]
        out["volume"] = col.iloc[:, 0] if isinstance(col, pd.DataFrame) else col
    else:
        out["volume"] = pd.Series(float("nan"), index=df.index)
    return pd.DataFrame(out)


def load(symbol="BTCUSDT", tf="15m", verbose=True):
    """Load one symbol/timeframe as a UTC-indexed OHLCV frame.

    Returns a DataFrame indexed by tz-aware UTC timestamps with columns
    open/high/low/close/volume, sorted ascending and free of duplicate bars.
    """
    if symbol not in SOURCES:
        raise KeyError(f"unknown symbol {symbol}; have {list(SOURCES)}")
    if tf not in SOURCES[symbol]:
        raise KeyError(f"no {tf} data for {symbol}; have {list(SOURCES[symbol])}")

    paths = []
    for pat in SOURCES[symbol][tf]:
        paths.extend(glob.glob(os.path.join(REPO, pat), recursive=True))
    if not paths:
        raise FileNotFoundError(f"no files matched for {symbol} {tf}")

    df = pd.concat([_read_one(p) for p in sorted(paths)], ignore_index=True)
    df = df.dropna(subset=["time"] + OHLC)
    df["time"] = df["time"].astype("int64")

    before = len(df)
    df = df.drop_duplicates(subset="time", keep="first").sort_values("time")
    dupes = before - len(df)

    df.index = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.drop(columns="time")

    if verbose:
        rep = gap_report(df, tf)
        print(
            f"{symbol} {tf}: {len(df)} bars  "
            f"{df.index[0].date()} -> {df.index[-1].date()}  "
            f"dupes dropped {dupes}  gaps {rep['n_gaps']}  "
            f"coverage {rep['coverage']:.1%}"
        )
    return df[OHLCV]


def gap_report(df, tf):
    """Describe missing bars. Coverage is observed bars over expected bars."""
    step = TF_SECONDS[tf]
    t = _unix_seconds(df.index)
    delta = pd.Series(t).diff().dropna()
    gaps = delta[delta > step]
    span = int(t[-1] - t[0])
    expected = span // step + 1
    return {
        "n_gaps": int(len(gaps)),
        "missing_bars": int(((gaps - step) // step).sum()),
        "largest_gap_bars": int((gaps.max() - step) // step) if len(gaps) else 0,
        "expected": int(expected),
        "observed": int(len(df)),
        "coverage": len(df) / expected if expected else 0.0,
    }


def contiguous_segments(df, tf, min_bars=200):
    """Split a frame into runs of unbroken bars.

    Strategies with state that carries across bars (trends, trailing stops,
    pattern lookbacks) must not read across a gap. Run them per segment and
    pool the trades.
    """
    step = TF_SECONDS[tf]
    t = _unix_seconds(df.index)
    brk = (pd.Series(t).diff() != step).to_numpy().copy()
    brk[0] = True
    seg_id = brk.cumsum()
    segs = [g for _, g in df.groupby(seg_id) if len(g) >= min_bars]
    return segs


if __name__ == "__main__":
    for sym, tfs in SOURCES.items():
        for tf in tfs:
            try:
                d = load(sym, tf)
                segs = contiguous_segments(d, tf)
                print(
                    f"    -> {len(segs)} contiguous segments of >=200 bars, "
                    f"longest {max((len(s) for s in segs), default=0)} bars"
                )
            except Exception as e:
                print(f"{sym} {tf}: FAILED {type(e).__name__}: {e}")
