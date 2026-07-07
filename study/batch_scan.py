import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
from research import scan_conditions

# (tf, rr, atr_mult)
JOBS = [
    ("4H", 1.0, 1.5), ("4H", 2.0, 1.5),
    ("1D", 1.0, 1.5), ("1D", 2.0, 1.5),
    ("1h", 2.0, 1.5), ("1h", 1.0, 2.0),
    ("15m", 1.0, 1.5), ("15m", 2.0, 1.5),
]
for tf, rr, am in JOBS:
    try:
        scan_conditions(tf, atr_mult=am, rr=rr, max_bars=300)
    except Exception as e:
        print(f"{tf} rr={rr} am={am} ERROR {e}")
