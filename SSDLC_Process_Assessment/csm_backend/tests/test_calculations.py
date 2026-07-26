# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Unit tests for all calculation services.
# Date: 2026-03-20
# ---------------------------------------------------------------------------
"""
Unit tests for all calculation services.
Uses exact workbook default values - no HTTP, direct service instantiation.
"""
from __future__ import annotations

import sys
import os

# Ensure csm_backend root is on the path when running tests from any directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from decimal import Decimal
import pytest

from app.models.inputs import InputAssumptions
from app.models.vendor_spend import VendorSpendRecord
from app.models.tower_model import DEFAULT_TOWER_PARAMS
from app.services.workbook_parser_service import default_inputs
from app.services.input_assumption_service import InputAssumptionService
from app.services.vendor_spend_service import VendorSpendService
from app.services.tower_consolidation_service import TowerConsolidationService
from app.services.techm_growth_service import TechMGrowthService
from app.services.transformation_capacity_service import TransformationCapacityService
from app.services.vendor_heatmap_service import VendorHeatmapService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Function: inputs
@pytest.fixture
def inputs() -> InputAssumptions:
    """Exact workbook default inputs."""
    return default_inputs()


# Function: vendor_records
@pytest.fixture
def vendor_records() -> list[VendorSpendRecord]:
    """
    Minimal vendor dataset matching exact workbook tower totals:
      Applications:            18,900,000  (11 vendors)
      Infrastructure:           8,300,000  (9 vendors)
      Data & AI:                6,300,000  (7 vendors)
      Workplace/Productivity:   7,700,000  (2 vendors)
      Cross-Tower Labor:       15,900,000  (2 vendors)
      Other:                   18,300,000  (2 vendors)
      TOTAL:                   75,400,000
    """
    # Function: v
    def v(vendor, category, tower, spend):
        return VendorSpendRecord(
            vendor=vendor,
            spend_category=category,
            tower=tower,
            annual_spend=Decimal(str(spend)),
        )

    # Category targets:
    #   Talent:   40,800,000
    #   Software: 26,000,000
    #   Data:      8,600,000  (JD Power 2.5M + Others-Data AI 0.4M + rest in Infra/Data tower)
    # Tower targets must also be met exactly.
    #
    # Layout chosen to satisfy both constraints simultaneously:
    #   Apps (18.9M):  Talent 14.6M + Software 4.3M
    #   Infra (8.3M):  Talent 2.5M  + Software 5.8M
    #   Data&AI (6.3M): Data 2.9M   + Software 3.4M
    #   Workplace (7.7M): Software 7.7M
    #   CTL (15.9M):   Talent 15.9M
    #   Other (18.3M): Software 4.8M + Talent 5.7M + Data 7.8M
    #
    #   Talent  = 14.6 + 2.5 + 15.9 + 5.7 + 2.1  = 40.8  ✓
    #             (Apps) (Infra) (CTL) (Other) (remainder)
    #   Software= 4.3 + 5.8 + 3.4 + 7.7 + 4.8 = 26.0  ✓
    #   Data    = 2.9 + 7.8 = ... need 8.6 not in scope; simplify:
    #
    # Simplified to match exactly:
    #   Talent vendors total  = 40,800,000
    #   Software vendors total= 26,000,000
    #   Data vendors total    =  8,600,000
    #   Grand total           = 75,400,000  ✓
    #
    # Distribution:
    #   Applications (18.9M):
    #     Talent: Interra 6.2M, Blue Hill 3M, TechM 2.5M, Infosys 1.5M, Cognizant 1.4M = 14.6M
    #     Software: Salesforce 2.3M, SAP 2.0M = 4.3M  → total 18.9M ✓
    #   Infrastructure (8.3M):
    #     Talent: Wipro 2.5M = 2.5M
    #     Software: IBM 1.5M, Dell 1.0M, HPE 0.8M, NetApp 0.6M, Cisco 0.5M, Zscaler 0.5M, Others 0.9M = 5.8M → 8.3M ✓
    #   Data & AI (6.3M):
    #     Data: JD Power 2.5M, Others-Data 0.4M = 2.9M
    #     Software: Databricks 1.0M, Snowflake 0.8M, MS Fabric 0.7M, Palantir 0.5M, Alteryx 0.4M = 3.4M → 6.3M ✓
    #   Workplace (7.7M):
    #     Software: MS 6.1M, ServiceNow 1.6M = 7.7M ✓
    #   Cross-Tower Labor (15.9M):
    #     Talent: Manpower 15M, Others-CTL 0.9M = 15.9M ✓
    #   Other (18.3M):
    #     Talent: Others-Talent 5.7M, Gartner-Talent 2.1M = 7.8M
    #     Software: Others-SW 4.8M = 4.8M
    #     Data: IHS Markit 3.7M, Experian 2.0M, Polk 1.9M = 7.6M → … adjust
    #
    # Easiest correct split for Other (18.3M):
    #     Data: 5.7M  (IHS Markit 2.5M + S&P 1.7M + Experian 1.5M)
    #     Talent: 7.8M (Others-Talent 7.8M)
    #     Software: 4.8M (Others-SW 4.8M)
    #   total = 5.7 + 7.8 + 4.8 = 18.3 ✓
    #
    # Category totals check:
    #   Talent  = 14.6(Apps) + 2.5(Infra) + 15.9(CTL) + 7.8(Other) = 40.8  ✓
    #   Software= 4.3(Apps) + 5.8(Infra) + 3.4(D&AI) + 7.7(WP) + 4.8(Other) = 26.0  ✓
    #   Data    = 2.9(D&AI) + 5.7(Other) = 8.6
    #   TOTAL   = 40.8 + 26.0 + 8.6 = 75.4  ✓

    records = [
        # --- Applications (total 18,900,000 | 11 vendors) ---
        # Talent: 6.2+3.0+2.5+0.8+0.7+0.6+0.5+0.3 = 14.6M
        # Software: 2.3+2.0 = 4.3M
        v("Interra IT",              "Talent",   "Applications",           6_200_000),
        v("Blue Hill",               "Talent",   "Applications",           3_000_000),
        v("Tech Mahindra",           "Talent",   "Applications",           2_500_000),
        v("Infosys",                 "Talent",   "Applications",             800_000),
        v("Cognizant",               "Talent",   "Applications",             700_000),
        v("Capgemini",               "Talent",   "Applications",             600_000),
        v("Accenture",               "Talent",   "Applications",             500_000),
        v("HCLTech",                 "Talent",   "Applications",             300_000),
        v("Salesforce",              "Software", "Applications",           2_300_000),
        v("SAP",                     "Software", "Applications",           1_700_000),
        v("Others - Apps SW",        "Software", "Applications",             300_000),
        # --- Infrastructure (total 8,300,000) ---
        v("Wipro",                   "Talent",   "Infrastructure",         2_500_000),
        v("IBM",                     "Software", "Infrastructure",         1_500_000),
        v("Dell Technologies",       "Software", "Infrastructure",         1_000_000),
        v("HPE",                     "Software", "Infrastructure",           800_000),
        v("NetApp",                  "Software", "Infrastructure",           600_000),
        v("Cisco",                   "Software", "Infrastructure",           500_000),
        v("Zscaler",                 "Software", "Infrastructure",           500_000),
        v("Others - Infra SW",       "Software", "Infrastructure",           900_000),
        # --- Data & AI (total 6,300,000) ---
        v("JD Power",                "Data",     "Data & AI",              2_500_000),
        v("Others - Data AI",        "Data",     "Data & AI",                400_000),
        v("Databricks",              "Software", "Data & AI",              1_000_000),
        v("Snowflake",               "Software", "Data & AI",                800_000),
        v("Microsoft Fabric",        "Software", "Data & AI",                700_000),
        v("Palantir",                "Software", "Data & AI",                500_000),
        v("Alteryx",                 "Software", "Data & AI",                400_000),
        # --- Workplace/Productivity (total 7,700,000) ---
        v("Microsoft",               "Software", "Workplace/Productivity", 6_100_000),
        v("ServiceNow",              "Software", "Workplace/Productivity", 1_600_000),
        # --- Cross-Tower Labor (total 15,900,000) ---
        v("Manpower",                "Talent",   "Cross-Tower Labor",     15_000_000),
        v("Others - CTL",            "Talent",   "Cross-Tower Labor",        900_000),
        # --- Other (total 18,300,000) ---
        v("Others - Talent",         "Talent",   "Other",                  7_800_000),
        v("Others - Software",       "Software", "Other",                  4_800_000),
        v("IHS Markit",              "Data",     "Other",                  2_500_000),
        v("S&P Global",              "Data",     "Other",                  1_700_000),
        v("Experian",                "Data",     "Other",                  1_500_000),
    ]
    return records


