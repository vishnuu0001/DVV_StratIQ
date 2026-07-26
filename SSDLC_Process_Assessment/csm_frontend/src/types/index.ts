// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/types (index.ts)
// Date: 2025-11-19
// ---------------------------------------------------------------------------
export interface WorkbookUploadResponse {
  workbook_id: string
  filename: string
  status: string
  sheet_count: number
  sheets: string[]
  validation: ValidationResult
}

export interface ValidationResult {
  status: string
  warnings: string[]
}

export interface KpiData {
  total_technology_spend: number
  direct_tech_opex: number
  total_third_party_spend: number
  external_talent_spend: number
  addressable_spend: number
  gross_annual_capacity_created: number
  transition_cost: number
  net_year_1_capacity_created: number
  run_rate_annual_capacity_created: number
}

export interface TowerSummaryRow {
  tower: string
  current_spend: number
  addressable_spend: number
  gross_savings: number
  transition_cost: number
  net_year_1_savings: number
  run_rate_savings: number
  vendor_count: number
  consolidation_scope_pct: number
}

export interface SpendBreakdown {
  category: string
  spend: number
  count: number
}

export interface VendorRecord {
  vendor: string
  spend_category: string
  tower: string
  annual_spend: number
  share_of_third_party_spend: number
  consolidation_signal: 'High' | 'Medium' | 'Low'
  recommended_treatment: string
  rank: number
}

export interface DashboardResponse {
  kpis: KpiData
  tower_summary: TowerSummaryRow[]
  spend_by_category: SpendBreakdown[]
  top_vendors: VendorRecord[]
  executive_story: ExecutiveStoryBullet[]
  calculation_audit: CalculationAuditEntry[]
  validation: ValidationResult
}

export interface ExecutiveStoryBullet {
  metric_key: string
  label: string
  display_value?: string
  text?: string
}

export interface CalculationAuditEntry {
  metric: string
  formula: string
  source_refs: string[]
  inputs: Record<string, number>
  result: number
}

export interface HeatmapRow {
  tower: string
  spend: number
  vendor_count: number
  strategic_importance: number
  complexity: number
  consolidation_priority_score: number
  rag: 'Red' | 'Amber' | 'Green'
  recommended_move: string
}

export interface TechMScenario {
  scenario: string
  year_1_target: number
  positioning: string
  confidence: string
  incremental_growth: number
  growth_pct: number
  quarterly_run_rate: number
}

export interface OpportunityArea {
  area: string
  low_case: number
  high_case: number
  expected_case: number
}

export interface TechMGrowthResponse {
  current_baseline: number
  scenarios: TechMScenario[]
  opportunity_areas: OpportunityArea[]
}

export interface CapacityScenario {
  name: string
  optimization_rate: number
  capacity_created: number
  reinvestment_pool: number
}

export interface ReinvestmentAllocation {
  area: string
  allocation_pct: number
  funding: number
}

export interface TransformationCapacityResponse {
  scenarios: CapacityScenario[]
  reinvestment_allocations: ReinvestmentAllocation[]
  total_capacity: number
  recommended_scenario: string
}

export interface ScenarioRequest {
  scenario_name: string
  rate_compression_pct: number
  productivity_improvement_pct: number
  transition_cost_pct: number
  tower_scope_overrides: Record<string, number>
}

export interface TowerModelRow {
  tower: string
  current_spend: number
  consolidation_scope_pct: number
  addressable_spend: number
  productivity_savings: number
  rate_savings: number
  vm_savings: number
  gross_savings: number
  transition_cost: number
  net_year_1_savings: number
  run_rate_savings: number
  vendor_count?: number
}

export interface TowerModelResponse {
  rows: TowerModelRow[]
  totals: TowerModelRow
  scenario_name: string
}

export interface VendorLandscapeResponse {
  vendors: VendorRecord[]
  spend_by_category: SpendBreakdown[]
  spend_by_tower: SpendBreakdown[]
  summary: {
    total_spend: number
    talent_pct: number
    software_pct: number
    data_pct: number
    top_vendor: string
  }
}

export interface HeatmapResponse {
  rows: HeatmapRow[]
}

export interface OperatingModelParticipant {
  name: string
  role: string
  responsibilities: string[]
  color: string
}

export interface OperatingModelRoadmapItem {
  phase: string
  months: string
  activities: string[]
  milestone: string
}

export interface RaciEntry {
  activity: string
  mazda: string
  ey: string
  microsoft: string
  tech_mahindra: string
}

export interface OperatingModelResponse {
  participants: OperatingModelParticipant[]
  roadmap: OperatingModelRoadmapItem[]
  raci: RaciEntry[]
  priority_areas: { area: string; description: string; impact: string }[]
}
