"""Stage G: final verdict on the 15m-path-resolved alt short book."""
import numpy as np, pandas as pd
from c_portfolio import portfolio
from e_kill import block_bootstrap

r = pd.read_parquet("trades_15m_truth.parquet")
r["yr"] = r.exit_dt.dt.year
S = r[r.side == -1].copy(); L = r[r.side == 1].copy()

print("="*104)
print("G1. 15m-PATH-RESOLVED RESULTS  (point-in-time >$50M/d universe, 10bp fee + 5bp slip, funding modelled)")
print("="*104)
for lab, t in [("SHORT book", S), ("LONG book", L), ("both", r)]:
    m, k = block_bootstrap(t)
    lo, hi = np.percentile(m, [2.5, 97.5])
    print(f"{lab:<12} n={len(t):<6} WR={(t.netR>0).mean():5.1%}  E={t.netR.mean():+.3f}R  "
          f"95% CI [{lo:+.3f},{hi:+.3f}]  P(E<=0)={np.mean(m<=0):.3f}")

print("\nhow much the modelling assumption mattered (short book expectancy):")
print("  4h bars, stop fills at stop price   : +0.132R   (optimistic)")
print("  4h bars, stop fills at bar close    : +0.041R   (pessimistic)")
print(f"  15m path, stop fills at 15m close   : {S.netR.mean():+.3f}R   (best estimate)")

print("\n" + "="*104)
print("G2. PER-YEAR (net R/trade, 15m-resolved)")
print("="*104)
piv = r.pivot_table(index="yr", columns=r.side.map({1:"long",-1:"short"}),
                    values="netR", aggfunc=["mean","size"])
print(piv.round(3).to_string())

print("\n" + "="*104)
print("G3. TAIL RISK OF THE SHORT BOOK")
print("="*104)
print("  " + "  ".join(f"p{q}={np.percentile(S.netR,q):+.2f}R" for q in [0.1,1,5,25,50,75,95,99]))
print(f"  worst single trade {S.netR.min():+.2f}R | trades worse than -1.5R: {(S.netR<-1.5).mean():.2%}"
      f" | worse than -2R: {(S.netR<-2).mean():.2%}")
print(f"  worst 1% of trades cost {np.sort(S.netR.values)[:len(S)//100].sum():+.0f}R "
      f"of total {S.netR.sum():+.0f}R")

print("\n" + "="*104)
print("G4. PORTFOLIO (0.5% risk/trade, max 8 concurrent)")
print("="*104)
S = S.rename(columns={"gross_R":"gross_R"})
portfolio(S, label="SHORT alt book")
portfolio(S[S.exit_dt<'2025-01-01'], label="  train 2020-2024")
portfolio(S[S.exit_dt>='2025-01-01'], label="  test  2025-2026")
for risk in [0.0025, 0.005, 0.0075, 0.01]:
    portfolio(S, risk=risk, label=f"  risk={risk:.2%}/trade")

print("\n" + "="*104)
print("G5. COST HEADROOM (extra slippage on top of the 15bp already charged)")
print("="*104)
for extra in [0, 5, 10, 15, 20, 30]:
    adj = S.netR - (extra/1e4)*2/S.sdf
    print(f"  +{extra:2d}bp/side extra  ->  E={adj.mean():+.3f}R   "
          f"train {adj[S.exit_dt<'2025-01-01'].mean():+.3f} / test {adj[S.exit_dt>='2025-01-01'].mean():+.3f}")