# ---------------------------------------------------------------------------
# Test 1: calculated_internal_labor
# ---------------------------------------------------------------------------

# Function: test_calculated_internal_labor
def test_calculated_internal_labor(inputs):
    """142,750,000 × 0.25 = 35,687,500"""
    svc = InputAssumptionService()
    derived = svc.calculate_derived_inputs(inputs)
    assert derived.calculated_internal_labor == Decimal("35687500.00"), (
        f"Expected 35687500.00, got {derived.calculated_internal_labor}"
    )


# ---------------------------------------------------------------------------
# Test 2: external_spend_pct
# ---------------------------------------------------------------------------

# Function: test_external_spend_pct
def test_external_spend_pct(inputs):
    """75,400,000 / 142,750,000 ≈ 0.528185"""
    svc = InputAssumptionService()
    derived = svc.calculate_derived_inputs(inputs)
    result = float(derived.external_spend_pct_of_total_tech_spend)
    assert abs(result - 0.5282) < 0.0002, f"Expected ~0.5282, got {result}"


# ---------------------------------------------------------------------------
# Test 3: talent_spend_pct
# ---------------------------------------------------------------------------

# Function: test_talent_spend_pct
def test_talent_spend_pct(inputs):
    """40,800,000 / 75,400,000 ≈ 0.541117"""
    svc = InputAssumptionService()
    derived = svc.calculate_derived_inputs(inputs)
    result = float(derived.talent_spend_pct_of_third_party_spend)
    assert abs(result - 0.5411) < 0.0002, f"Expected ~0.5411, got {result}"


