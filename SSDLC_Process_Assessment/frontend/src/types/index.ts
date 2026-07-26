// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/types (index.ts)
// Date: 2026-06-18
// ---------------------------------------------------------------------------
export interface SheetInfo {
  name: string
  row_count: number
  column_count: number
  has_data: boolean
}

export interface WorkbookUploadResponse {
  workbook_id: string
  filename: string
  status: string
  sheet_count: number
  sheets: SheetInfo[]
  validation: string[]
  message?: string
}

export interface ValidationResult {
  status: string
  warnings: string[]
}

export interface KpiData {
  total_third_party_spend: number | string
  total_third_party_spend_fmt?: string
  external_talent_spend: number | string
  external_talent_spend_fmt?: string
  addressable_spend: number | string
  gross_annual_capacity: number | string
  gross_annual_capacity_fmt?: string
  transition_cost: number | string
  net_year_1_savings: number | string
  run_rate_annual_savings: number | string
  roi_pct: number | string
  roi_pct_fmt?: string
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
  bullet: string
  category: string
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
  name: string
  year_1_target: number | string
  incremental_growth: number | string
  growth_pct: number | string
  quarterly_run_rate: number | string
}

export interface OpportunityArea {
  area: string
  low: number | string
  high: number | string
  expected: number | string
}

export interface TechMGrowthResponse {
  current_techm_spend: number | string
  scenarios: TechMScenario[]
  opportunity_areas: OpportunityArea[]
}

export interface CapacityScenario {
  name: string
  optimization_rate: number | string
  capacity_created: number | string
  reinvestment_pool: number | string
}

export interface ReinvestmentAllocation {
  area: string
  pct: number | string
  funding: number | string
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
