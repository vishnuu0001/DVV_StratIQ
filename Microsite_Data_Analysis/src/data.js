// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Microsite_Data_Analysis — src (data.js)
// Date: 2025-10-04
// ---------------------------------------------------------------------------
// Assumption Manager defaults (Inputs tab in the blueprint)
export const defaultAssumptions = {
  rateCompressionPct:    0.08,   // Rate Compression %
  productivityPct:       0.10,   // Target Delivery Efficiency / Productivity %
  vendorMgmtOverheadPct: 0.03,   // Vendor Mgmt Overhead %
  overheadReductionPct:  0.40,   // Overhead Reduction %
  transitionCostPct:     0.05,   // Transition Cost %
};

// Current_Vendor_Spend tab — one row per vendor engagement
// Tower names must match defaultTowers names exactly (SUMIF key)
export const defaultVendorSpend = [
  { id: 1,  tower: "Applications",             vendor: "SAP",              category: "ERP",                 annualSpend: 3.20, contractDate: "2025-12" },
  { id: 2,  tower: "Applications",             vendor: "Oracle",           category: "Database",            annualSpend: 2.10, contractDate: "2026-06" },
  { id: 3,  tower: "Applications",             vendor: "Salesforce",       category: "CRM",                 annualSpend: 4.80, contractDate: "2026-03" },
  { id: 4,  tower: "Applications",             vendor: "Microsoft",        category: "Productivity",        annualSpend: 2.50, contractDate: "2027-01" },
  { id: 5,  tower: "Applications",             vendor: "ServiceNow",       category: "ITSM",                annualSpend: 1.90, contractDate: "2025-09" },
  { id: 6,  tower: "Applications",             vendor: "Workday",          category: "HCM",                 annualSpend: 2.20, contractDate: "2026-12" },
  { id: 7,  tower: "Applications",             vendor: "Coupa",            category: "Procurement",         annualSpend: 1.20, contractDate: "2026-06" },
  { id: 8,  tower: "Infrastructure",           vendor: "AWS",              category: "Cloud",               annualSpend: 3.20, contractDate: "2026-03" },
  { id: 9,  tower: "Infrastructure",           vendor: "Azure",            category: "Cloud",               annualSpend: 2.40, contractDate: "2026-09" },
  { id: 10, tower: "Infrastructure",           vendor: "VMware",           category: "Virtualisation",      annualSpend: 1.40, contractDate: "2025-12" },
  { id: 11, tower: "Infrastructure",           vendor: "Cisco",            category: "Networking",          annualSpend: 1.60, contractDate: "2026-06" },
  { id: 12, tower: "Data & AI",                vendor: "Databricks",       category: "Analytics",           annualSpend: 2.50, contractDate: "2026-03" },
  { id: 13, tower: "Data & AI",                vendor: "Snowflake",        category: "Data Warehouse",      annualSpend: 2.00, contractDate: "2025-12" },
  { id: 14, tower: "Data & AI",                vendor: "Informatica",      category: "Data Integration",    annualSpend: 1.80, contractDate: "2026-06" },
  { id: 15, tower: "Workplace / Productivity", vendor: "Microsoft 365",    category: "Collaboration",       annualSpend: 3.20, contractDate: "2026-03" },
  { id: 16, tower: "Workplace / Productivity", vendor: "Zoom",             category: "Video Conferencing",  annualSpend: 1.10, contractDate: "2025-12" },
  { id: 17, tower: "Workplace / Productivity", vendor: "Slack",            category: "Messaging",           annualSpend: 0.90, contractDate: "2026-01" },
  { id: 18, tower: "Workplace / Productivity", vendor: "Okta",             category: "Identity",            annualSpend: 0.80, contractDate: "2026-06" },
  { id: 19, tower: "Workplace / Productivity", vendor: "CrowdStrike",      category: "Endpoint Security",   annualSpend: 1.70, contractDate: "2026-09" },
  { id: 20, tower: "Cross-Tower Labor",        vendor: "TechMahindra",     category: "Managed Services",    annualSpend: 8.50, contractDate: "2027-03" },
  { id: 21, tower: "Cross-Tower Labor",        vendor: "Wipro",            category: "Staff Augmentation",  annualSpend: 4.20, contractDate: "2026-06" },
  { id: 22, tower: "Cross-Tower Labor",        vendor: "Infosys",          category: "Staff Augmentation",  annualSpend: 3.20, contractDate: "2026-03" },
  { id: 23, tower: "Other",                    vendor: "Various SaaS",     category: "SaaS Tools",          annualSpend: 5.50, contractDate: "2026-06" },
  { id: 24, tower: "Other",                    vendor: "Legacy Vendors",   category: "Legacy Systems",      annualSpend: 4.80, contractDate: "2025-12" },
  { id: 25, tower: "Other",                    vendor: "Regional Vendors", category: "Regional IT",         annualSpend: 4.00, contractDate: "2026-09" },
  { id: 26, tower: "Other",                    vendor: "Telco Partners",   category: "Telecom",             annualSpend: 4.00, contractDate: "2026-03" },
];

