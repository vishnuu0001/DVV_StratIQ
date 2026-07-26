# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: scanner/cloud_pricing.py
# Date: 2025-07-23
# ---------------------------------------------------------------------------
"""
scanner/cloud_pricing.py

Static VM flavor catalogs, storage tier catalogs, PaaS service pricing, and
helper functions used by report_builder to produce PDF-level rich reports.

All pricing is approximate (East US / us-east-1 / us-central1 region, 2025).
Exact figures depend on region, reservation commitment, and billing currency.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

# ─── Azure VM Flavor Catalog ──────────────────────────────────────────────────

@dataclass
class VMFlavor:
    name: str
    cpu_cores: int
    ram_gb: float
    family: str            # General Purpose / Memory Optimized / Compute Optimized / Storage Optimized
    # Pay As You Go — Linux base (no OS license)
    cost_payg_linux: float
    # Reservation discounts expressed as monthly-equivalent cost
    cost_1yr_full_linux: float
    cost_1yr_no_upfront_linux: float
    cost_3yr_full_linux: float
    cost_3yr_no_upfront_linux: float
    # Compute Savings Plans
    cost_1yr_savings_full_linux: float = 0.0
    cost_1yr_savings_no_upfront_linux: float = 0.0
    cost_3yr_savings_full_linux: float = 0.0
    cost_3yr_savings_no_upfront_linux: float = 0.0
    # Windows Server OS license surcharge (add to linux base)
    windows_surcharge: float = 0.0
    # RHEL license surcharge
    rhel_surcharge: float = 0.0

    # Function: cost_for
    def cost_for(
        self,
        plan: str,
        os_name: str = "",
    ) -> float:
        """Return monthly cost for a given plan and OS."""
        os_lower = (os_name or "").lower()
        base = self._base_cost(plan)
        surcharge = 0.0
        if "windows" in os_lower:
            surcharge = self.windows_surcharge
        elif "red hat" in os_lower or "rhel" in os_lower:
            surcharge = self.rhel_surcharge
        return round(base + surcharge, 3)

    # Function: _base_cost
    def _base_cost(self, plan: str) -> float:
        plan_lower = plan.lower()
        if "pay as you go" in plan_lower or "payg" in plan_lower:
            return self.cost_payg_linux
        if "3 year" in plan_lower or "3yr" in plan_lower or "3 yr" in plan_lower:
            if "no upfront" in plan_lower:
                return self.cost_3yr_no_upfront_linux
            if "savings" in plan_lower:
                return self.cost_3yr_savings_full_linux or self.cost_3yr_full_linux
            return self.cost_3yr_full_linux
        # Default: 1yr
        if "no upfront" in plan_lower:
            return self.cost_1yr_no_upfront_linux
        if "savings" in plan_lower:
            return self.cost_1yr_savings_full_linux or self.cost_1yr_full_linux
        return self.cost_1yr_full_linux


# Azure East US flavor catalog (2025 approximate pricing, USD/month)
# Sources: Azure portal Pricing Calculator + values visible in reference PDFs
AZURE_FLAVORS: list[VMFlavor] = [
    VMFlavor(
        name="Standard_B2als_v2", cpu_cores=2, ram_gb=4,
        family="General Purpose",
        cost_payg_linux=24.53,
        cost_1yr_full_linux=14.60, cost_1yr_no_upfront_linux=16.06,
        cost_3yr_full_linux=10.39, cost_3yr_no_upfront_linux=10.42,
        cost_1yr_savings_full_linux=18.39, cost_1yr_savings_no_upfront_linux=18.39,
        cost_3yr_savings_full_linux=12.35, cost_3yr_savings_no_upfront_linux=10.42,
        windows_surcharge=35.04, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="Standard_B4als_v2", cpu_cores=4, ram_gb=8,
        family="General Purpose",
        cost_payg_linux=43.86,
        cost_1yr_full_linux=26.28, cost_1yr_no_upfront_linux=28.91,
        cost_3yr_full_linux=18.61, cost_3yr_no_upfront_linux=18.72,
        cost_1yr_savings_full_linux=32.58, cost_1yr_savings_no_upfront_linux=32.58,
        cost_3yr_savings_full_linux=21.85, cost_3yr_savings_no_upfront_linux=18.47,
        windows_surcharge=70.08, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="Standard_B4as_v2", cpu_cores=4, ram_gb=16,
        family="General Purpose",
        cost_payg_linux=76.01,
        cost_1yr_full_linux=47.45, cost_1yr_no_upfront_linux=52.19,
        cost_3yr_full_linux=33.60, cost_3yr_no_upfront_linux=33.81,
        cost_1yr_savings_full_linux=55.64, cost_1yr_savings_no_upfront_linux=55.64,
        cost_3yr_savings_full_linux=37.34, cost_3yr_savings_no_upfront_linux=31.57,
        windows_surcharge=70.08, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="Standard_B8als_v2", cpu_cores=8, ram_gb=16,
        family="General Purpose",
        cost_payg_linux=175.07,
        cost_1yr_full_linux=104.38, cost_1yr_no_upfront_linux=114.83,
        cost_3yr_full_linux=73.92, cost_3yr_no_upfront_linux=74.35,
        cost_1yr_savings_full_linux=130.10, cost_1yr_savings_no_upfront_linux=130.10,
        cost_3yr_savings_full_linux=87.38, cost_3yr_savings_no_upfront_linux=73.92,
        windows_surcharge=140.16, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="Standard_B16als_v2", cpu_cores=16, ram_gb=32,
        family="General Purpose",
        cost_payg_linux=350.14,
        cost_1yr_full_linux=208.76, cost_1yr_no_upfront_linux=229.66,
        cost_3yr_full_linux=147.84, cost_3yr_no_upfront_linux=148.70,
        cost_1yr_savings_full_linux=260.20, cost_1yr_savings_no_upfront_linux=260.20,
        cost_3yr_savings_full_linux=174.76, cost_3yr_savings_no_upfront_linux=147.84,
        windows_surcharge=280.32, rhel_surcharge=292.00,
    ),
    VMFlavor(
        name="Standard_B32als_v2", cpu_cores=32, ram_gb=64,
        family="General Purpose",
        cost_payg_linux=700.28,
        cost_1yr_full_linux=417.52, cost_1yr_no_upfront_linux=459.32,
        cost_3yr_full_linux=295.68, cost_3yr_no_upfront_linux=297.40,
        cost_1yr_savings_full_linux=520.40, cost_1yr_savings_no_upfront_linux=520.40,
        cost_3yr_savings_full_linux=349.52, cost_3yr_savings_no_upfront_linux=295.68,
        windows_surcharge=560.64, rhel_surcharge=584.00,
    ),
    VMFlavor(
        name="Standard_D2ls_v5", cpu_cores=2, ram_gb=4,
        family="General Purpose",
        cost_payg_linux=82.86,
        cost_1yr_full_linux=49.64, cost_1yr_no_upfront_linux=54.60,
        cost_3yr_full_linux=33.45, cost_3yr_no_upfront_linux=33.79,
        cost_1yr_savings_full_linux=65.05, cost_1yr_savings_no_upfront_linux=65.05,
        cost_3yr_savings_full_linux=48.33, cost_3yr_savings_no_upfront_linux=44.61,
        windows_surcharge=35.04, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="Standard_D4ls_v5", cpu_cores=4, ram_gb=8,
        family="General Purpose",
        cost_payg_linux=111.84,
        cost_1yr_full_linux=67.28, cost_1yr_no_upfront_linux=74.01,
        cost_3yr_full_linux=45.33, cost_3yr_no_upfront_linux=45.67,
        cost_1yr_savings_full_linux=83.15, cost_1yr_savings_no_upfront_linux=83.15,
        cost_3yr_savings_full_linux=54.60, cost_3yr_savings_no_upfront_linux=47.17,
        windows_surcharge=70.08, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="Standard_D8ls_v5", cpu_cores=8, ram_gb=16,
        family="General Purpose",
        cost_payg_linux=219.00,
        cost_1yr_full_linux=131.40, cost_1yr_no_upfront_linux=144.54,
        cost_3yr_full_linux=88.32, cost_3yr_no_upfront_linux=89.04,
        cost_1yr_savings_full_linux=162.74, cost_1yr_savings_no_upfront_linux=162.74,
        cost_3yr_savings_full_linux=109.14, cost_3yr_savings_no_upfront_linux=94.30,
        windows_surcharge=140.16, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="Standard_E8as_v5", cpu_cores=8, ram_gb=64,
        family="Memory Optimized",
        cost_payg_linux=299.29,
        cost_1yr_full_linux=187.44, cost_1yr_no_upfront_linux=201.17,
        cost_3yr_full_linux=130.10, cost_3yr_no_upfront_linux=130.10,
        cost_1yr_savings_full_linux=223.75, cost_1yr_savings_no_upfront_linux=223.75,
        cost_3yr_savings_full_linux=156.20, cost_3yr_savings_no_upfront_linux=125.39,
        windows_surcharge=140.16, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="Standard_E16as_v5", cpu_cores=16, ram_gb=128,
        family="Memory Optimized",
        cost_payg_linux=598.58,
        cost_1yr_full_linux=374.88, cost_1yr_no_upfront_linux=402.34,
        cost_3yr_full_linux=260.20, cost_3yr_no_upfront_linux=260.20,
        cost_1yr_savings_full_linux=447.50, cost_1yr_savings_no_upfront_linux=447.50,
        cost_3yr_savings_full_linux=312.40, cost_3yr_savings_no_upfront_linux=250.78,
        windows_surcharge=280.32, rhel_surcharge=292.00,
    ),
    VMFlavor(
        name="Standard_F4s_v2", cpu_cores=4, ram_gb=8,
        family="Compute Optimized",
        cost_payg_linux=169.44,
        cost_1yr_full_linux=101.66, cost_1yr_no_upfront_linux=111.83,
        cost_3yr_full_linux=68.40, cost_3yr_no_upfront_linux=68.88,
        cost_1yr_savings_full_linux=125.88, cost_1yr_savings_no_upfront_linux=125.88,
        cost_3yr_savings_full_linux=84.72, cost_3yr_savings_no_upfront_linux=68.40,
        windows_surcharge=70.08, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="Standard_F8s_v2", cpu_cores=8, ram_gb=16,
        family="Compute Optimized",
        cost_payg_linux=338.88,
        cost_1yr_full_linux=203.32, cost_1yr_no_upfront_linux=223.66,
        cost_3yr_full_linux=136.80, cost_3yr_no_upfront_linux=137.76,
        cost_1yr_savings_full_linux=251.76, cost_1yr_savings_no_upfront_linux=251.76,
        cost_3yr_savings_full_linux=169.44, cost_3yr_savings_no_upfront_linux=136.80,
        windows_surcharge=140.16, rhel_surcharge=146.00,
    ),
]

# ─── AWS EC2 Flavor Catalog ───────────────────────────────────────────────────

AWS_FLAVORS: list[VMFlavor] = [
    VMFlavor(
        name="t3.small", cpu_cores=2, ram_gb=2,
        family="General Purpose",
        cost_payg_linux=15.18,
        cost_1yr_full_linux=9.22, cost_1yr_no_upfront_linux=10.00,
        cost_3yr_full_linux=6.43, cost_3yr_no_upfront_linux=6.50,
        windows_surcharge=31.39, rhel_surcharge=60.00,
    ),
    VMFlavor(
        name="t3.medium", cpu_cores=2, ram_gb=4,
        family="General Purpose",
        cost_payg_linux=30.37,
        cost_1yr_full_linux=18.47, cost_1yr_no_upfront_linux=20.15,
        cost_3yr_full_linux=12.89, cost_3yr_no_upfront_linux=13.00,
        windows_surcharge=62.78, rhel_surcharge=60.00,
    ),
    VMFlavor(
        name="t3.large", cpu_cores=2, ram_gb=8,
        family="General Purpose",
        cost_payg_linux=60.74,
        cost_1yr_full_linux=36.94, cost_1yr_no_upfront_linux=40.30,
        cost_3yr_full_linux=25.78, cost_3yr_no_upfront_linux=26.00,
        windows_surcharge=125.56, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="m6i.large", cpu_cores=2, ram_gb=8,
        family="General Purpose",
        cost_payg_linux=70.08,
        cost_1yr_full_linux=42.34, cost_1yr_no_upfront_linux=46.57,
        cost_3yr_full_linux=28.61, cost_3yr_no_upfront_linux=29.20,
        windows_surcharge=125.56, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="m6i.xlarge", cpu_cores=4, ram_gb=16,
        family="General Purpose",
        cost_payg_linux=140.16,
        cost_1yr_full_linux=84.68, cost_1yr_no_upfront_linux=93.14,
        cost_3yr_full_linux=57.22, cost_3yr_no_upfront_linux=58.40,
        windows_surcharge=251.12, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="m6i.2xlarge", cpu_cores=8, ram_gb=32,
        family="General Purpose",
        cost_payg_linux=280.32,
        cost_1yr_full_linux=169.36, cost_1yr_no_upfront_linux=186.28,
        cost_3yr_full_linux=114.44, cost_3yr_no_upfront_linux=116.80,
        windows_surcharge=502.24, rhel_surcharge=292.00,
    ),
    VMFlavor(
        name="r6i.large", cpu_cores=2, ram_gb=16,
        family="Memory Optimized",
        cost_payg_linux=94.17,
        cost_1yr_full_linux=57.76, cost_1yr_no_upfront_linux=62.54,
        cost_3yr_full_linux=39.42, cost_3yr_no_upfront_linux=39.88,
        windows_surcharge=125.56, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="r6i.xlarge", cpu_cores=4, ram_gb=32,
        family="Memory Optimized",
        cost_payg_linux=188.34,
        cost_1yr_full_linux=115.52, cost_1yr_no_upfront_linux=125.08,
        cost_3yr_full_linux=78.84, cost_3yr_no_upfront_linux=79.76,
        windows_surcharge=251.12, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="r6i.2xlarge", cpu_cores=8, ram_gb=64,
        family="Memory Optimized",
        cost_payg_linux=376.68,
        cost_1yr_full_linux=231.04, cost_1yr_no_upfront_linux=250.16,
        cost_3yr_full_linux=157.68, cost_3yr_no_upfront_linux=159.52,
        windows_surcharge=502.24, rhel_surcharge=292.00,
    ),
    VMFlavor(
        name="c6i.large", cpu_cores=2, ram_gb=4,
        family="Compute Optimized",
        cost_payg_linux=62.42,
        cost_1yr_full_linux=38.33, cost_1yr_no_upfront_linux=41.62,
        cost_3yr_full_linux=26.28, cost_3yr_no_upfront_linux=26.57,
        windows_surcharge=62.78, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="c6i.xlarge", cpu_cores=4, ram_gb=8,
        family="Compute Optimized",
        cost_payg_linux=124.84,
        cost_1yr_full_linux=76.66, cost_1yr_no_upfront_linux=83.24,
        cost_3yr_full_linux=52.56, cost_3yr_no_upfront_linux=53.14,
        windows_surcharge=125.56, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="c6i.2xlarge", cpu_cores=8, ram_gb=16,
        family="Compute Optimized",
        cost_payg_linux=249.68,
        cost_1yr_full_linux=153.32, cost_1yr_no_upfront_linux=166.48,
        cost_3yr_full_linux=105.12, cost_3yr_no_upfront_linux=106.28,
        windows_surcharge=251.12, rhel_surcharge=146.00,
    ),
]

# ─── GCP Flavor Catalog ───────────────────────────────────────────────────────

GCP_FLAVORS: list[VMFlavor] = [
    VMFlavor(
        name="n2-standard-2", cpu_cores=2, ram_gb=8,
        family="General Purpose",
        cost_payg_linux=58.30,
        cost_1yr_full_linux=40.81, cost_1yr_no_upfront_linux=44.89,
        cost_3yr_full_linux=29.15, cost_3yr_no_upfront_linux=29.15,
        windows_surcharge=100.00, rhel_surcharge=73.00,
    ),
    VMFlavor(
        name="n2-standard-4", cpu_cores=4, ram_gb=16,
        family="General Purpose",
        cost_payg_linux=116.60,
        cost_1yr_full_linux=81.62, cost_1yr_no_upfront_linux=89.78,
        cost_3yr_full_linux=58.30, cost_3yr_no_upfront_linux=58.30,
        windows_surcharge=200.00, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="n2-standard-8", cpu_cores=8, ram_gb=32,
        family="General Purpose",
        cost_payg_linux=233.20,
        cost_1yr_full_linux=163.24, cost_1yr_no_upfront_linux=179.56,
        cost_3yr_full_linux=116.60, cost_3yr_no_upfront_linux=116.60,
        windows_surcharge=400.00, rhel_surcharge=292.00,
    ),
    VMFlavor(
        name="n2-highmem-4", cpu_cores=4, ram_gb=32,
        family="Memory Optimized",
        cost_payg_linux=161.94,
        cost_1yr_full_linux=113.36, cost_1yr_no_upfront_linux=124.69,
        cost_3yr_full_linux=80.97, cost_3yr_no_upfront_linux=80.97,
        windows_surcharge=200.00, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="n2-highmem-8", cpu_cores=8, ram_gb=64,
        family="Memory Optimized",
        cost_payg_linux=323.88,
        cost_1yr_full_linux=226.72, cost_1yr_no_upfront_linux=249.38,
        cost_3yr_full_linux=161.94, cost_3yr_no_upfront_linux=161.94,
        windows_surcharge=400.00, rhel_surcharge=292.00,
    ),
    VMFlavor(
        name="c2-standard-4", cpu_cores=4, ram_gb=16,
        family="Compute Optimized",
        cost_payg_linux=134.40,
        cost_1yr_full_linux=94.08, cost_1yr_no_upfront_linux=103.49,
        cost_3yr_full_linux=67.20, cost_3yr_no_upfront_linux=67.20,
        windows_surcharge=200.00, rhel_surcharge=146.00,
    ),
    VMFlavor(
        name="c2-standard-8", cpu_cores=8, ram_gb=32,
        family="Compute Optimized",
        cost_payg_linux=268.80,
        cost_1yr_full_linux=188.16, cost_1yr_no_upfront_linux=206.98,
        cost_3yr_full_linux=134.40, cost_3yr_no_upfront_linux=134.40,
        windows_surcharge=400.00, rhel_surcharge=292.00,
    ),
]

# ─── On-Prem / OpenStack Flavor Catalog ─────────────────────────────────────

ONPREM_FLAVORS: list[VMFlavor] = [
    VMFlavor(
        name="onprem.small", cpu_cores=2, ram_gb=4,
        family="General Purpose",
        cost_payg_linux=0.0,
        cost_1yr_full_linux=0.0, cost_1yr_no_upfront_linux=0.0,
        cost_3yr_full_linux=0.0, cost_3yr_no_upfront_linux=0.0,
    ),
    VMFlavor(
        name="onprem.medium", cpu_cores=4, ram_gb=8,
        family="General Purpose",
        cost_payg_linux=0.0,
        cost_1yr_full_linux=0.0, cost_1yr_no_upfront_linux=0.0,
        cost_3yr_full_linux=0.0, cost_3yr_no_upfront_linux=0.0,
    ),
    VMFlavor(
        name="onprem.large", cpu_cores=8, ram_gb=16,
        family="General Purpose",
        cost_payg_linux=0.0,
        cost_1yr_full_linux=0.0, cost_1yr_no_upfront_linux=0.0,
        cost_3yr_full_linux=0.0, cost_3yr_no_upfront_linux=0.0,
    ),
    VMFlavor(
        name="onprem.xlarge", cpu_cores=16, ram_gb=32,
        family="General Purpose",
        cost_payg_linux=0.0,
        cost_1yr_full_linux=0.0, cost_1yr_no_upfront_linux=0.0,
        cost_3yr_full_linux=0.0, cost_3yr_no_upfront_linux=0.0,
    ),
    VMFlavor(
        name="onprem.memory-large", cpu_cores=8, ram_gb=64,
        family="Memory Optimized",
        cost_payg_linux=0.0,
        cost_1yr_full_linux=0.0, cost_1yr_no_upfront_linux=0.0,
        cost_3yr_full_linux=0.0, cost_3yr_no_upfront_linux=0.0,
    ),
]

# ─── OCI (Oracle Cloud) flavor catalog ────────────────────────────────────────
# OCI's real billing model prices flexible shapes per-OCPU + per-GB-memory
# rather than a flat rate per fixed SKU (see services/live_pricing.py's
# oci_hourly_cost() for the full explanation and services/live_pricing.py's
# fetch_oci_prices() for how live rates are obtained). These monthly figures
# are pre-computed at the real observed E5.Flex general-purpose rates
# (~$0.025/OCPU-hr, ~$0.0015/GB-hr) x 730 hours/month — "cpu_cores" is treated
# as OCPU count directly, consistent with services/tco_rightsizing.py.
# No published reservation/savings-plan tiers exist for OCI flex shapes in the
# same shape as Azure/AWS, so only the PAYG-equivalent tier is populated;
# reservation fields are left at the PAYG rate rather than 0 so downstream
# code that blindly picks a "1yr"/"3yr" plan doesn't silently price OCI at $0.
_OCI_OCPU_HOURLY = 0.025
_OCI_MEM_GB_HOURLY = 0.0015


# Function: _oci_monthly
def _oci_monthly(cpu_cores: int, ram_gb: float) -> float:
    return round((cpu_cores * _OCI_OCPU_HOURLY + ram_gb * _OCI_MEM_GB_HOURLY) * 730, 2)


OCI_FLAVORS: list[VMFlavor] = [
    VMFlavor(
        name=f"VM.Standard.E5.Flex-{cpu}-{ram}", cpu_cores=cpu, ram_gb=ram,
        family="Memory Optimized" if ram / cpu >= 6 else "General Purpose",
        cost_payg_linux=_oci_monthly(cpu, ram),
        cost_1yr_full_linux=_oci_monthly(cpu, ram), cost_1yr_no_upfront_linux=_oci_monthly(cpu, ram),
        cost_3yr_full_linux=_oci_monthly(cpu, ram), cost_3yr_no_upfront_linux=_oci_monthly(cpu, ram),
    )
    for cpu, ram in [(2, 8), (2, 16), (4, 16), (4, 32), (8, 32), (8, 64), (16, 64), (16, 128)]
]

# ─── Provider → Catalog mapping ───────────────────────────────────────────────

FLAVOR_CATALOG: dict[str, list[VMFlavor]] = {
    "azure": AZURE_FLAVORS,
    "aws": AWS_FLAVORS,
    "gcp": GCP_FLAVORS,
    "oci": OCI_FLAVORS,
    "onprem": ONPREM_FLAVORS,
}

# ─── Pricing plan names ───────────────────────────────────────────────────────

AZURE_PRICING_PLANS = [
    "Pay As You Go",
    "1 Year Reserved Full Upfront",
    "1 Year Reserved No Upfront",
    "1 Year Compute Savings Full Upfront",
    "1 Year Compute Savings No Upfront",
    "3 Year Reserved Full Upfront",
    "3 Year Reserved No Upfront",
    "3 Year Compute Savings Full Upfront",
    "3 Year Compute Savings No Upfront",
]

AWS_PRICING_PLANS = [
    "Pay As You Go",
    "1 Year Reserved Full Upfront",
    "1 Year Reserved No Upfront",
    "3 Year Reserved Full Upfront",
    "3 Year Reserved No Upfront",
]

GCP_PRICING_PLANS = [
    "Pay As You Go",
    "1 Year Committed Use Full Upfront",
    "1 Year Committed Use No Upfront",
    "3 Year Committed Use Full Upfront",
    "3 Year Committed Use No Upfront",
]

ONPREM_PRICING_PLANS: list[str] = []

PROVIDER_PLANS: dict[str, list[str]] = {
    "azure": AZURE_PRICING_PLANS,
    "aws": AWS_PRICING_PLANS,
    "gcp": GCP_PRICING_PLANS,
    "onprem": ONPREM_PRICING_PLANS,
}

# ─── Flavor matching ──────────────────────────────────────────────────────────

# Function: _workload_family
def _workload_family(workload_types: set[str]) -> str:
    """Determine preferred flavor family from workload type set."""
    if "db" in workload_types:
        return "Memory Optimized"
    if "compute" in workload_types:
        return "Compute Optimized"
    return "General Purpose"


# Function: find_equivalence_flavor
def find_equivalence_flavor(
    cpu_cores: int,
    ram_gb: float,
    provider: str,
    preferred_family: str = "General Purpose",
) -> Optional[VMFlavor]:
    """Find the best matching flavor (>= server spec, closest size)."""
    catalog = FLAVOR_CATALOG.get(provider, AZURE_FLAVORS)
    # Filter: must cover the server's CPU and RAM
    candidates = [
        f for f in catalog
        if f.cpu_cores >= cpu_cores and f.ram_gb >= ram_gb
    ]
    if not candidates:
        # Fallback: largest available
        candidates = catalog
    # Prefer family match, then sort by (cpu, ram) to find closest
    family_candidates = [f for f in candidates if f.family == preferred_family]
    pool = family_candidates if family_candidates else candidates
    return min(pool, key=lambda f: (f.cpu_cores - cpu_cores) + (f.ram_gb - ram_gb))


# Function: find_best_match_flavor
def find_best_match_flavor(
    cpu_cores: int,
    ram_gb: float,
    provider: str,
    utilization_band: str = "unknown",
    preferred_family: str = "General Purpose",
) -> Optional[VMFlavor]:
    """Find the right-sized (best match) flavor factoring in utilization."""
    # Right-size: underutilized → halve resources; others keep the same
    is_underutil = utilization_band in ("underutilized", "unknown")
    if is_underutil:
        target_cpu = max(2, math.ceil(cpu_cores * 0.5))
        target_ram = max(4.0, ram_gb * 0.5)
    else:
        target_cpu = cpu_cores
        target_ram = ram_gb
    return find_equivalence_flavor(target_cpu, target_ram, provider, preferred_family)


# ─── Storage tier catalog ─────────────────────────────────────────────────────

@dataclass
class StorageTier:
    cloud: str
    storage_type: str               # Standard HDD / Premium SSD / Ultra SSD
    tier_label: str                 # e.g. "Standard Managed HDD (LRS)"
    size_gb: int
    iops: int
    throughput_mbps: int
    cost_per_disk_month: float
    redundancy: str = "LRS"


AZURE_STORAGE_TIERS: list[StorageTier] = [
    StorageTier("Azure", "Standard HDD", "Standard Managed HDD (LRS)", 64,   500,  60,   3.01),
    StorageTier("Azure", "Standard HDD", "Standard Managed HDD (LRS)", 128,  500,  60,   5.89),
    StorageTier("Azure", "Standard HDD", "Standard Managed HDD (LRS)", 256,  500,  60,  11.33),
    StorageTier("Azure", "Standard HDD", "Standard Managed HDD (LRS)", 512,  500,  60,  21.76),
    StorageTier("Azure", "Standard HDD", "Standard Managed HDD (LRS)", 1024, 500,  60,  40.96),
    StorageTier("Azure", "Standard SSD", "Standard Managed SSD (LRS)", 128,  500, 100,   9.60),
    StorageTier("Azure", "Standard SSD", "Standard Managed SSD (LRS)", 256,  500, 125,  15.36),
    StorageTier("Azure", "Premium SSD",  "Premium Managed SSD (LRS)",  128,  500, 100,  19.71),
    StorageTier("Azure", "Premium SSD",  "Premium Managed SSD (LRS)",  256, 1100, 125,  38.01),
    StorageTier("Azure", "Premium SSD",  "Premium Managed SSD (LRS)",  512, 2300, 150,  68.27),
    StorageTier("Azure", "Ultra SSD",    "Ultra Managed SSD (LRS)",    1024,16000,2000, 110.08),
]

AWS_STORAGE_TIERS: list[StorageTier] = [
    StorageTier("AWS", "Standard HDD", "EBS st1 HDD",  125,  500,  40,   5.75),
    StorageTier("AWS", "Standard HDD", "EBS sc1 HDD",  125,  250,  12,   2.00),
    StorageTier("AWS", "General SSD",  "EBS gp3 SSD",  100, 3000, 125,   8.00),
    StorageTier("AWS", "General SSD",  "EBS gp3 SSD",  500, 3000, 125,  40.00),
    StorageTier("AWS", "General SSD",  "EBS gp3 SSD", 1024, 3000, 250,  81.92),
    StorageTier("AWS", "Premium SSD",  "EBS io2 SSD",  128,16000, 500,  24.73),
    StorageTier("AWS", "Premium SSD",  "EBS io2 SSD",  512,64000,1000,  98.92),
]

GCP_STORAGE_TIERS: list[StorageTier] = [
    StorageTier("GCP", "Standard HDD", "Persistent Disk Standard",  100,  750, 120,   4.00),
    StorageTier("GCP", "Standard HDD", "Persistent Disk Standard",  500,  750, 120,  20.00),
    StorageTier("GCP", "Balanced SSD", "Persistent Disk Balanced",  100, 3000, 240,  10.00),
    StorageTier("GCP", "Balanced SSD", "Persistent Disk Balanced",  500, 3000, 240,  50.00),
    StorageTier("GCP", "Premium SSD",  "Persistent Disk SSD",       100, 6000, 480,  17.00),
    StorageTier("GCP", "Premium SSD",  "Persistent Disk SSD",       500, 6000, 480,  85.00),
]

ONPREM_STORAGE_TIERS: list[StorageTier] = [
    StorageTier("OnPrem", "Standard HDD", "Local SATA HDD",   500,  200,  80,   0.0),
    StorageTier("OnPrem", "Standard HDD", "Local SATA HDD",  1000,  200,  80,   0.0),
    StorageTier("OnPrem", "Standard SSD", "Local NVMe SSD",   512, 4000, 500,   0.0),
    StorageTier("OnPrem", "Standard SSD", "Local NVMe SSD",  1024, 4000, 500,   0.0),
    StorageTier("OnPrem", "NAS",          "Network Attached Storage", 2048, 500, 125, 0.0),
    StorageTier("OnPrem", "SAN",          "Storage Area Network",     2048, 5000, 500, 0.0),
]

PROVIDER_STORAGE_TIERS: dict[str, list[StorageTier]] = {
    "azure": AZURE_STORAGE_TIERS,
    "aws": AWS_STORAGE_TIERS,
    "gcp": GCP_STORAGE_TIERS,
    "onprem": ONPREM_STORAGE_TIERS,
}


# Function: _workload_requires_premium_ssd
def _workload_requires_premium_ssd(workload_types: set[str]) -> bool:
    """DB and app servers benefit from Premium SSD."""
    return bool(workload_types & {"db", "app", "mail", "queue"})


# Function: find_storage_tier
def find_storage_tier(
    required_gb: float,
    provider: str,
    workload_types: set[str] | None = None,
) -> StorageTier:
    """Choose the best storage tier for a given disk size and workload type."""
    catalog = PROVIDER_STORAGE_TIERS.get(provider, AZURE_STORAGE_TIERS)
    wl = workload_types or set()
    prefer_premium = _workload_requires_premium_ssd(wl)

    if prefer_premium:
        premium = [t for t in catalog if "Premium" in t.storage_type or "SSD" in t.storage_type]
    else:
        premium = [t for t in catalog if "HDD" in t.storage_type or "Standard" in t.storage_type]

    pool = premium if premium else catalog
    # Pick smallest tier that covers the required GB
    suitable = [t for t in pool if t.size_gb >= required_gb]
    if suitable:
        return min(suitable, key=lambda t: t.size_gb)
    # Fall back to largest available
    return max(pool, key=lambda t: t.size_gb)


# ─── PaaS service pricing ─────────────────────────────────────────────────────

@dataclass
class PaaSService:
    cloud_provider: str
    workload_name: str      # MySQL, PostgreSQL, ApacheTomcat, etc.
    workload_type: str      # db / web / app
    paas_service: str       # e.g. "Azure Database for MySQL"
    paas_tier: str          # e.g. "Business Critical"
    paas_config: str        # human-readable spec
    cost_month: float


AZURE_PAAS_SERVICES: list[PaaSService] = [
    PaaSService("Azure", "MySQL", "db",
                "Azure Database for MySQL",
                "Business Critical",
                "8 core, 300.0 GB, 200 GB Backup, Business Critical", 743.0),
    PaaSService("Azure", "PostgreSQL", "db",
                "Azure Database for PostgreSQL",
                "Business Critical",
                "8 core, 300.0 GB, 200 GB Backup, Business Critical", 762.0),
    PaaSService("Azure", "MSSQL", "db",
                "Azure SQL Database",
                "Business Critical",
                "8 vCores, 20.4 GB RAM, Business Critical", 1092.0),
    PaaSService("Azure", "MongoDB", "db",
                "Azure Cosmos DB (MongoDB API)",
                "Serverless",
                "Serverless, 1 RU/s baseline", 0.25),
    PaaSService("Azure", "Redis", "cache",
                "Azure Cache for Redis",
                "Standard C2",
                "Standard C2: 6 GB, HA replicated", 97.82),
    PaaSService("Azure", "Kafka", "queue",
                "Azure Event Hubs",
                "Standard 1 TU",
                "1 Throughput Unit, Standard tier", 9.82),
    PaaSService("Azure", "RabbitMQ", "queue",
                "Azure Service Bus",
                "Standard",
                "Standard tier, 1M operations/month", 10.00),
    PaaSService("Azure", "Elasticsearch", "search",
                "Azure Elastic Cloud (Elasticsearch)",
                "Standard 2048 MB",
                "2 GB RAM Deployment, Standard", 45.60),
    PaaSService("Azure", "ApacheTomcat", "web",
                "App Service",
                "Basic B3",
                "B3: 4 Core, 7 GB RAM, 10 GB Storage, Basic", 219.0),
    PaaSService("Azure", "ApacheTomcat", "app",
                "App Service",
                "Basic B3",
                "B3: 4 Core, 7 GB RAM, 10 GB Storage, Basic", 219.0),
    PaaSService("Azure", "nginx", "web",
                "App Service",
                "Basic B2",
                "B2: 2 Core, 3.5 GB RAM, 10 GB Storage, Basic", 109.50),
    PaaSService("Azure", "IIS", "web",
                "App Service",
                "Standard S2",
                "S2: 2 Core, 3.5 GB RAM, 50 GB Storage, Standard", 146.00),
    PaaSService("Azure", "Keycloak", "app",
                "Azure App Service",
                "Standard S2",
                "S2: 2 Core, 3.5 GB RAM, 50 GB Storage, Standard", 146.00),
]

AWS_PAAS_SERVICES: list[PaaSService] = [
    PaaSService("AWS", "MySQL", "db",
                "Amazon RDS for MySQL",
                "db.m6i.2xlarge Multi-AZ",
                "8 vCPU, 32 GB RAM, Multi-AZ deployment, 300 GB storage", 810.00),
    PaaSService("AWS", "PostgreSQL", "db",
                "Amazon RDS for PostgreSQL",
                "db.m6i.2xlarge Multi-AZ",
                "8 vCPU, 32 GB RAM, Multi-AZ deployment, 300 GB storage", 810.00),
    PaaSService("AWS", "MSSQL", "db",
                "Amazon RDS for SQL Server",
                "db.m6i.2xlarge Multi-AZ",
                "8 vCPU, 32 GB RAM, Multi-AZ deployment, 100 GB storage", 1220.00),
    PaaSService("AWS", "Redis", "cache",
                "Amazon ElastiCache for Redis",
                "cache.r6g.large",
                "2 vCPU, 13.07 GB RAM, single-node", 156.00),
    PaaSService("AWS", "Kafka", "queue",
                "Amazon MSK (Managed Kafka)",
                "kafka.m5.large 3-broker",
                "3 brokers, kafka.m5.large, 100 GB EBS each", 397.20),
    PaaSService("AWS", "ApacheTomcat", "web",
                "AWS Elastic Beanstalk (App Service)",
                "t3.large",
                "t3.large, auto-scaling, load-balanced", 60.74),
    PaaSService("AWS", "nginx", "web",
                "AWS Elastic Beanstalk",
                "t3.medium",
                "t3.medium, auto-scaling enabled", 30.37),
]

GCP_PAAS_SERVICES: list[PaaSService] = [
    PaaSService("GCP", "MySQL", "db",
                "Cloud SQL for MySQL",
                "db-n2-highmem-4 HA",
                "4 vCPU, 32 GB RAM, HA, 300 GB SSD", 734.00),
    PaaSService("GCP", "PostgreSQL", "db",
                "Cloud SQL for PostgreSQL",
                "db-n2-highmem-4 HA",
                "4 vCPU, 32 GB RAM, HA, 300 GB SSD", 734.00),
    PaaSService("GCP", "Redis", "cache",
                "Memorystore for Redis",
                "Standard 5 GB",
                "Standard tier, 5 GB, HA replica", 135.00),
    PaaSService("GCP", "Kafka", "queue",
                "Google Cloud Pub/Sub",
                "Standard",
                "Standard throughput, 1 TB/month", 40.00),
    PaaSService("GCP", "ApacheTomcat", "web",
                "Google App Engine (Standard)",
                "F4",
                "F4: 2.4 GHz, 512 MB RAM, Standard environment", 48.00),
]

PROVIDER_PAAS_SERVICES: dict[str, list[PaaSService]] = {
    "azure": AZURE_PAAS_SERVICES,
    "aws": AWS_PAAS_SERVICES,
    "gcp": GCP_PAAS_SERVICES,
}


# Function: find_paas_service
def find_paas_service(
    workload_name: str,
    workload_type: str,
    provider: str,
) -> Optional[PaaSService]:
    """Look up the best PaaS service match for a workload on a given cloud provider."""
    catalog = PROVIDER_PAAS_SERVICES.get(provider, AZURE_PAAS_SERVICES)
    wl_lower = workload_name.lower()
    for svc in catalog:
        if svc.workload_name.lower() in wl_lower or wl_lower in svc.workload_name.lower():
            if svc.workload_type == workload_type or not workload_type:
                return svc
    # Try partial name match
    for svc in catalog:
        if svc.workload_name.lower() in wl_lower:
            return svc
    return None


# ─── VMware / OpenStack / AVS capacity planning ──────────────────────────────

@dataclass
class VMwareFlavor:
    name: str                   # e.g. AV36P
    cpu_cores: int              # per host
    ram_gb: int                 # per host
    nvme_tb: float              # NVMe/vSAN per host
    features: list[str]         # NSX-T, vSphere, vSAN, HCX
    cost_payg_month: float
    cost_1yr_month: float
    cost_3yr_month: float
    cost_5yr_month: float


AVS_FLAVORS: list[VMwareFlavor] = [
    VMwareFlavor(
        name="AV36", cpu_cores=36, ram_gb=576, nvme_tb=15.36,
        features=["NSX-T", "vSphere", "vSAN", "HCX Advanced"],
        cost_payg_month=7686.00, cost_1yr_month=5579.00,
        cost_3yr_month=4120.00, cost_5yr_month=3268.00,
    ),
    VMwareFlavor(
        name="AV36P", cpu_cores=36, ram_gb=768, nvme_tb=19.20,
        features=["NSX-T", "vSphere", "vSAN", "HCX Advanced"],
        cost_payg_month=9016.00, cost_1yr_month=6559.00,
        cost_3yr_month=4846.00, cost_5yr_month=3842.00,
    ),
    VMwareFlavor(
        name="AV52", cpu_cores=52, ram_gb=1536, nvme_tb=38.40,
        features=["NSX-T", "vSphere", "vSAN", "HCX Advanced"],
        cost_payg_month=13524.00, cost_1yr_month=9839.00,
        cost_3yr_month=7268.00, cost_5yr_month=5762.00,
    ),
]


@dataclass
class OpenStackFlavor:
    name: str
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    cost_per_vm_month: float   # approximate compute cost (self-hosted = HW depreciation)


OPENSTACK_FLAVORS: list[OpenStackFlavor] = [
    OpenStackFlavor("m1.small",   1,  2,   20, 0.0),
    OpenStackFlavor("m1.medium",  2,  4,   40, 0.0),
    OpenStackFlavor("m1.large",   4,  8,   80, 0.0),
    OpenStackFlavor("m1.xlarge",  8, 16,  160, 0.0),
    OpenStackFlavor("m1.2xlarge",16, 32,  320, 0.0),
    OpenStackFlavor("r1.large",   4, 16,   80, 0.0),
    OpenStackFlavor("r1.xlarge",  8, 32,  160, 0.0),
    OpenStackFlavor("r1.2xlarge",16, 64,  320, 0.0),
]


# Function: recommend_avs_cluster
def recommend_avs_cluster(
    total_cpu: int,
    total_ram_gb: float,
    total_storage_tb: float,
    flavor_name: str = "AV36P",
) -> dict:
    """
    Recommend an AVS cluster size for the given workload totals.
    Returns host count, cluster total resources, and multi-year pricing.
    """
    flavor = next((f for f in AVS_FLAVORS if f.name == flavor_name), AVS_FLAVORS[1])
    # Safety buffer: 30% overhead for HA + overhead
    min_cpu = math.ceil(total_cpu * 1.3 / flavor.cpu_cores)
    min_ram = math.ceil(total_ram_gb * 1.3 / flavor.ram_gb)
    min_stor = math.ceil(total_storage_tb * 1.3 / flavor.nvme_tb)
    host_count = max(3, max(min_cpu, min_ram, min_stor))  # AVS minimum 3 hosts

    return {
        "flavor": flavor.name,
        "host_count": host_count,
        "cluster_count": math.ceil(host_count / 16),   # max 16 hosts/cluster
        "total_cpu_cores": host_count * flavor.cpu_cores,
        "total_ram_gb": host_count * flavor.ram_gb,
        "total_nvme_tb": round(host_count * flavor.nvme_tb, 2),
        "features": flavor.features,
        "pricing": {
            "pay_as_you_go_month": round(host_count * flavor.cost_payg_month, 2),
            "1yr_reserved_month":  round(host_count * flavor.cost_1yr_month, 2),
            "3yr_reserved_month":  round(host_count * flavor.cost_3yr_month, 2),
            "5yr_reserved_month":  round(host_count * flavor.cost_5yr_month, 2),
        },
    }


# Function: recommend_openstack_cluster
def recommend_openstack_cluster(
    total_cpu: int,
    total_ram_gb: float,
    total_storage_tb: float,
) -> dict:
    """Recommend an OpenStack cluster node count using m1.xlarge nodes."""
    flavor = next(f for f in OPENSTACK_FLAVORS if f.name == "m1.xlarge")
    min_cpu  = math.ceil(total_cpu * 1.25 / flavor.cpu_cores)
    min_ram  = math.ceil(total_ram_gb * 1.25 / flavor.ram_gb)
    min_stor = math.ceil(total_storage_tb * 1024 * 1.25 / flavor.storage_gb)
    node_count = max(3, max(min_cpu, min_ram, min_stor))
    return {
        "flavor": flavor.name,
        "node_count": node_count,
        "total_cpu_cores": node_count * flavor.cpu_cores,
        "total_ram_gb": node_count * flavor.ram_gb,
        "total_storage_gb": node_count * flavor.storage_gb,
        "note": (
            f"Recommended OpenStack compute node count: {node_count} x {flavor.name} "
            "nodes for on-prem private cloud deployment."
        ),
    }


# ─── Kubernetes AKS / EKS / GKE node flavor selection ───────────────────────

# Function: recommend_kubernetes_node_flavor
def recommend_kubernetes_node_flavor(
    total_cpu_pods: float,
    total_ram_mb_pods: float,
    provider: str,
    node_os: str = "linux",
) -> VMFlavor:
    """Choose a Kubernetes node flavor sized for the given aggregate pod requests."""
    catalog = FLAVOR_CATALOG.get(provider, AZURE_FLAVORS)
    # Pods use ~70% of node capacity
    req_cpu = math.ceil(total_cpu_pods / 0.7)
    req_ram = math.ceil(total_ram_mb_pods / 1024 / 0.7)
    candidates = [f for f in catalog if f.cpu_cores >= req_cpu and f.ram_gb >= req_ram]
    if not candidates:
        candidates = catalog
    return min(candidates, key=lambda f: f.cost_payg_linux)


# ─── OS license type detection ───────────────────────────────────────────────

# Function: detect_license_type
def detect_license_type(os_name: str) -> str:
    """Return 'Windows-DC' / 'Windows-Std' / 'RHEL' / 'BYOL' / 'Included' / 'None'."""
    os_lower = (os_name or "").lower()
    if "windows" in os_lower:
        if "datacenter" in os_lower or "dc" in os_lower:
            return "Windows-DC"
        return "Windows-Std"
    if "red hat" in os_lower or "rhel" in os_lower:
        return "RHEL"
    if "suse" in os_lower or "sles" in os_lower:
        return "SUSE"
    return "None"   # Linux — no extra OS license cost


# Function: count_os_licenses
def count_os_licenses(servers: list) -> dict[str, int]:
    """Count OS licenses needed by type across a list of DiscoveredServer objects."""
    counts: dict[str, int] = {}
    for s in servers:
        lic = detect_license_type(getattr(s, "os_name", "") or "")
        if lic not in ("None", "Included"):
            counts[lic] = counts.get(lic, 0) + 1
    return counts


# Function: count_db_licenses
def count_db_licenses(servers: list) -> dict[str, int]:
    """Count DB licenses needed by type across a list of DiscoveredServer objects."""
    counts: dict[str, int] = {}
    for s in servers:
        for w in getattr(s, "workloads", []):
            wl_lower = (getattr(w, "name", "") or "").lower()
            if "mssql" in wl_lower or "sql server" in wl_lower:
                counts["MSSQL"] = counts.get("MSSQL", 0) + 1
            elif "oracle" in wl_lower:
                counts["Oracle"] = counts.get("Oracle", 0) + 1
    return counts
