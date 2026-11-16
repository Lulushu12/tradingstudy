import numpy as np
import pandas as pd
import pytest

from tradingstudy.backtest import engine as E
from tradingstudy.backtest.portfolio import run_portfolio
from tradingstudy.backtest.stats import deflated_sharpe, prop_monte_carlo

H = 3600 * 10**9
T0 = pd.Timestamp("2024-01-01 01:00", tz="UTC").value


def sim(coin, t_sig_h, t_end_h, net_R, status=E.FILLED):
    return {"coin": coin, "sig_ts": T0 + int(t_sig_h * H), "status": status, "fill_ts": T0 + int(t_sig_h * H),
            "end_ts": T0 + int(t_end_h * H), "net_R": net_R, "touched": 1}


def test_one_per_coin_and_cap_of_three():
    rows = [sim("A", 0, 5, 1), sim("A", 1, 2, 1),            # A busy until 5h -> second A skipped
            sim("B", 1, 5, 1), sim("C", 1, 5, 1), sim("D", 2, 5, 1),  # D would be the 4th open -> skipped
            sim("D", 6, 7, 1)]                                # after all closed -> taken
    s, _ = run_portfolio(pd.DataFrame(rows))
    assert s["taken"].tolist() == [True, False, True, True, False, True]


def test_daily_guard_stops_new_entries():
    rows = [sim(c, i, i + 0.5, -1.05) for i, c in enumerate("ABCDE")]  # each loss ~0.525%
    s, _ = run_portfolio(pd.DataFrame(rows))
    # after 4 losses realized day P&L ~ -2.1% <= -2% -> 5th skipped
    assert s["taken"].tolist() == [True, True, True, True, False]


def test_pending_unfilled_orders_occupy_but_do_not_pay():
    rows = [sim("A", 0, 3, np.nan, status=E.CANCELLED), sim("A", 1, 2, 1.0)]
    s, summ = run_portfolio(pd.DataFrame(rows))
    assert s["taken"].tolist() == [True, False] and summ["final_equity"] == 1.0


def test_monte_carlo_extremes():
    start, end = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-03-01", tz="UTC")
    days = pd.date_range(start, end, freq="D", tz="UTC")[:-1]
    loss = pd.DataFrame({"net_R": -1.0, "end_ts": [d.value + H for d in days]})
    out = prop_monte_carlo(loss, start, end, paths=500)
    assert out["p_max_breach_90d"] == 1.0          # 0.5% loss every day -> 6% gone in ~13 days
    none = pd.DataFrame({"net_R": [], "end_ts": []})
    assert prop_monte_carlo(none, start, end, paths=200)["p_any_breach_90d"] == 0.0


def test_deflated_sharpe_behaviour():
    p1 = deflated_sharpe(0.1, 1000, 0.0, 3.0, 1, 0.0)
    assert p1 == pytest.approx(0.9992, abs=1e-3)   # single trial: plain probabilistic Sharpe vs 0
    p800 = deflated_sharpe(0.1, 1000, 0.0, 3.0, 800, 0.03**2)
    assert p800 < p1                                # more trials -> harder to clear


def test_structure_stops_side_and_minimum():
    from tradingstudy.backtest.signals import _finish
    sig = pd.DataFrame({"close": [100.0, 100.0, 100.0, 100.0], "atr14": [2.0] * 4, "direction": [1, 1, -1, -1]})
    out = _finish(sig.copy(), np.array([98.0, 99.5, 103.0, 99.0]))
    # long stop 2 below = 1 ATR ok; long stop 0.5 below < 0.5 ATR -> skipped; short stop 3 above ok; short stop below entry -> skipped
    assert out["stop_dist"].tolist()[0] == 2.0 and np.isnan(out["stop_dist"].iloc[1])
    assert out["stop_dist"].iloc[2] == 3.0 and np.isnan(out["stop_dist"].iloc[3])