# ---------------------------------------------------------------------------
# Test 4: total vendor spend
# ---------------------------------------------------------------------------

# Function: test_total_vendor_spend
def test_total_vendor_spend(vendor_records):
    svc = VendorSpendService()
    total = svc.total_spend(vendor_records)
    assert total == Decimal("75400000"), f"Expected 75400000, got {total}"


# ---------------------------------------------------------------------------
# Test 5: talent category spend
# ---------------------------------------------------------------------------

# Function: test_talent_category_spend
def test_talent_category_spend(vendor_records):
    svc = VendorSpendService()
    talent = svc.talent_spend(vendor_records)
    assert talent == Decimal("40800000"), f"Expected 40800000, got {talent}"


# ---------------------------------------------------------------------------
# Test 6: software category spend
# ---------------------------------------------------------------------------

# Function: test_software_category_spend
def test_software_category_spend(vendor_records):
    svc = VendorSpendService()
    software = svc.software_spend(vendor_records)
    assert software == Decimal("26000000"), f"Expected 26000000, got {software}"


# ---------------------------------------------------------------------------
# Test 7: applications tower spend
# ---------------------------------------------------------------------------

# Function: test_applications_tower_spend
def test_applications_tower_spend(vendor_records):
    svc = VendorSpendService()
    by_tower = svc.spend_by_tower(vendor_records)
    apps_spend = by_tower.get("Applications", Decimal("0"))
    assert apps_spend == Decimal("18900000"), f"Expected 18900000, got {apps_spend}"


# ---------------------------------------------------------------------------
# Test 8: applications addressable spend
# ---------------------------------------------------------------------------

# Function: test_applications_addressable_spend
def test_applications_addressable_spend(vendor_records, inputs):
    svc = TowerConsolidationService()
    row = svc.calculate_tower_row(
        tower_name="Applications",
        consolidation_scope_pct=Decimal("0.75"),
        vendor_records=vendor_records,
        inputs=inputs,
    )
    assert row.addressable_spend == Decimal("14175000.00"), (
        f"Expected 14175000, got {row.addressable_spend}"
    )


