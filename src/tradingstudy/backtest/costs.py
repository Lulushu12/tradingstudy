"""Cost assumptions frozen in PROTOCOL section 3."""
SLIPPAGE = {"BTC": 0.0003, "ETH": 0.0004, "XRP": 0.0005, "ADA": 0.0006, "DOGE": 0.0006, "LINK": 0.0006,
            "AVAX": 0.00065, "SOL": 0.0007, "SUI": 0.0008}

# tick sizes inferred from the 1m data per year (reports/phase1/gate1_facts.json); default applies to other years
TICKS = {"BTC": {2022: 0.01, "default": 0.1}, "ETH": {"default": 0.01}, "SOL": {2025: 0.01, "default": 0.001},
         "ADA": {"default": 0.0001}, "XRP": {"default": 0.0001}, "DOGE": {"default": 0.00001},
         "SUI": {"default": 0.0001}, "LINK": {"default": 0.001}, "AVAX": {"default": 0.001}}


def tick_for(sym: str, year: int) -> float:
    t = TICKS[sym]
    return t.get(year, t["default"])
