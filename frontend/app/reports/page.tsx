import React from "react";

import { ReportEvidencePanel } from "../../components/reports/report-evidence-panel";
import { ReportSummaryCard } from "../../components/reports/report-summary-card";
import { getExecutiveReports } from "../../lib/api/reports";

type ReportsPageProps = {
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

export default async function ReportsPage({ searchParams }: ReportsPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const runIdSource = Array.isArray(resolvedSearchParams.run_id)
    ? resolvedSearchParams.run_id[0]
    : resolvedSearchParams.run_id;
  const runId = runIdSource?.trim() || "latest";
  const repositoryUrl = normalizeRepositoryUrl(resolvedSearchParams.repository_url);

  const reports = await getExecutiveReports(runId, repositoryUrl);
  const selectedReport = reports[0];

  return (
    <section aria-label="Executive report content">
      <h1>Executive Report</h1>
      <p>Report scope: {runId}</p>

      {!selectedReport ? (
        <p>No executive reports available for this run.</p>
      ) : (
        <>
          <ReportSummaryCard report={selectedReport} />
          <ReportEvidencePanel claims={selectedReport.claims} />
        </>
      )}
    </section>
  );
}
