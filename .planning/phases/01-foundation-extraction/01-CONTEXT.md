# Phase 1: Foundation Extraction - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Convert the notebook prototype into a maintainable package baseline with secure non-interactive configuration. This phase is limited to extraction and foundation decisions, not full runtime API deployment or advanced product features.

</domain>

<decisions>
## Implementation Decisions

### Module boundaries and package layout
- **D-01:** Use a feature-folder-first layout for initial extraction rather than strict layered layout.
- **D-02:** Keep shared request/response contracts in `domain/contracts.py` as the common schema source.
- **D-03:** Unify duplicate `get_document_content` into one source implementation.
- **D-04:** Keep framework integrations as thin adapters over shared core logic.

### Secrets and configuration strategy
- **D-05:** Primary runtime secret source is environment variables.
- **D-06:** Startup must fail fast on missing/invalid required configuration.
- **D-07:** Rename key contract to generic `LLM_API_KEY` for extraction baseline.
- **D-08:** Always redact sensitive secret values in logs/errors.

### Entrypoint contract for extracted code
- **D-09:** First production run surface is a callable Python service interface.
- **D-10:** Framework mode selection is an explicit enum-like argument.
- **D-11:** Return a normalized structured dictionary output contract.
- **D-12:** On mode/config/provider failure, return structured failure payloads (no silent fallback).

### the agent's Discretion
- Exact folder naming conventions under feature folders (while preserving chosen structure)
- Internal helper naming and module-level organization details
- Low-level implementation of redaction and error serialization helpers

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and outcomes
- `.planning/ROADMAP.md` — Defines Phase 1 goal, requirements mapping (ARCH-01, SECU-01, SECU-02), and success criteria.

### Requirement contracts
- `.planning/REQUIREMENTS.md` — Source of formal requirement IDs and expected v1 behavior.
- `.planning/PROJECT.md` — Core value, constraints, and project-level non-negotiables.

### Current source artifact
- `Chapter_15_Agents.ipynb` — Current implementation baseline to extract from (includes duplicated helper, interactive secret prompt, and runtime/tool logic).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `get_document_content` logic and scenario payload patterns can be reused as a single shared fixture provider.
- Tool classes (`ValidateDocumentFieldsTool`, `QueryCreditBureauAPITool`, `CalculateRiskScoreTool`, `CheckLendingComplianceTool`) are directly extractable into package modules.
- `robust_execute` safe wrapper behavior can seed runtime safety module extraction.

### Established Patterns
- Current source mixes domain/tool/runtime concerns in one notebook file; extraction must preserve behavior while introducing boundaries.
- Secret configuration currently uses interactive `getpass` + environment assignment; production path must replace this with non-interactive loading.
- Both CrewAI and LangGraph flows already exist and should remain parity-capable as extraction proceeds.

### Integration Points
- Extracted callable interface should be invokable by both tests and future API layer.
- Framework-specific code should connect through thin adapters to shared business/domain outputs.

</code_context>

<specifics>
## Specific Ideas

- Keep feature-folder packaging for initial migration speed, while preserving shared contract layer.
- Avoid hidden fallback behavior between framework modes to keep run behavior deterministic.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---
*Phase: 01-foundation-extraction*
*Context gathered: 2026-03-27*
