"""Feature cache: features + structure for each coin and execution TF (dev scope with warm-up), stored as parquet.
Rebuild with rebuild=True whenever feature code changes."""
from __future__ import annotations

import warnings

import pandas as pd

from tradingstudy.config import DATA
from tradingstudy.features.build import build_features
from tradingstudy.structure.build import build_structure

CACHE = DATA / "cache"


def load_cached(sym: str, tf: str, rebuild: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    CACHE.mkdir(parents=True, exist_ok=True)
    fp, ep = CACHE / f"{sym}_{tf}_features.parquet", CACHE / f"{sym}_{tf}_events.parquet"
    if fp.exists() and ep.exists() and not rebuild:
        return pd.read_parquet(fp), pd.read_parquet(ep)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = build_features(sym, tf)
        s, ev = build_structure(sym, tf)
    df = pd.concat([f, s], axis=1)
    df.to_parquet(fp)
    ev.to_parquet(ep)
    return df, ev
