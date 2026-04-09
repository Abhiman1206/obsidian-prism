import React from "react";

import { RiskDashboardSummary } from "../../lib/api/risk";

type RiskKpiGridProps = {
  summary: RiskDashboardSummary;
};

type KpiCard = {
  label: string;
  value: string;
};

export function RiskKpiGrid({ summary }: RiskKpiGridProps) {
  const cards: KpiCard[] = [
    {
      label: "Total Components",
      value: String(summary.totalComponents),
    },
    {
      label: "High Risk Components",
      value: String(summary.highRiskCount),
    },
    {
      label: "Average Confidence",
      value: `${summary.averageConfidencePercent}%`,
    },
  ];

  return (
    <div className="dashboard-kpi-grid" aria-label="Risk dashboard KPI summary">
      {cards.map((card) => (
        <article key={card.label} className="dashboard-kpi-card">
          <h2>{card.label}</h2>
          <p>{card.value}</p>
        </article>
      ))}
    </div>
  );
}
