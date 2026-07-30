"""Drive the optimiser across timeframes and validate every finalist properly."""
import os
import sys
import json

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ruleopt2 as RO     # noqa: E402
import validate as V      # noqa: E402
import dataset as DS      # noqa: E402


def main(tf, hold, depth, beam, cover, min_trades, tag):
    d, book, allc, chosen, final, sl, ss = RO.run(
        tf=tf, hold=hold, depth=depth, beam=beam,
        min_trades=min_trades, cover=cover)
    if not chosen:
        print("no rule set found")
        return
    print("\n" + "=" * 78)
    print("RULE SET")
    for path, side in chosen:
        rule = " & ".join("%s%s%.6g" % (a, ">=" if c > 0 else "<=", q)
                          for a, q, c in path)
        print(f"  {'LONG ' if side>0 else 'SHORT'}  {rule}")
    print("=" * 78)

    T, sel = V.rules_to_trades(d, chosen, tf=tf)
    best = V.report(T, f"{tf} optimised rule set")

    out = {"tf": tf, "hold": hold,
           "rules": [{"side": int(s),
                      "conds": [[a, float(q), int(c)] for a, q, c in p]}
                     for p, s in chosen],
           "proxy": {k: (v if isinstance(v, str) else float(v))
                     for k, v in final.items()}}
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    with open(os.path.join(rep, f"ruleset_{tag}.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nsaved reports/ruleset_{tag}.json")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--hold", type=int, default=60)
    p.add_argument("--depth", type=int, default=4)
    p.add_argument("--beam", type=int, default=20)
    p.add_argument("--cover", type=float, default=0.85)
    p.add_argument("--min-trades", type=int, default=300)
    p.add_argument("--tag", default=None)
    a = p.parse_args()
    main(a.tf, a.hold, a.depth, a.beam, a.cover, a.min_trades,
         a.tag or a.tf.replace("min", "m"))