# ---------------------------------------------------------------------------
# Test 9: applications gross savings
# ---------------------------------------------------------------------------

# Function: test_applications_gross_savings
def test_applications_gross_savings(vendor_records, inputs):
    """
    addressable = 14,175,000
    productivity (10%)  = 1,417,500
    rate (8%)           = 1,134,000
    vendor_mgmt (3%×40%)=   170,100
    gross               = 2,721,600
    """
    svc = TowerConsolidationService()
    row = svc.calculate_tower_row(
        tower_name="Applications",
        consolidation_scope_pct=Decimal("0.75"),
        vendor_records=vendor_records,
        inputs=inputs,
    )
    assert row.gross_annual_savings == Decimal("2721600.00"), (
        f"Expected 2721600, got {row.gross_annual_savings}"
    )


# ---------------------------------------------------------------------------
# Test 10: total gross savings
# ---------------------------------------------------------------------------

# Function: test_total_gross_savings
def test_total_gross_savings(vendor_records, inputs):
    svc = TowerConsolidationService()
    result = svc.calculate_model(vendor_records, inputs, DEFAULT_TOWER_PARAMS)
    assert result.totals.gross_annual_savings == Decimal("8902080.00"), (
        f"Expected 8902080, got {result.totals.gross_annual_savings}"
    )


# ---------------------------------------------------------------------------
# Test 11: total transition cost
# ---------------------------------------------------------------------------

# Function: test_total_transition_cost
def test_total_transition_cost(vendor_records, inputs):
    svc = TowerConsolidationService()
    result = svc.calculate_model(vendor_records, inputs, DEFAULT_TOWER_PARAMS)
    assert result.totals.transition_cost == Decimal("2318250.00"), (
        f"Expected 2318250, got {result.totals.transition_cost}"
    )


# ---------------------------------------------------------------------------
# Test 12: net year 1 total
# ---------------------------------------------------------------------------

# Function: test_net_year_1_total
def test_net_year_1_total(vendor_records, inputs):
    svc = TowerConsolidationService()
    result = svc.calculate_model(vendor_records, inputs, DEFAULT_TOWER_PARAMS)
    assert result.totals.net_year_1_savings == Decimal("6583830.00"), (
        f"Expected 6583830, got {result.totals.net_year_1_savings}"
    )


# ---------------------------------------------------------------------------
# Test 13: TechM current spend
# ---------------------------------------------------------------------------

# Function: test_techm_current_spend
def test_techm_current_spend(vendor_records):
    svc = TechMGrowthService()
    result = svc.calculate(vendor_records)
    assert result["current_techm_spend"] == str(Decimal("2500000")), (
        f"Expected 2500000, got {result['current_techm_spend']}"
    )


# ---------------------------------------------------------------------------
# Test 14: TechM target case incremental growth
# ---------------------------------------------------------------------------

# Function: test_techm_target_case_incremental
def test_techm_target_case_incremental(vendor_records):
    """Target case: 10,000,000 target − 2,500,000 current = 7,500,000"""
    svc = TechMGrowthService()
    result = svc.calculate(vendor_records)
    target_scenario = next(s for s in result["scenarios"] if s["name"] == "Target Case")
    assert target_scenario["incremental_growth"] == str(Decimal("7500000")), (
        f"Expected 7500000, got {target_scenario['incremental_growth']}"
    )


# ---------------------------------------------------------------------------
# Test 15: transformation target capacity
# ---------------------------------------------------------------------------

# Function: test_transformation_target_capacity
def test_transformation_target_capacity(vendor_records):
    """Target scenario: 10% × 75,400,000 = 7,540,000"""
    svc = TransformationCapacityService()
    result = svc.calculate(vendor_records)
    assert result["target_capacity"] == str(Decimal("7540000.00")), (
        f"Expected 7540000, got {result['target_capacity']}"
    )


# ---------------------------------------------------------------------------
# Test 16: vendor heatmap Applications score and RAG
# ---------------------------------------------------------------------------

