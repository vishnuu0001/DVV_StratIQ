# TraceForge Architectural Rewrite - Comprehensive Plan

## Executive Summary

**Problem:** TraceForge generates only 2 test cases per requirement while ChatGPT/Codex generates 5-6+ diverse scenarios covering POSITIVE, NEGATIVE, EDGE, BOUNDARY, SECURITY, INTEGRATION test types.

**Root Cause:** Minimalist coverage policy (1 POSITIVE + 1 NEGATIVE minimum) combined with generic Ollama prompting that doesn't guide comprehensive scenario generation.

**Solution:** Multi-phase architectural rewrite to align TraceForge with enterprise test design standards:
- Phase 1: ✅ COMPLETED - Expand coverage policy from 2-case minimum to 6-10 case targets
- Phase 2: IN PROGRESS - Enhance Ollama prompting with business-rule decomposition guidance
- Phase 3: PENDING - Add process-area mapping and intelligent scenario classification
- Phase 4: PENDING - Excel output enhancement with process-area grouping and summary statistics

**Expected Outcome:** 5-8 test cases per requirement on average, comprehensive scenario coverage, ChatGPT/Codex comparable quality.

---

## Phase 1: Coverage Policy Expansion ✅ COMPLETED

**Status:** IMPLEMENTED AND TESTED

**Changes Made:**
```python
DEFAULT_POLICY = {
    "min_per_requirement": {
        "POSITIVE": 3,      # Increased from 1 to 3
        "NEGATIVE": 2,      # Added as explicit base
        "EDGE": 1,          # Added edge cases
    },
    "acceptance_criteria_coverage": "EVERY_AC_MAPPED_WITH_DEDICATED_SCENARIO",
    "nfr_policy": "PERFORMANCE_OR_BOUNDARY_OR_EXPLICIT_WAIVER",
    "boundary_required_when": "requirement contains numeric range, limit, quantity, or measurable constraint",
    "security_required_when": "requirement contains authorization, role, permission, or approval keyword",
    "integration_required_when": "requirement mentions inter-system flow, reconciliation, interface, or handoff",
}
```

**Updated Functions:**
1. `minimum_scenarios_for_requirement()` - Now generates augmented targets based on requirement characteristics
2. `_check_boundary_policy()` - Returns list[CoverageGap] instead of single gap
3. `_check_security_policy()` - NEW: Enforces SECURITY tests for auth requirements
4. `_check_integration_policy()` - NEW: Enforces INTEGRATION tests for multi-system flows
5. `check_coverage()` - Updated to call all three new policy checks

**Impact Analysis:**
- Test 1 (Simple requirement): 2 → 6 scenarios (+200%)
- Test 2 (With rejection): 2 → 7 scenarios (+250%)
- Test 3 (With numeric bounds): 2 → 7 scenarios (+250%)
- Test 4 (With security): 2 → 8 scenarios (+300%)
- Test 5 (Complex scenario): 2 → 10 scenarios (+400%)

**Validation:** ✅ All syntax verified, unit tests pass

---

## Phase 2: Enhanced Ollama Prompting (IN PROGRESS)

**Objective:** Guide Ollama toward comprehensive, diverse, business-rule-aware scenario generation.

**Key Additions Needed:**

### 2.1 Comprehensive Scenario Generation Section
```
COMPREHENSIVE SCENARIO GENERATION (NOT MINIMAL COVERAGE):
Your goal is to generate 5-8 diverse, independent, evidence-backed test scenarios per requirement, 
not just the minimum viable 2-3. Every acceptance criterion must have its own dedicated test case 
plus complementary boundary, edge, and security variants.
```

### 2.2 Business-Rule Decomposition Instruction
```
BUSINESS-RULE DECOMPOSITION - CRITICAL INSTRUCTION:
When the requirement or acceptance criteria contain compound conditions (linked by "both", "and", 
"must", "must also"), decompose EACH condition into its own independent test scenario:

Example requirement: "The order requires approval AND FSC balance check."
Generate 5+ scenarios: 
  1. SC-01 [POSITIVE]: Approval succeeds with sufficient FSC balance
  2. SC-02 [NEGATIVE]: Approval denied due to insufficient FSC balance
  3. SC-03 [NEGATIVE_SECURITY]: User without approval role cannot approve
  4. SC-04 [EDGE]: FSC balance exactly equals requirement
  5. SC-05 [INTEGRATION]: Approval and FSC check orchestration via system interfaces
Never hide compound conditions under a single scenario title.
```

### 2.3 Negative and Edge Pattern Guidance
```
NEGATIVE AND EDGE SCENARIO PATTERNS - Generate These Explicitly:
For every POSITIVE scenario, you MUST also generate:
  1. NEGATIVE_VALIDATION: Invalid/missing field, wrong type, out-of-range value
  2. NEGATIVE_BUSINESS_RULE: Violates stated business rule
  3. NEGATIVE_SECURITY: Unauthorized identity, insufficient permissions
  4. EDGE_CONCURRENCY: Multiple simultaneous requests on shared state
  5. EDGE_BOUNDARY: Exactly at threshold (balance equals requirement precisely)
  6. INTEGRATION: Multi-step workflow spanning multiple systems
```

