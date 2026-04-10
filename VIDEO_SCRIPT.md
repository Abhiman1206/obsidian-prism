# Whole Application Video Script

## Video Goal
Explain how the Loan Agents system works, with primary focus on agent orchestration, stage behavior, and normalized decision output.

## Target Duration
3 minutes

## Audience
Mixed audience: product stakeholders, engineers, and reviewers.

## Script

### 0:00 - 0:20 | Opening
**Visual**: App landing screen with the hero header and status card.

**Narration**:
Welcome to the Loan Agents Runtime Console. In this demo, we will focus on one thing: how multiple agents collaborate to produce a reliable loan decision, with the same output contract in CrewAI and LangGraph modes.

---

### 0:20 - 0:45 | Input and Mode Selection
**Visual**: Highlight applicant ID, document ID, mode selector, and Run Pipeline button.

**Narration**:
The user provides applicant ID, document ID, and execution mode. The mode switch is important because it lets us run the same request through two orchestration engines, CrewAI or LangGraph, and compare behavior without changing the client experience.

The frontend validates inputs first, then sends one normalized request to the backend runtime.

---

### 0:45 - 1:50 | Core Agent Workflow
**Visual**: Sequence diagram showing runtime service and stage progression: document -> credit -> risk -> compliance.

**Narration**:
Once Run Pipeline is triggered, the runtime receives the request and dispatches it through the selected orchestration adapter. This is where agent behavior becomes the center of the system.

The pipeline runs in a deterministic order across four domain agents:
1. Document agent validates and extracts required file-level facts.
2. Credit agent evaluates credit profile signals.
3. Risk agent computes risk interpretation from prior outputs.
4. Compliance agent checks policy and regulatory constraints.

Each agent receives structured context from previous stages and returns structured output. If a stage fails, downstream stages are marked as skipped, not silently omitted. That explicit status model gives us traceability and makes operations easier to debug.

Even though CrewAI and LangGraph orchestrate differently internally, both adapters are normalized into the same stage schema and decision envelope.

---

### 1:50 - 2:25 | Decision Normalization and Failure Behavior
**Visual**: Result panel with a success run and a failure run side by side.

**Narration**:
A key design choice is deterministic output shape. Both successful and failed runs return a predictable envelope with fields like status, mode, stages, decision, and error.

This means consumers do not need special parsing logic for different orchestration modes or failure types. They can rely on one contract every time.

Because each stage carries explicit status and timing, teams can quickly identify where execution degraded or stopped.

---

### 2:25 - 2:50 | Operational Controls Around Agents
**Visual**: Logs and metrics overlay with correlation ID and stage duration.

**Narration**:
Around the agent pipeline, the runtime applies retries, timeout handling, rate limiting, structured logging, and redaction. So the system is not only multi-agent, but production-safe and observable.

---

### 2:50 - 3:00 | Closing
**Visual**: Final successful run in UI.

**Narration**:
In short, this application demonstrates practical agent orchestration: deterministic stage flow, framework-agnostic normalization, and consistent decision contracts that are ready for real-world integration.

---

## Optional Alternate Closing (Short)
This is a multi-agent loan decision runtime where different orchestration frameworks produce one consistent, production-ready contract.
