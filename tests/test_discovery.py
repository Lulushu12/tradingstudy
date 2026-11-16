import numpy as np
import pandas as pd

from tradingstudy.phase3 import discovery as D


def synth(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "status": 0, "atr_pctile_30d": rng.random(n), "funding_z_rel": rng.standard_normal(n),
        "cmf_rel": rng.standard_normal(n), "cmf4h_rel": rng.standard_normal(n),
        "confluence_types": rng.integers(0, 4, n).astype(float), "sr_dist": rng.random(n) * 3,
        "r1_rel": rng.choice([-1.0, 0.0, 1.0], n), "r2_rel": rng.choice([-1.0, 0.0, 1.0], n),
        "htf_near_cross_rel": rng.choice([0.0, 1.0], n), "htf_mf_rel": rng.choice([0.0, 1.0], n),
        "session": rng.choice(["asia", "europe", "us", "late"], n), "fib_exec_in_0618_zone": rng.choice([0.0, 1.0], n)})
    df["net_R"] = rng.standard_normal(n) * 0.2 - 0.1
    return df


def test_search_finds_planted_two_condition_rule():
    df = synth()
    edge = (df.r1_rel == 1.0) & (df.atr_pctile_30d > 2 / 3)
    df.loc[edge, "net_R"] += 1.0
    best = D.search(df)
    feats = {c[0] for c in best["rule"]}
    assert feats == {"r1_rel", "atr_pctile_30d"} and best["n"] >= D.MIN_TRAIN_TRADES


def test_search_respects_minimum_trades_and_ignores_unfilled():
    df = synth(400)
    df.loc[:5, "net_R"] = 50.0          # a tiny lucky cluster must not be picked (n < 100)
    df.loc[6:, "status"] = np.where(np.arange(len(df) - 6) % 2 == 0, 0, 1)
    best = D.search(df)
    assert best["n"] >= D.MIN_TRAIN_TRADES
    assert best["n"] <= (df.status == 0).sum()


def test_rule_key_ignores_thresholds():
    a = (("atr_pctile_30d", "gt", 0.61), ("r1_rel", "eq", 1.0))
    b = (("r1_rel", "eq", 1.0), ("atr_pctile_30d", "gt", 0.70))
    assert D.rule_key(a) == D.rule_key(b)
