import React from "react";

import { RiskKpiGrid } from "../components/dashboard/risk-kpi-grid";
import { analyzeRepository } from "../lib/api/repositories";
import { RiskTable } from "../components/dashboard/risk-table";
import { buildRiskDashboardSummary, getRiskForecasts } from "../lib/api/risk";

type HomePageProps = {
  searchParams?: Promise<{
    run_id?: string | string[];
    repository_url?: string | string[];
  }>;
};

const DEFAULT_REPOSITORY_URL = "https://github.com/Abhiman1206/AI_APP.git";

function normalizeRepositoryUrl(raw: string | string[] | undefined): string {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : DEFAULT_REPOSITORY_URL;
}

function buildCommitActivity(commits: Array<{ committed_at: string }>): number[] {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const bins = new Array<number>(14).fill(0);
  for (const commit of commits) {
    const committedAt = new Date(commit.committed_at);
    if (Number.isNaN(committedAt.getTime())) {
      continue;
    }

    committedAt.setHours(0, 0, 0, 0);
    const diffDays = Math.floor((today.getTime() - committedAt.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays >= 0 && diffDays < 14) {
      const idx = 13 - diffDays;
      bins[idx] += 1;
    }
  }

  return bins;
}

function ActivityChart({ bars }: { bars: number[] }) {
  const max = Math.max(...bars, 1);

  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', height: '150px', gap: '8px', padding: '1rem 0' }}>
      {bars.map((count, i) => (
        <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <div 
            style={{ 
              width: '100%', 
              height: `${Math.max(8, Math.round((count / max) * 100))}%`, 
              background: `linear-gradient(180deg, var(--neon) 0%, transparent 100%)`,
              borderRadius: '4px 4px 0 0',
              opacity: 0.8
            }}
            title={`${count} commit${count === 1 ? '' : 's'}`}
          ></div>
        </div>
      ))}
    </div>
  );
}

type RepositoryKpiItem = {
  label: string;
  value: string;
};

function RepositoryKpiGrid({ items }: { items: RepositoryKpiItem[] }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap: "0.75rem",
        marginTop: "0.5rem",
      }}
    >
      {items.map((item) => (
        <div
          key={item.label}
          style={{
            border: "1px solid var(--surface-border)",
            borderRadius: "10px",
            padding: "0.8rem",
            background: "rgba(255,255,255,0.02)",
          }}
        >
          <p style={{ margin: 0, color: "var(--muted)", fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.4px" }}>
            {item.label}
          </p>
          <p style={{ margin: "0.35rem 0 0", fontSize: "1.2rem", fontWeight: 700 }}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};

  const runIdSource = Array.isArray(resolvedSearchParams.run_id)
    ? resolvedSearchParams.run_id[0]
    : resolvedSearchParams.run_id;
  const runId = runIdSource?.trim() || "latest";

  const repositoryUrl = normalizeRepositoryUrl(resolvedSearchParams.repository_url);
  const analysis = await analyzeRepository(repositoryUrl);

  const forecasts = await getRiskForecasts(runId);
  const summary = buildRiskDashboardSummary(forecasts);
  const commitActivity = buildCommitActivity(analysis?.recent_commits ?? []);
  const hasCommitSeries = commitActivity.some((value) => value > 0);

  const activityFallbackKpis: RepositoryKpiItem[] = [
    { label: "Stars", value: String(analysis?.stars ?? 0) },
    { label: "Forks", value: String(analysis?.forks ?? 0) },
    { label: "Open Issues", value: String(analysis?.open_issues ?? 0) },
    { label: "Contributors", value: String(analysis?.contributor_count ?? 0) },
    { label: "Primary Language", value: analysis?.primary_language ?? "Unknown" },
    { label: "Health Score", value: analysis?.health?.score !== undefined ? `${analysis.health.score}/100` : "N/A" },
  ];

  const riskFallbackKpis: RepositoryKpiItem[] = [
    {
      label: "Repo Health",
      value: analysis?.health?.score !== undefined ? `${analysis.health.score}/100` : "N/A",
    },
    {
      label: "Readme",
      value: analysis?.has_readme ? "Present" : "Missing",
    },
    {
      label: "Default Branch",
      value: analysis?.default_branch ?? "Unknown",
    },
    {
      label: "Archived",
      value: analysis?.archived ? "Yes" : "No",
    },
  ];

  return (
    <section>
      <div className="page-header">
        <h1>Intelligent Dashboard</h1>
        <p>Command Center • Run Scope: <span className="text-neon">{runId}</span></p>
      </div>

      <div className="dashboard-grid">
        <RiskKpiGrid summary={summary} analysis={analysis} />
        
        <div className="glass-panel" style={{ gridColumn: 'span 12', padding: '1.5rem', marginTop: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontWeight: 600 }}>Repository Activity & Commits</h3>
            <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>Last 14 Days</span>
          </div>
          {analysis?.recent_commits && analysis.recent_commits.length > 0 && hasCommitSeries ? (
            <ActivityChart bars={commitActivity} />
          ) : (
            <>
              <p style={{ margin: 0, color: 'var(--muted)' }}>
                No commit activity detected in the last 14 days. Showing repository KPI snapshot instead.
              </p>
              <RepositoryKpiGrid items={activityFallbackKpis} />
            </>
          )}
        </div>

        <div className="glass-panel" style={{ gridColumn: 'span 12', padding: '1.5rem', marginTop: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
             <h3 style={{ margin: 0, fontWeight: 600 }}>Risk Outlook</h3>
             <button className="btn-glass" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>View All</button>
          </div>
          {forecasts.length === 0 ? (
            <>
              <p style={{ margin: 0, color: 'var(--muted)' }}>No risk forecast data available for this run. Showing repository risk baseline KPIs.</p>
              <RepositoryKpiGrid items={riskFallbackKpis} />
            </>
          ) : (
            <RiskTable forecasts={forecasts} />
          )}
        </div>
      </div>
    </section>
  );
}
