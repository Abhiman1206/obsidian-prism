import React from "react";
import Link from "next/link";

import { ReportEvidencePanel } from "../../components/reports/report-evidence-panel";
import { ReportSummaryCard } from "../../components/reports/report-summary-card";
import { getExecutiveReportPdfUrl } from "../../lib/api/reports";
import { getExecutiveReports } from "../../lib/api/reports";
import { getNonTechnicalReportPdfUrl } from "../../lib/api/reports";
import { getTechnicalReportPdfUrl } from "../../lib/api/reports";

type ReportsPageProps = {
  searchParams?: Promise<{
    run_id?: string | string[];
    repository_url?: string | string[];
  }>;
};

export default async function ReportsPage({ searchParams }: ReportsPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const runIdSource = Array.isArray(resolvedSearchParams.run_id)
    ? resolvedSearchParams.run_id[0]
    : resolvedSearchParams.run_id;
  const repositoryUrlSource = Array.isArray(resolvedSearchParams.repository_url)
    ? resolvedSearchParams.repository_url[0]
    : resolvedSearchParams.repository_url;
  const runId = runIdSource?.trim() || "";
  const repositoryUrl = repositoryUrlSource?.trim() || "";

  const runsParams = new URLSearchParams();
  if (repositoryUrl) {
    runsParams.set("repository_url", repositoryUrl);
  }
  const runsHref = runsParams.toString() ? `/runs?${runsParams.toString()}` : "/runs";

  const reports = await getExecutiveReports(runId);
  const selectedReport = reports[0];
  const legacyPdfUrl = selectedReport
    ? getExecutiveReportPdfUrl(selectedReport.run_id || runId, selectedReport.report_id)
    : null;
  const technicalPdfUrl = selectedReport
    ? getTechnicalReportPdfUrl(selectedReport.run_id || runId, selectedReport.report_id)
    : null;
  const nonTechnicalPdfUrl = selectedReport
    ? getNonTechnicalReportPdfUrl(selectedReport.run_id || runId, selectedReport.report_id)
    : null;

  return (
    <section aria-label="Executive report content">
      <h1>Executive Report</h1>
      <p>Report scope: {runId || "not selected"}</p>

      {!runId ? (
        <p>
          Select a run first from the <Link href={runsHref}>runs page</Link> to view an executive report.
        </p>
      ) : !selectedReport ? (
        <p>No executive reports available for this run.</p>
      ) : (
        <>
          <ReportSummaryCard report={selectedReport} />
          <ReportEvidencePanel claims={selectedReport.claims} />

          {legacyPdfUrl ? (
            <section className="report-pdf-section" aria-label="Executive report PDF">
              <h2>Generate Report PDFs</h2>
              <div className="report-pdf-actions">
                <a href={technicalPdfUrl || legacyPdfUrl} target="_blank" rel="noreferrer" className="report-pdf-link">
                  Generate Technical Member PDF
                </a>
                <a href={nonTechnicalPdfUrl || legacyPdfUrl} target="_blank" rel="noreferrer" className="report-pdf-link">
                  Generate Non-Technical Member PDF
                </a>
                <a href={nonTechnicalPdfUrl || legacyPdfUrl} download className="report-pdf-link">
                  Download Non-Technical PDF
                </a>
              </div>
              <iframe
                src={nonTechnicalPdfUrl || legacyPdfUrl}
                title="Non-technical report PDF preview"
                className="report-pdf-frame"
              />
            </section>
          ) : null}
        </>
      )}
    </section>
  );
}
