import React from "react";

import { analyzeRepository } from "../../lib/api/repositories";
import { PrivateRepoConsole } from "../../components/private-repo-console";

type RepositoryPageProps = {
  searchParams?: Promise<{
    repository_url?: string | string[];
  }>;
};

function formatBytes(sizeInBytes: number): string {
  if (!Number.isFinite(sizeInBytes) || sizeInBytes <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = sizeInBytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  const decimals = unitIndex === 0 ? 0 : 2;
  return `${value.toFixed(decimals)} ${units[unitIndex]}`;
}

function normalizeRepositoryUrl(raw: string | string[] | undefined): string | null {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : null;
}

export default async function RepositoryExplorerPage({ searchParams }: RepositoryPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const repositoryUrl = normalizeRepositoryUrl(resolvedSearchParams.repository_url);
  const analysis = repositoryUrl ? await analyzeRepository(repositoryUrl) : null;

  return (
    <section>
      <div className="page-header">
        <h1>Repository Explorer</h1>
        <p>
          Connected GitHub repository analysis and <span className="text-neon">engineering health insights</span>.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: "1rem", marginBottom: "1rem" }}>
        <PrivateRepoConsole defaultRepositoryUrl={repositoryUrl ?? ""} />
      </div>

      <div className="glass-panel" style={{ padding: "1rem", marginBottom: "1rem" }}>
        <form method="get" action="/repository" style={{ display: "grid", gap: "0.75rem" }}>
          <label htmlFor="repository_url" style={{ fontWeight: 600 }}>
            GitHub Repository URL
          </label>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <input
              id="repository_url"
              name="repository_url"
              type="text"
              defaultValue={repositoryUrl ?? ""}
              style={{
                flex: 1,
                minWidth: "240px",
                background: "rgba(0,0,0,0.2)",
                border: "1px solid var(--surface-border)",
                borderRadius: "8px",
                padding: "0.75rem 1rem",
                color: "var(--text)",
              }}
            />
            <button type="submit" className="btn-primary">
              Analyze Repository
            </button>
          </div>
        </form>
      </div>

      {analysis ? (
        <div style={{ display: "grid", gap: "1rem" }}>
          <div className="glass-panel" style={{ padding: "1rem", display: "grid", gap: "0.5rem" }}>
            <h2 style={{ margin: 0 }}>{analysis.repository_name}</h2>
            <p style={{ margin: 0, color: "var(--muted)" }}>
              {analysis.description ?? "No repository description available."}
            </p>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
              <span className="pill medium">Branch: {analysis.default_branch}</span>
              <span className="pill medium">Primary: {analysis.primary_language ?? "Unknown"}</span>
              <span className="pill medium">Health Score: {analysis.health.score}/100</span>
            </div>
            <p style={{ margin: 0, color: "var(--muted)" }}>{analysis.health.summary}</p>
          </div>

          <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>Stars</p>
              <strong style={{ fontSize: "1.4rem" }}>{analysis.stars}</strong>
            </div>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>Forks</p>
              <strong style={{ fontSize: "1.4rem" }}>{analysis.forks}</strong>
            </div>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>Watchers</p>
              <strong style={{ fontSize: "1.4rem" }}>{analysis.watchers}</strong>
            </div>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>Open Issues</p>
              <strong style={{ fontSize: "1.4rem" }}>{analysis.open_issues}</strong>
            </div>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>Contributors</p>
              <strong style={{ fontSize: "1.4rem" }}>{analysis.contributor_count}</strong>
            </div>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>File Count</p>
              <strong style={{ fontSize: "1.4rem" }}>{analysis.file_count}</strong>
            </div>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <p style={{ margin: "0 0 0.25rem", color: "var(--muted)" }}>
                Repository Size{" "}
                <span
                  title="Computed as the sum of git blob sizes from the default branch tree."
                  aria-label="Repository size calculation method"
                  style={{ fontSize: "0.75rem", cursor: "help" }}
                >
                  (i)
                </span>
              </p>
              <strong style={{ fontSize: "1.4rem" }}>{formatBytes(analysis.repository_size_bytes)}</strong>
            </div>
          </div>

          <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
            <div className="glass-panel" style={{ padding: "1rem" }}>
              <h3 style={{ marginTop: 0 }}>Language Breakdown</h3>
              {analysis.languages.length === 0 ? (
                <p style={{ color: "var(--muted)" }}>No language metrics available.</p>
              ) : (
                <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "0.4rem" }}>
                  {analysis.languages.slice(0, 6).map((language) => (
                    <li key={language.language} style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                      <span>{language.language}</span>
                      <span className="text-neon">{language.percentage.toFixed(2)}%</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="glass-panel" style={{ padding: "1rem" }}>
              <h3 style={{ marginTop: 0 }}>Recent Commits</h3>
              {analysis.recent_commits.length === 0 ? (
                <p style={{ color: "var(--muted)" }}>No recent commits returned from GitHub.</p>
              ) : (
                <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "0.7rem" }}>
                  {analysis.recent_commits.map((commit) => (
                    <li key={commit.sha}>
                      <p style={{ margin: 0, fontWeight: 600 }}>{commit.message}</p>
                      <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--muted)" }}>
                        {commit.author} • {commit.committed_at || "unknown time"}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-panel" style={{ padding: "1rem" }}>
          <p style={{ margin: 0 }}>
            {repositoryUrl
              ? "Analysis could not be generated. Verify the repository URL is public and that the backend API is running."
              : "Enter a repository URL and run analysis to view repository insights."}
          </p>
        </div>
      )}
    </section>
  );
}
