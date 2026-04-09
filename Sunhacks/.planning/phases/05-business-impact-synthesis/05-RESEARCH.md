---
phase: 05-business-impact-synthesis
status: complete
created: 2026-04-10
requirements: [BIZ-01, BIZ-02, BIZ-03]
---

# Phase 5 Research: Business Impact Synthesis

## Objective
Design a deterministic and auditable business-impact synthesis layer that converts component risk forecasts into executive-friendly financial narratives.

## Inputs Available from Existing Phases
- Run-scoped risk forecast rows with ranked probability, confidence, and top contributing signals.
- Run-scoped health score and explainability factors.
- Ingestion evidence lineage records retrievable by run.
- Typed contract parity checks between Python contracts and frontend TypeScript mirrors.

## Recommended Architecture

### 1) Business assumption model and KPI translation engine
Create a deterministic translation module that accepts:
- risk forecasts per component
- optional business assumptions (hourly engineering rate, expected incident hours, downtime revenue per hour)

Outputs per component:
- expected_engineering_hours
- expected_downtime_hours
- expected_total_cost
- cost_drivers (top weighted financial drivers)

Design principle:
- no probabilistic sampling in v1
- deterministic formulas only
- all formulas explicit in code and tests

### 2) Executive narrative writer (template-first)
Implement a report writer that builds plain-language sections:
- executive_summary
- top_risks
- cost_of_inaction
- recommended_priorities

Design principle:
- avoid engineering jargon
- use short sentence templates and threshold-based language bands
- output is action-oriented and includes priority ordering rationale

### 3) Claim-to-lineage trace linkage
Each business claim in the report should include evidence references:
- claim_id
- claim_text
- related_component_id
- lineage_refs (lineage IDs or source locators for supporting evidence)

Design principle:
- claim references are machine-readable and deterministic
- unknown lineage for a claim should return an empty list, never crash

## Proposed File Targets
- backend/app/domain/business/translation.py
- backend/app/domain/business/report_writer.py
- backend/app/domain/business/repository.py
- backend/app/workers/business_reporting.py
- backend/app/api/routes/executive_reports.py
- contracts/v1/report.py
- frontend/lib/contracts/index.ts
- backend/tests/test_business_impact_translation.py
- backend/tests/test_executive_report_writer.py
- backend/tests/test_executive_reports_route_contract.py
- backend/tests/test_contract_alignment.py
- backend/app/main.py

## Risks and Mitigations
- Risk: Business assumptions vary by company and can cause noisy output.
  - Mitigation: Define clear default assumptions and support explicit override payloads.
- Risk: Report language becomes too technical.
  - Mitigation: Template constraints and tests that assert disallowed technical jargon tokens are absent in summary sections.
- Risk: Claim traceability is incomplete.
  - Mitigation: Require claim refs and lineage link lists in route contract tests.

## Validation Strategy
- BIZ-01: `pytest backend/tests/test_business_impact_translation.py -q`
- BIZ-02: `pytest backend/tests/test_executive_report_writer.py backend/tests/test_contract_alignment.py -q`
- BIZ-03: `pytest backend/tests/test_executive_reports_route_contract.py -q`

Full phase regression gate:
- `pytest backend/tests/test_business_impact_translation.py backend/tests/test_executive_report_writer.py backend/tests/test_contract_alignment.py backend/tests/test_executive_reports_route_contract.py -q`

## Recommendation
Proceed with three plans in dependency order:
1. Build deterministic business assumptions and KPI translation logic.
2. Build executive report writer templates and aligned contracts.
3. Persist report claims with evidence lineage references and expose run-scoped API retrieval.