### 2.4 Process-Area Identification Guidance
```
PROCESS AREA IDENTIFICATION:
Automatically identify and assign process_area for each scenario:
  - Master Data, Sales Order, MRP / TIPS, Production, BIO-Burden Quality
  - FSC Accounting, Billing, External Warehouse, Outbound Logistics
  - Customer Return, R2R / BC Checks, Reconciliation
  - Integration Recovery, Audit and Compliance
```

### 2.5 Priority Assignment Logic
```
PRIORITY ASSIGNMENT:
- P1 (Critical): Directly impact business value, customer outcomes, financial accuracy, compliance
- P2 (High): Secondary workflows, error handling, important edge cases
- P3 (Low): Informational, logging, diagnostic scenarios
Default is P2; use P1 only when explicitly justified.
```

**Implementation Status:**
- System prompt update attempted but blocked by encoding issues (em-dash character)
- Alternative: Modify `_build_test_case_prompt()` to programmatically construct enhanced prompt
- Alternative: Update prompt templates in database or config files

**Next Steps for Phase 2:**
1. Refactor `_build_test_case_prompt()` to use string concatenation instead of template substitution
2. Add business-rule decomposition examples
3. Add process-area mapping logic as separate Ollama pre-processing step
4. Enhance `_generate_category_batch()` user prompt with scenario diversity requirements

---

## Phase 3: Process-Area Mapping (PENDING)

**Objective:** Intelligently map requirements to process areas and ensure variant scenarios inherit parent process area.

**New Function Needed:** `_detect_process_area(requirement: Requirement) -> str`

**Implementation:**
```python
PROCESS_AREA_KEYWORDS = {
    "Master Data": ["master data", "dimension", "customer", "material", "supplier", "location", "grade", "configuration"],
    "Sales Order": ["order entry", "sales order", "pricing", "validation", "modification", "cancellation"],
    "MRP / TIPS": ["mrp", "tips", "demand planning", "supply planning", "production planning", "raw-material"],
    "Production": ["manufacturing", "production", "shift", "bom", "routing", "twin reel", "single reel"],
    "BIO-Burden Quality": ["bio-burden", "sampling", "testing", "quality release", "certification"],
    "FSC Accounting": ["fsc", "credit", "balance", "reconciliation", "return reversal", "post-dispatch"],
    "Billing": ["billing", "invoice", "line-item", "price", "discount", "posting"],
    "External Warehouse": ["warehouse", "stock receipt", "batch", "availability"],
    "Outbound Logistics": ["outbound", "dispatch", "shipment", "quality-hold"],
    "Customer Return": ["return", "acceptance", "quality assessment", "accounting reversal"],
    "R2R / BC Checks": ["r2r", "bc check", "reconciliation"],
    "Reconciliation": ["reconcil", "inter-system sync", "audit trail", "completeness"],
    "Integration Recovery": ["error handling", "retry", "manual intervention"],
    "Audit and Compliance": ["audit", "compliance", "regulatory"],
}

def _detect_process_area(requirement: Requirement) -> str:
    evidence = f"{requirement.title} {requirement.statement} {' '.join(requirement.acceptance_criteria or [])}".lower()
    for area, keywords in PROCESS_AREA_KEYWORDS.items():
        if any(kw in evidence for kw in keywords):
            return area
    return ""
```

**Where to Implement:**
- Add to `test_designer.py` as new helper function
- Call in `_validate_test_case_items()` when extracting test case from Ollama response
- Call in `_expand_outline()` when expanding scenario outlines into full test cases
- Pass to Excel generator for grouping and summary

---

## Phase 4: Excel Output Enhancement (PENDING)

**Objective:** Match ChatGPT/Codex Excel output structure with process-area grouping and comprehensive statistics.

**Changes to `test_case_excel_generator.py`:**

### 4.1 Test Cases Sheet: Add Process-Area Grouping
- Sort test cases by process_area before writing to sheet
- Add subtotal rows after each process area group
- Color-code process areas for visual distinction

### 4.2 Summary Sheet: Enhanced Statistics
```
Coverage Summary:
- Total test cases (current formula works)
- Cases by process area (add new row per area)
- Cases by priority (P1/P2/P3 distribution)
- Cases by test type (POSITIVE/NEGATIVE/EDGE/BOUNDARY/SECURITY/INTEGRATION)
- Cases by test level (UNIT/API/UI_E2E/INTEGRATION/UAT)
- Cases by automation status
- AUTOMATION_BLOCKED count (high-risk indicators)
- Manual test count (resource planning indicator)
```

### 4.3 New Coverage Metrics Sheet
```
Coverage Dimension Analysis:
- BUSINESS_RULE: (count) scenarios
- WORKFLOW: (count) scenarios
- DATA_VARIANT: (count) scenarios
- NEGATIVE_CONTROL: (count) scenarios
- BOUNDARY: (count) scenarios
- EDGE_CONDITION: (count) scenarios
- SECURITY: (count) scenarios
- PERFORMANCE: (count) scenarios
- INTEGRATION_HANDOFF: (count) scenarios
- RECONCILIATION: (count) scenarios
- END_TO_END: (count) scenarios
```

