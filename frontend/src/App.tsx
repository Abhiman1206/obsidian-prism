import { useMemo, useState } from "react";
import { InputField } from "./components/InputField";
import { ModeSelect } from "./components/ModeSelect";
import { RequestLifecycle } from "./components/RequestLifecycle";
import { ResultPanel } from "./components/ResultPanel";
import { submitPipeline } from "./lib/api";
import type { PipelineInput, PipelineResult, ValidationErrors } from "./lib/types";
import { runtimeEnv } from "./config/env";
import {
  emptyValidationErrors,
  toInitialInput,
  validatePipelineInput,
} from "./lib/validation";

type UiStatus = "idle" | "submitting" | "success" | "failure";

function toRawPayload(input: PipelineInput): {
  applicant_id: unknown;
  document_id: unknown;
  mode: unknown;
} {
  return {
    applicant_id: input.applicant_id,
    document_id: input.document_id,
    mode: input.mode,
  };
}

export default function App() {
  const [input, setInput] = useState<PipelineInput>(toInitialInput());
  const [errors, setErrors] = useState<ValidationErrors>(emptyValidationErrors());
  const [status, setStatus] = useState<UiStatus>("idle");
  const [result, setResult] = useState<PipelineResult | null>(null);

  const canSubmit = useMemo(() => status !== "submitting", [status]);

  const updateField = (field: keyof PipelineInput, value: string) => {
    setInput((current) => ({
      ...current,
      [field]: value,
    }));

    setErrors((current) => {
      if (!current[field]) {
        return current;
      }
      const nextErrors = { ...current };
      delete nextErrors[field];
      return nextErrors;
    });
  };

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validation = validatePipelineInput(toRawPayload(input));
    if (!validation.ok) {
      setErrors(validation.errors);
      setStatus("failure");
      setResult({
        status: "failure",
        decision: "not-run",
        mode: input.mode,
        stages: {},
        error: {
          code: "VALIDATION_ERROR",
          message: "Fix validation errors before submitting.",
        },
      });
      return;
    }

    setErrors(emptyValidationErrors());
    setStatus("submitting");
    setResult(null);

    try {
      const response = await submitPipeline(validation.data);
      setResult(response);
      const failed = response.error !== null || response.status.toLowerCase() === "failed";
      setStatus(failed ? "failure" : "success");
    } catch {
      setStatus("failure");
      setResult({
        status: "failure",
        decision: "unknown",
        mode: validation.data.mode,
        stages: {},
        error: {
          code: "UNEXPECTED_CLIENT_ERROR",
          message: "Unexpected failure while calling runtime.",
        },
      });
    }
  };

  const statusLabel =
    status === "submitting"
      ? "Submitting"
      : status === "success"
        ? "Success"
        : status === "failure"
          ? "Failure"
          : "Idle";

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero__copy">
          <p className="eyebrow">
            {runtimeEnv.useMock ? "Mock Runtime Mode" : "Connected Runtime Mode"}
          </p>
          <h1>Loan Agents Runtime Console</h1>
          <p>
            Collect intake payloads, validate contract fields, and track deterministic
            runtime lifecycle outcomes.
          </p>
        </div>
        <div className="hero__status" aria-live="polite">
          <p className="hero__status-label">Current Lifecycle</p>
          <p className="hero__status-value">{statusLabel}</p>
        </div>
      </header>

      <section className="kpi-strip" aria-label="Runtime highlights">
        <article className="kpi-card">
          <p className="kpi-card__value">2</p>
          <p className="kpi-card__label">Execution Modes</p>
        </article>
        <article className="kpi-card">
          <p className="kpi-card__value">3</p>
          <p className="kpi-card__label">Lifecycle Steps</p>
        </article>
        <article className="kpi-card">
          <p className="kpi-card__value">JSON</p>
          <p className="kpi-card__label">Normalized Output</p>
        </article>
      </section>

      <main className="grid-layout">
        <section className="panel panel--intake">
          <h2>Intake</h2>
          <p className="panel__description">
            Enter identifiers and run the orchestrated policy pipeline.
          </p>
          <form onSubmit={onSubmit} noValidate>
            <InputField
              id="applicant_id"
              label="Applicant ID"
              placeholder="app_100"
              value={input.applicant_id}
              error={errors.applicant_id}
              onChange={(nextValue) => {
                updateField("applicant_id", nextValue);
              }}
            />
            <InputField
              id="document_id"
              label="Document ID"
              placeholder="document_valid_123"
              value={input.document_id}
              error={errors.document_id}
              onChange={(nextValue) => {
                updateField("document_id", nextValue);
              }}
            />
            <ModeSelect
              value={input.mode}
              error={errors.mode}
              onChange={(nextValue) => {
                updateField("mode", nextValue);
              }}
            />
            <button type="submit" disabled={!canSubmit}>
              {status === "submitting" ? "Submitting..." : "Run Pipeline"}
            </button>
          </form>
        </section>

        <RequestLifecycle status={status} />
        <ResultPanel result={result} />
      </main>
    </div>
  );
}