# Function: test_heatmap_applications_score_and_rag
def test_heatmap_applications_score_and_rag(vendor_records):
    """
    Applications tower:
      spend = 18,900,000 → spend_M = 18.9
      vendor_count = 11
      strategic_importance = 5, complexity = 5

    score = (18.9 × 0.4) + (11 × 0.3) + (5 × 0.15) + (5 × 0.15)
          = 7.56 + 3.30 + 0.75 + 0.75
          = 12.36
    RAG = "Red" (score >= 8)
    """
    svc = VendorHeatmapService()
    result = svc.calculate(vendor_records)
    apps_row = next(r for r in result["heatmap"] if r["tower"] == "Applications")

    score = Decimal(apps_row["consolidation_priority_score"])
    assert score == Decimal("12.36"), f"Expected 12.36, got {score}"
    assert apps_row["rag_status"] == "Red", f"Expected Red, got {apps_row['rag_status']}"


# ---------------------------------------------------------------------------
# Additional coverage: tower row breakdowns
# ---------------------------------------------------------------------------

# Function: test_tower_row_values
@pytest.mark.parametrize("tower,spend,scope_pct,expected_addressable,expected_gross,expected_tc,expected_net_y1", [
    ("Applications",           18_900_000, "0.75", "14175000.00", "2721600.00",  "708750.00",  "2012850.00"),
    ("Infrastructure",          8_300_000, "0.75",  "6225000.00", "1195200.00",  "311250.00",   "883950.00"),
    ("Data & AI",               6_300_000, "0.75",  "4725000.00",  "907200.00",  "236250.00",   "670950.00"),
    ("Workplace/Productivity",  7_700_000, "0.60",  "4620000.00",  "887040.00",  "231000.00",   "656040.00"),
    ("Cross-Tower Labor",      15_900_000, "0.70", "11130000.00", "2136960.00",  "556500.00",  "1580460.00"),
    ("Other",                  18_300_000, "0.30",  "5490000.00", "1054080.00",  "274500.00",   "779580.00"),
])
def test_tower_row_values(tower, spend, scope_pct, expected_addressable, expected_gross, expected_tc, expected_net_y1, vendor_records, inputs):
    svc = TowerConsolidationService()
    row = svc.calculate_tower_row(
        tower_name=tower,
        consolidation_scope_pct=Decimal(scope_pct),
        vendor_records=vendor_records,
        inputs=inputs,
    )
    assert row.current_annual_spend == Decimal(str(spend)), f"[{tower}] spend mismatch: {row.current_annual_spend}"
    assert row.addressable_spend == Decimal(expected_addressable), f"[{tower}] addressable mismatch: {row.addressable_spend}"
    assert row.gross_annual_savings == Decimal(expected_gross), f"[{tower}] gross savings mismatch: {row.gross_annual_savings}"
    assert row.transition_cost == Decimal(expected_tc), f"[{tower}] transition cost mismatch: {row.transition_cost}"
    assert row.net_year_1_savings == Decimal(expected_net_y1), f"[{tower}] net Y1 mismatch: {row.net_year_1_savings}"


# Function: test_vendor_spend_summary
def test_vendor_spend_summary(vendor_records):
    """Basic smoke test for vendor spend summary."""
    svc = VendorSpendService()
    summary = svc.summarise(vendor_records)
    assert summary.total_spend == Decimal("75400000")
    assert summary.unique_vendors == len({r.vendor for r in vendor_records})
    assert len(summary.by_category) > 0
    assert len(summary.by_tower) > 0


# Function: test_default_inputs_values
def test_default_inputs_values():
    """Verify default_inputs() returns correct hardcoded values."""
    inp = default_inputs()
    assert inp.total_technology_spend == Decimal("142750000")
    assert inp.total_third_party_spend == Decimal("75400000")
    assert inp.internal_labor_pct == Decimal("0.25")
    assert inp.default_rate_compression_pct == Decimal("0.08")
    assert inp.default_productivity_improvement_pct == Decimal("0.10")
    assert inp.vendor_management_overhead_pct == Decimal("0.03")
    assert inp.target_vendor_management_overhead_reduction_pct == Decimal("0.40")
    assert inp.one_time_transition_cost_pct == Decimal("0.05")
    assert inp.scenario_name == "Base"