### 4.4 Risk Assessment Sheet
```
Risk Matrix:
- High-risk AUTOMATION_BLOCKED scenarios (manual testing required)
- Missing process area coverage (gaps in full E2E journey)
- Unmatched acceptance criteria (coverage gaps)
- Ambiguities requiring business clarification
- Integration recovery scenarios (resilience coverage)
```

---

## Implementation Roadmap

### Immediate (Phase 1 & 2):
- [x] Update coverage_policy.py with comprehensive targets
- [x] Add BOUNDARY/SECURITY/INTEGRATION policy checks
- [x] Test coverage policy changes
- [ ] Enhance _build_test_case_prompt() with scenario diversity guidance
- [ ] Add business-rule decomposition examples to system prompt
- [ ] Increase token budgets for test case generation (currently 1800*needed)
- [ ] Test end-to-end with sample requirement

### Short-term (Phase 3):
- [ ] Implement `_detect_process_area()` function
- [ ] Integrate process-area detection into test case extraction
- [ ] Add process-area field to scenario outlines
- [ ] Test process-area assignment accuracy

### Medium-term (Phase 4):
- [ ] Enhance test_case_excel_generator.py with process-area grouping
- [ ] Add Coverage Metrics sheet
- [ ] Add Risk Assessment sheet
- [ ] Update summary statistics formulas
- [ ] Test Excel output structure

### Long-term (Optimization):
- [ ] Implement semantic deduplication (content-based, not title-based)
- [ ] Add scenario complexity metrics (estimated automation effort)
- [ ] Add traceability heat map (which requirements/ACs are well-covered)
- [ ] Performance optimization for large requirement sets (50+ requirements)

---

## Success Criteria

**Phase 1 Complete When:**
- ✅ Coverage policy generates 6-10 scenarios per simple requirement
- ✅ All unit tests pass
- ✅ No regressions in test designer pipeline

**Phase 2 Complete When:**
- Ollama generates 5-8 scenarios per requirement on average
- Scenarios include POSITIVE/NEGATIVE/EDGE/BOUNDARY/SECURITY/INTEGRATION variants
- Business-rule decomposition produces distinct scenarios for compound conditions
- No generic step placeholder text in generated scenarios

**Phase 3 Complete When:**
- Process-area assignment is 95%+ accurate
- All test cases have correct process_area mapping
- Variant scenarios inherit parent process-area correctly

**Phase 4 Complete When:**
- Excel output matches ChatGPT/Codex structure
- Summary statistics accurately reflect test coverage
- Process-area grouping provides clear coverage overview

**Overall Success When:**
- Average scenarios per requirement: 5-6 (vs. current 2)
- ChatGPT/Codex comparison: Feature parity achieved
- Enterprise test standards: Comprehensive coverage demonstrated
- User satisfaction: Validation against business requirements

---

## Technical Considerations

### Token Budget Impact:
- Current: ~1800 tokens per test type batch
- Proposed: ~3000-4000 tokens per batch (3 POSITIVE + 2 NEGATIVE + 1 EDGE + variants)
- Mitigation: Increase TEST_CASE_MAX_TOKENS in config if needed

### Ollama Model Capacity:
- Current testing: Ollama 2.6B/7B models
- Concern: Larger prompt + higher token budget may cause truncation
- Recommendation: Test with Ollama 13B or larger if available

### Database Schema:
- Current: TestCase table supports all required fields
- No schema changes needed
- Consider indexing on (project_id, process_area, test_type, priority) for performance

### Backward Compatibility:
- All changes are additive (new fields, new checks)
- Existing test cases remain valid
- Coverage policy is only enforced on NEW generation, not on existing cases

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Ollama token truncation | Medium | High | Monitor token usage, increase budget cautiously |
| Performance degradation | Low | Medium | Implement batch generation for large requirements |
| Quality regression | Low | High | Extensive unit testing, pilot with sample requirements |
| Prompt encoding issues | Low | Low | Use string concatenation instead of template variables |
| Process-area detection inaccuracy | Medium | Low | Add manual override capability in UI |

---

## References

**ChatGPT/Codex Test Plan Reference:**
- File: C:\RD\DVV_StratIQ-Aqorynth\dsvstratiq\TraceForge\data\TestData\Outbound_E2E_01_Detailed_Test_Plan.docx
- File: C:\RD\DVV_StratIQ-Aqorynth\dsvstratiq\TraceForge\data\TestData\Outbound_E2E_01_Detailed_Test_Cases.xlsx
- Key Metrics: 82 test cases across 20 process areas for 14 requirements (5-6 cases/requirement)

**Requirement Baseline:**
- File: C:\RD\DVV_StratIQ-Aqorynth\dsvstratiq\TraceForge\data\TestData\E2E_OB_Direct Order – Twin Reel With FSC Requirements.docx

---

**Document Status:** ARCHITECTURAL PLAN - PHASE 1 COMPLETE, PHASES 2-4 PENDING  
**Last Updated:** 2026-08-08  
**Next Review:** After Phase 2 implementation
