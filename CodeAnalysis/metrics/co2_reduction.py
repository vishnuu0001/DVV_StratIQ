# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Estimates the CO₂ reduction potential (tons/year) achievable by migrating
# Date: 2026-01-27
# ---------------------------------------------------------------------------
"""
co2_reduction.py
----------------
Estimates the CO₂ reduction potential (tons/year) achievable by migrating
on-premises workloads to cloud-native infrastructure.

Model
~~~~~
1. Estimate on-prem server count from SLOC (1 server per 50 K SLOC, min 1).
2. Each on-prem server consumes ~4 000 kWh / year (incl. cooling, PUE ≈ 1.8).
3. Equivalent cloud workload uses ~40 % less energy (PUE ≈ 1.2, right-sizing).
4. The remaining *cloud gap* – (100 – cloud_score) / 100 – scales the savings:
   a fully cloud-ready repo has already captured most savings.
5. CO₂ conversion: US average grid ≈ 0.386 kg CO₂ / kWh (EPA 2023).
"""
from __future__ import annotations

from dataclasses import dataclass


# ── Constants ─────────────────────────────────────────────────────────────────
_SLOC_PER_SERVER     = 50_000        # lines of code per virtual server
_KWH_PER_SERVER_YEAR = 4_000         # on-prem kWh / server / year
_CLOUD_EFFICIENCY    = 0.40          # fraction of energy saved by moving to cloud
_KG_CO2_PER_KWH      = 0.386        # kg CO₂ / kWh (EPA 2023 US average)


@dataclass
class Co2ReductionScore:
    co2_tons_year:     float   # estimated CO₂ saved per year (metric tons)
    mwh_year:          float   # estimated electricity saved per year (MWh)
    servers_estimated: int     # inferred on-prem server headcount
    cloud_gap_pct:     float   # how much cloud migration remains (0–100)
    mtm_change:        float   # month-on-month change (placeholder, =0 on first scan)


class Co2ReductionCalculator:
    """
    Derives a CO₂ reduction potential from SLOC count and cloud maturity score.
    """

    # Function: calculate
    def calculate(self, total_sloc: int, cloud_score: float) -> Co2ReductionScore:
        servers          = max(1, total_sloc // _SLOC_PER_SERVER)
        cloud_gap        = max(0.0, (100.0 - cloud_score) / 100.0)

        energy_saved_kwh = (
            servers
            * _KWH_PER_SERVER_YEAR
            * _CLOUD_EFFICIENCY
            * cloud_gap
        )
        co2_tons  = round(energy_saved_kwh * _KG_CO2_PER_KWH / 1_000, 2)   # kg → tons
        mwh_saved = round(energy_saved_kwh / 1_000, 2)

        return Co2ReductionScore(
            co2_tons_year     = co2_tons,
            mwh_year          = mwh_saved,
            servers_estimated = servers,
            cloud_gap_pct     = round(cloud_gap * 100, 1),
            mtm_change        = 0.0,
        )
