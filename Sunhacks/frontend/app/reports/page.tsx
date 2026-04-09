import React from "react";

import { ReportEvidencePanel } from "../../components/reports/report-evidence-panel";
import { ReportSummaryCard } from "../../components/reports/report-summary-card";
import { getExecutiveReports } from "../../lib/api/reports";

type ReportsPageProps = {
  searchParams?: Promise<{
    run_id?: string | string[];
  }>;
};

export default async function ReportsPage({ searchParams }: ReportsPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const runIdSource = Array.isArray(resolvedSearchParams.run_id)
    ? resolvedSearchParams.run_id[0]
    : resolvedSearchParams.run_id;
  const runId = runIdSource?.trim() || "latest";

  const reports = await getExecutiveReports(runId);
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
