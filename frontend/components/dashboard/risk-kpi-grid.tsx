import React from "react";

import { RepositoryAnalysis } from "../../lib/contracts";
import { RiskDashboardSummary } from "../../lib/api/risk";

type RiskKpiGridProps = {
  summary: RiskDashboardSummary;
  analysis: RepositoryAnalysis | null;
};

type KpiCard = {
  label: string;
  value: string;
  subtitle?: string;
};

export function RiskKpiGrid({ summary, analysis }: RiskKpiGridProps) {
  const healthScore = analysis?.health?.score ?? null;

  const cards: KpiCard[] = [
    {
      label: "Repository Stars",
      value: String(analysis?.stars ?? 0),
      subtitle: `${analysis?.repository_name ?? "Repository"}`
    },
    {
      label: "Open Issues",
      value: String(analysis?.open_issues ?? 0),
      subtitle: `${analysis?.forks ?? 0} forks`
    },
    {
      label: "Avg. Confidence",
      value: `${summary.averageConfidencePercent}%`,
      subtitle: `${summary.highRiskCount} high risk components`
    },
    {
      label: "System Health",
      value: healthScore === null ? "Unknown" : healthScore >= 70 ? "Optimal" : "Warning",
      subtitle: healthScore === null ? "No score available" : `Score ${healthScore}/100`
    }
  ];

  return (
    <>
      {cards.map((card) => (
        <article key={card.label} className="glass-panel kpi-card">
          <h3>{card.label}</h3>
          <p className="kpi-value">{card.value}</p>
          {card.subtitle && <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--muted)' }}>{card.subtitle}</p>}
        </article>
      ))}
    </>
  );
}
