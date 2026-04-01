import type { PipelineResult } from "../lib/types";

type ResultPanelProps = {
  result: PipelineResult | null;
};

export function ResultPanel({ result }: ResultPanelProps) {
  if (!result) {
    return (
      <section className="panel panel--result" aria-live="polite">
        <h2>Decision Summary</h2>
        <p>Submit a request to see normalized runtime output.</p>
      </section>
    );
  }

  return (
    <section className="panel panel--result" aria-live="polite">
      <h2>Decision Summary</h2>
      <div className="result-summary-grid">
        <p>
          Status: <strong>{result.status}</strong>
        </p>
        <p>
          Decision: <strong>{result.decision}</strong>
        </p>
        <p>
          Mode: <strong>{result.mode}</strong>
        </p>
      </div>
      <h3>Stages</h3>
      <pre>{JSON.stringify(result.stages, null, 2)}</pre>
      {result.error ? (
        <div className="error-box" role="alert">
          <p>
            Error Code: <strong>{result.error.code}</strong>
          </p>
          <p>{result.error.message}</p>
          {result.error.failure_category ? (
            <p>
              Failure Category: <strong>{result.error.failure_category}</strong>
            </p>
          ) : null}
          {typeof result.error.retry_count === "number" ? (
            <p>
              Retry Count: <strong>{result.error.retry_count}</strong>
            </p>
          ) : null}
          {result.error.stage ? (
            <p>
              Stage: <strong>{result.error.stage}</strong>
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
