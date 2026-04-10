import React from "react";
import { analyzeRepository } from "../../lib/api/repositories";
import { getRunStatus, inferRunIds } from "../../lib/api/runs";

type RunsPageProps = {
  searchParams?: Promise<{
    repository_url?: string | string[];
  }>;
};

const DEFAULT_REPOSITORY_URL = "https://github.com/Abhiman1206/AI_APP.git";

function normalizeRepositoryUrl(raw: string | string[] | undefined): string {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : DEFAULT_REPOSITORY_URL;
}

function statusTone(status: string): { label: string; color: string } {
  if (status === "succeeded") {
    return { label: "Succeeded", color: "var(--success)" };
  }
  if (status === "running") {
    return { label: "Running", color: "var(--primary)" };
  }
  if (status === "queued") {
    return { label: "Queued", color: "var(--accent)" };
  }
  return { label: "Failed", color: "#ef4444" };
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Unknown";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "Unknown";
  }
  return parsed.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function RunsPage({ searchParams }: RunsPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const repositoryUrl = normalizeRepositoryUrl(resolvedSearchParams.repository_url);
  const analysis = await analyzeRepository(repositoryUrl);

  const runIds = inferRunIds(analysis?.repository_name ?? "repo-123");
  const statuses = await Promise.all(runIds.map((runId) => getRunStatus(runId)));
  const runRecords = statuses.filter((record): record is NonNullable<typeof record> => record !== null);

  const primaryLanguage = analysis?.primary_language ?? "Unknown";
  const commitCount = analysis?.recent_commits.length ?? 0;

  return (
    <section>
      <div className="page-header">
        <h1>Analysis Runs</h1>
        <p>
          Pipeline execution and run diagnostics for <span className="text-neon">{analysis?.repository_name ?? "connected repository"}</span>.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: "1rem", marginBottom: "1rem" }}>
        <p style={{ margin: "0 0 0.4rem" }}>
          Repository: <strong>{analysis?.repository_name ?? "not available"}</strong>
        </p>
        <p style={{ margin: 0, color: "var(--muted)" }}>
          Primary language {primaryLanguage}. Recent commits analyzed: {commitCount}. Health score: {analysis?.health.score ?? "N/A"}/100.
        </p>
      </div>

      {runRecords.length === 0 ? (
        <div className="glass-panel" style={{ padding: "1rem" }}>
          <p style={{ margin: 0 }}>
            No run records were returned for the inferred run IDs.
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gap: "1rem" }} aria-label="run-list-panel">
          {runRecords.map((run) => {
            const tone = statusTone(run.status);
            return (
              <div key={run.run_id} className="glass-panel" style={{ padding: "1rem", display: "grid", gap: "0.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.5rem" }}>
                  <h3 style={{ margin: 0, fontSize: "1.05rem" }}>{run.run_id}</h3>
                  <span className="pill medium" style={{ color: tone.color, borderColor: tone.color }}>
                    {tone.label}
                  </span>
                </div>
                <p style={{ margin: 0, color: "var(--muted)" }}>Updated at: {formatDate(run.updated_at)}</p>
                <p style={{ margin: 0 }}>{run.message ?? "No additional message provided."}</p>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
