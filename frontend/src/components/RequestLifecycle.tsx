type RequestLifecycleProps = {
  status: "idle" | "submitting" | "success" | "failure";
};

const LABELS: Record<RequestLifecycleProps["status"], string> = {
  idle: "Idle",
  submitting: "Submitting",
  success: "Success",
  failure: "Failure",
};

export function RequestLifecycle({ status }: RequestLifecycleProps) {
  const finalized = status === "success" || status === "failure";

  return (
    <section className="panel panel--lifecycle" aria-live="polite">
      <h2>Progress</h2>
      <p className="status-chip status-chip--active">
        Lifecycle: {LABELS[status]}
      </p>
      <ol className="timeline">
        <li className={status === "idle" ? "timeline__item is-active" : "timeline__item"}>Idle</li>
        <li
          className={
            status === "submitting"
              ? "timeline__item is-active"
              : finalized
                ? "timeline__item is-done"
                : "timeline__item"
          }
        >
          Submitting
        </li>
        <li
          className={
            finalized
              ? "timeline__item is-active"
              : "timeline__item"
          }
        >
          Finalized
        </li>
      </ol>
    </section>
  );
}
