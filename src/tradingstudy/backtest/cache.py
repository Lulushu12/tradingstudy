"""Feature cache: features + structure for each coin and execution TF (dev scope with warm-up), stored as parquet.
Rebuild with rebuild=True whenever feature code changes."""
from __future__ import annotations

import warnings

import pandas as pd

from tradingstudy.config import DATA
from tradingstudy.features.build import build_features
from tradingstudy.structure.build import build_structure

CACHE = DATA / "cache"


def load_cached(sym: str, tf: str, rebuild: bool = False, defs: str = "v1") -> tuple[pd.DataFrame, pd.DataFrame]:
    """defs="v1": Phase 2 definitions (reproduces P2-001..212). defs="v2": PROTOCOL Amendment 1."""
    CACHE.mkdir(parents=True, exist_ok=True)
    sfx = "" if defs == "v1" else f"_{defs}"
    fp, ep = CACHE / f"{sym}_{tf}_features{sfx}.parquet", CACHE / f"{sym}_{tf}_events{sfx}.parquet"
    if fp.exists() and ep.exists() and not rebuild:
        return pd.read_parquet(fp), pd.read_parquet(ep)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = build_features(sym, tf, defs=defs)
        s, ev = build_structure(sym, tf, defs=defs)
    df = pd.concat([f, s], axis=1)
    df.to_parquet(fp)
    ev.to_parquet(ep)
    return df, ev
