// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/constants (stages.js)
// Date: 2026-07-15
// ---------------------------------------------------------------------------
/**
 * The real Oppty Stage funnel used in the FY27 Plan Tracker source data —
 * replaces the previous CRM-generic vocabulary (Prospecting/Qualification/...),
 * which never matched any real stage value and could never satisfy the
 * backend's is_closed_won_stage() gap-analysis check for opportunities
 * created through this UI. Shared by OpportunityReport.jsx, OpportunityForm.jsx,
 * and DashboardPage.jsx so all three always agree on the same taxonomy.
 */
export const STAGES = ['P0-P2', 'P3 Upside', 'P3.1 Strong Upside', 'P5 Closed/Won'];

export const STAGE_COLORS = {
  'P5 Closed/Won': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  'P3.1 Strong Upside': 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  'P3 Upside': 'bg-violet-500/20 text-violet-300 border-violet-500/30',
  'P0-P2': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
};

// Function: isClosedWonStage
// Case/whitespace-tolerant, mirrors the backend's financial_summary_service.is_closed_won_stage —
// stage text is user-entered and will keep growing, so an exact string compare is too brittle.
// Function: isClosedWonStage
export function isClosedWonStage(stage) {
  return /closed\s*\/?\s*won/i.test(stage || '');
}
