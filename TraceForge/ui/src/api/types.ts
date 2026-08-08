// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/api (types.ts)
// Date: 2026-07-04
// ---------------------------------------------------------------------------
export interface Project {
  id: string
  key: string
  name: string
  client_name: string | null
  status: string
  config: Record<string, unknown>
  created_at: string
}

export interface SourceDocument {
  id: string
  project_id: string
  source_type: string
  connector_ref: Record<string, unknown>
  filename: string
  doc_class: string
  status: 'PENDING' | 'PARSING' | 'INDEXED' | 'FAILED'
  page_count: number | null
  parse_error: string | null
}

export interface Chunk {
  id: string
  ordinal: number
  text: string
  token_count: number
  locator: Record<string, unknown>
}

export interface AmbiguityFlag {
  code: string
  span: string
  explanation: string
  suggestion: string
}

export interface Requirement {
  id: string
  req_id: string
  project_id: string
  level: string
  title: string
  statement: string
  ears_pattern: string
  ears_parts: Record<string, string | null>
  rationale: string | null
  acceptance_criteria: string[]
  priority: string
  ambiguity_score: number
  ambiguity_flags: AmbiguityFlag[]
  status: string
  version: number
  created_by_agent: boolean
}

export interface Citation {
  id: string
  chunk_id: string
  relevance: number
  quoted_span: string
  locator: Record<string, unknown>
  source_document_filename: string
}

export interface RequirementDetail extends Requirement {
  citations: Citation[]
}

export interface PipelineRun {
  id: string
  project_id: string
  stage: string
  status: 'QUEUED' | 'RUNNING' | 'AWAITING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'FAILED'
  stats: Record<string, unknown>
  error: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface Gate {
  id: string
  pipeline_run_id: string
  required_role: string
  decision: string
  decided_by: string | null
  rationale: string | null
  item_decisions: Record<string, string>
  auto_approve: boolean
}

export interface AuditEventOut {
  id: string
  actor: string
  action: string
  entity_type: string
  entity_id: string
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
  at: string
}

export interface TestPlan {
  id: string
  title: string
  scope: string
  strategy: string
  environments: string[]
  schedule: Record<string, unknown>
  entry_exit_criteria: { entry?: string[]; exit?: string[]; suspension?: string[]; resumption?: string[] }
  status: string
  version: number
}

export interface TestStep {
  step_no: number
  action: string
  expected_result: string
  test_data?: string
  binding_status?: 'PENDING' | 'CONFIRMED'
}

export interface TestCase {
  id: string
  tc_id: string
  project_id: string
  requirement_id: string
  title: string
  test_type: 'POSITIVE' | 'NEGATIVE' | 'EDGE' | 'BOUNDARY' | 'NEGATIVE_SECURITY' | 'PERFORMANCE'
  test_level: string
  preconditions: string[]
  steps: TestStep[]
  gherkin: string | null
  priority: string
  status: string
  version: number
  created_by_agent: boolean
}

export interface TestScript {
  id: string
  ts_id: string
  project_id: string
  test_case_id: string
  target: 'PLAYWRIGHT_TS' | 'SELENIUM_TS' | string
  language: string
  code: string
  file_path: string
  compiles: boolean | null
  validation_output: string | null
  status: string
  version: number
}

export interface Artifact {
  id: string
  project_id: string
  kind: string
  filename: string
  sha256: string
  version: number
  stale: boolean
  requirement_ids: string[]
}

export interface CoverageSummary {
  total_requirements: number
  covered_requirements: number
  coverage_pct: number
  by_level: Record<string, { total: number; covered: number }>
  total_test_cases: number
  total_scripts: number
}
