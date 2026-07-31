"""Pre-generate trade labels for the extended universe, in parallel.

`labels.make` resolves a 2:1 trade from every bar on the real 1-minute path and
caches the result. It is the expensive step in the whole pipeline, and running
it lazily inside the ML driver serialises 31 symbols behind one core. This does
the same work up front across processes so the experiment itself is fast.

Idempotent: `labels.make` returns the cached parquet if it already exists, so
re-running costs nothing.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels as L        # noqa: E402

CORE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]
EXTENDED = ["ADAUSDT", "DOGEUSDT", "LINKUSDT", "LTCUSDT", "AVAXUSDT", "DOTUSDT",
            "ATOMUSDT", "UNIUSDT", "ETCUSDT", "FILUSDT", "NEARUSDT", "AAVEUSDT",
            "ALGOUSDT", "EOSUSDT", "XLMUSDT", "TRXUSDT", "VETUSDT", "SANDUSDT",
            "AXSUSDT", "THETAUSDT", "FTMUSDT", "GRTUSDT", "CHZUSDT", "ENJUSDT",
            "ZILUSDT", "IOTAUSDT"]
ALL = CORE + EXTENDED

TIMEFRAMES = [("4h", 60), ("1h", 96)]


def job(arg):
    symbol, tf, hold = arg
    try:
        d = L.make(symbol, tf, "DESIGN", atr_mult=2.0, rr=2.0, max_hold_bars=hold)
        return f"{symbol:10} {tf:4} ok    {len(d):>7,} bars"
    except Exception as e:                              # noqa: BLE001
        return f"{symbol:10} {tf:4} FAIL  {e}"


def main(symbols=None, workers=4):
    symbols = symbols or ALL
    tasks = [(s, tf, hold) for tf, hold in TIMEFRAMES for s in symbols]
    print(f"pre-generating {len(tasks)} label sets on {workers} processes")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(job, tasks):
            print(r, flush=True)
    print("PRELABEL_DONE")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args or None)
