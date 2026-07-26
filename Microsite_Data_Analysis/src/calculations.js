// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Microsite_Data_Analysis — src (calculations.js)
// Date: 2025-10-02
// ---------------------------------------------------------------------------
// ── Calculation Engine ────────────────────────────────────────────────────
// Implements blueprint specification exactly.
// Field naming matches blueprint TypeScript pseudocode.

// calculateTowerOutput: core formula per tower
// currentSpend and vendorCount are derived via SUMIF/COUNTIF from vendorSpend
// Function: num
function num(value, fallback = 0) {
  const next = Number(value);
  return Number.isFinite(next) ? next : fallback;
}

// Function: calculateTowerOutput
export function calculateTowerOutput(tower, vendorSpend, assumptions) {
  const towerRows = vendorSpend.filter(v => v.tower === tower.name);
  const currentSpend = towerRows.reduce((sum, v) => sum + num(v.annualSpend), 0);
  const vendorCount  = towerRows.length;

  const consolidationScopePct = num(tower.consolidationScopePct);
  const productivityPct = num(assumptions.productivityPct);
  const rateCompressionPct = num(assumptions.rateCompressionPct);
  const vendorMgmtOverheadPct = num(assumptions.vendorMgmtOverheadPct);
  const overheadReductionPct = num(assumptions.overheadReductionPct);
  const transitionCostPct = num(assumptions.transitionCostPct);

  const addressableSpend    = currentSpend * consolidationScopePct;
  const efficiencySavings   = addressableSpend * productivityPct;        // blueprint: productivityPct
  const rateSavings         = addressableSpend * rateCompressionPct;
  const vendorMgmtSavings   = addressableSpend * vendorMgmtOverheadPct * overheadReductionPct;
  const grossAnnualCapacity = efficiencySavings + rateSavings + vendorMgmtSavings;
  const transitionCost      = addressableSpend * transitionCostPct;
  const netYear1Capacity    = grossAnnualCapacity - transitionCost;
  const runRateAnnualCapacity = grossAnnualCapacity;

  return {
    ...tower,
    currentSpend,
    vendorCount,
    addressableSpend,
    efficiencySavings,
    rateSavings,
    vendorMgmtSavings,
    grossAnnualCapacity,
    transitionCost,
    netYear1Capacity,
    runRateAnnualCapacity,
  };
}

// calculateScenarioTotals: aggregate all tower outputs → ScenarioTotals
// Function: calculateScenarioTotals
export function calculateScenarioTotals(towerOutputs) {
  const zero = {
    currentSpend: 0, vendorCount: 0, addressableSpend: 0,
    efficiencySavings: 0, rateSavings: 0, vendorMgmtSavings: 0,
    grossAnnualCapacity: 0, transitionCost: 0, netYear1Capacity: 0,
    runRateAnnualCapacity: 0,
  };
  return towerOutputs.reduce((acc, t) => ({
    currentSpend:           acc.currentSpend           + num(t.currentSpend),
    vendorCount:            acc.vendorCount             + num(t.vendorCount),
    addressableSpend:       acc.addressableSpend        + num(t.addressableSpend),
    efficiencySavings:      acc.efficiencySavings       + num(t.efficiencySavings),
    rateSavings:            acc.rateSavings             + num(t.rateSavings),
    vendorMgmtSavings:      acc.vendorMgmtSavings       + num(t.vendorMgmtSavings),
    grossAnnualCapacity:    acc.grossAnnualCapacity     + num(t.grossAnnualCapacity),
    transitionCost:         acc.transitionCost          + num(t.transitionCost),
    netYear1Capacity:       acc.netYear1Capacity        + num(t.netYear1Capacity),
    runRateAnnualCapacity:  acc.runRateAnnualCapacity   + num(t.runRateAnnualCapacity),
  }), zero);
}

// calculateReinvestment: allocate net capacity across strategic areas
// fundingAmount = allocationPct × reinvestmentPool  (blueprint: Target Scenario Funding)
// Function: calculateReinvestment
export function calculateReinvestment(reinvestmentList, reinvestmentPool) {
  return reinvestmentList.map(r => ({
    ...r,
    fundingAmount: num(reinvestmentPool) * num(r.allocationPct),
  }));
}

// calculateTechMGrowth: Org Growth Planner
// Function: calculateTechMGrowth
export function calculateTechMGrowth(currentTechMSpend, targetSpend) {
  const incrementalGrowth = targetSpend - currentTechMSpend;
  const growthPct         = currentTechMSpend > 0 ? incrementalGrowth / currentTechMSpend : 0;
  const quarterlyRunRate  = targetSpend / 4;
  return { incrementalGrowth, growthPct, quarterlyRunRate };
}

// calculateHeatmapScore: Vendor Rationalization Heatmap priority score
// Function: calculateHeatmapScore
export function calculateHeatmapScore(spend, vendorCount, strategicImportance, complexity, weights = {}) {
  const { wSpend = 0.35, wVendor = 0.25, wImportance = 0.25, wComplexity = 0.15 } = weights;
  const spendScore      = Math.min(100, (spend / 5) * 100);
  const vendorScore     = Math.min(100, (vendorCount / 15) * 100);
  const importanceScore = strategicImportance * 10;
  const complexityScore = complexity * 10;
  return Math.round(wSpend * spendScore + wVendor * vendorScore + wImportance * importanceScore + wComplexity * complexityScore);
}

// ── Formatting helpers ────────────────────────────────────────────────────
// Function: fmtM
export function fmtM(v, d = 1)  { return `$${Number(v || 0).toFixed(d)}M`; }
// Function: fmtPct
export function fmtPct(v)        { return `${(Number(v || 0) * 100).toFixed(0)}%`; }
// Function: fmtPct1
export function fmtPct1(v)       { return `${(Number(v || 0) * 100).toFixed(1)}%`; }
// Function: fmtNum
export function fmtNum(v)        { return Number(v || 0).toLocaleString(); }