// Option1_Tower_Model tab — tower configuration
// consolidationScopePct and action are editable in Tower Consolidation Studio
export const defaultTowers = [
  { id: 1, name: "Applications",             consolidationScopePct: 0.75, action: "Consolidate" },
  { id: 2, name: "Infrastructure",           consolidationScopePct: 0.75, action: "Consolidate" },
  { id: 3, name: "Data & AI",                consolidationScopePct: 0.75, action: "Consolidate" },
  { id: 4, name: "Workplace / Productivity", consolidationScopePct: 0.60, action: "Selective"   },
  { id: 5, name: "Cross-Tower Labor",        consolidationScopePct: 0.70, action: "Optimize"    },
  { id: 6, name: "Other",                    consolidationScopePct: 0.30, action: "Selective"   },
];

// Exec3_Transform_Capacity — reinvestment allocation areas
export const defaultReinvestment = [
  { id: 1, area: "Salesforce / Customer & Dealer 360", allocationPct: 0.30 },
  { id: 2, area: "Data & AI / Fabric / Databricks",    allocationPct: 0.30 },
  { id: 3, area: "Automation / Process Engineering",   allocationPct: 0.20 },
  { id: 4, area: "Copilot / AI Productivity",           allocationPct: 0.10 },
  { id: 5, area: "Architecture / Governance / TBM",    allocationPct: 0.10 },
];

// Exec6_Roadmap — transition milestones
export const defaultRoadmap = [
  {
    id: 1, horizon: "0–30 Days",
    milestone: "Mobilize & Baseline",
    owner: "Program Office",
    status: "In Progress",
    actions: "Confirm scope, baseline spend, vendor data collection, RACI alignment, kick-off governance cadence",
  },
  {
    id: 2, horizon: "30–60 Days",
    milestone: "Quick Win Discovery",
    owner: "TechM Lead",
    status: "Pending",
    actions: "Salesforce discovery, Data/Fabric review, TBM pilot design, vendor overlap analysis, automation scan",
  },
  {
    id: 3, horizon: "60–90 Days",
    milestone: "Pilot & Validate",
    owner: "Solutions Arch",
    status: "Pending",
    actions: "Apptio/TBM pilot, automation scan, vendor overlap review, financial model validation, steering deck",
  },
  {
    id: 4, horizon: "3–6 Months",
    milestone: "Transition Design",
    owner: "CTO / CPO",
    status: "Pending",
    actions: "Operating model, RACI, governance framework, commercial model design, wave 1 SoW",
  },
  {
    id: 5, horizon: "6–12 Months",
    milestone: "Execute Wave 1",
    owner: "Delivery Lead",
    status: "Pending",
    actions: "Salesforce, Data & AI, apps consolidation quick wins, first savings realised, KPI tracking live",
  },
  {
    id: 6, horizon: "12–24 Months",
    milestone: "Scale & Strategic Partner",
    owner: "CEO / Board",
    status: "Pending",
    actions: "Selective tower consolidation, automation at scale, managed services expansion, Org Growth partnership",
  },
];

export const TOWER_NAMES = defaultTowers.map(t => t.name);
export const ACTION_OPTIONS = ["Consolidate", "Optimize", "Selective", "Retain", "Defer"];
export const STATUS_OPTIONS  = ["Pending", "In Progress", "Complete", "At Risk"];
