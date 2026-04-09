import React from "react";

import { RiskKpiGrid } from "../components/dashboard/risk-kpi-grid";
import { RiskTable } from "../components/dashboard/risk-table";
import { buildRiskDashboardSummary, getRiskForecasts } from "../lib/api/risk";

type HomePageProps = {
  searchParams?: Promise<{
    run_id?: string | string[];
  }>;
};

export default async function HomePage({ searchParams }: HomePageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};

  const runIdSource = Array.isArray(resolvedSearchParams.run_id)
    ? resolvedSearchParams.run_id[0]
    : resolvedSearchParams.run_id;
  const runId = runIdSource?.trim() || "latest";
  const forecasts = await getRiskForecasts(runId);
  const summary = buildRiskDashboardSummary(forecasts);

  return (
    <section>
      <h1>Repository Risk Dashboard</h1>
      <p>Risk outlook for run scope: {runId}</p>

      <RiskKpiGrid summary={summary} />

      {forecasts.length === 0 ? (
        <p>No risk forecast data available for this run.</p>
      ) : (
        <RiskTable forecasts={forecasts} />
      )}
    </section>
  );
}
