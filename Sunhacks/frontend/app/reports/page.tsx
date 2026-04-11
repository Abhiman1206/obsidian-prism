import React from "react";
import Link from "next/link";

import { ReportEvidencePanel } from "../../components/reports/report-evidence-panel";
import { ReportSummaryCard } from "../../components/reports/report-summary-card";
import { getExecutiveReportPdfUrl } from "../../lib/api/reports";
import { getExecutiveReports } from "../../lib/api/reports";
import { getLatestExecutiveReport } from "../../lib/api/reports";
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
  const requestedRunId = runIdSource?.trim() || "";
  const repositoryUrl = repositoryUrlSource?.trim() || "";

  const runsParams = new URLSearchParams();
  if (repositoryUrl) {
    runsParams.set("repository_url", repositoryUrl);
  }
  const runsHref = runsParams.toString() ? `/runs?${runsParams.toString()}` : "/runs";

  const latestReport = await getLatestExecutiveReport();
  const reports = requestedRunId ? await getExecutiveReports(requestedRunId) : [];
  const selectedReport = reports[0] ?? latestReport;
  const runId = selectedReport?.run_id || requestedRunId;
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

      {!selectedReport ? (
        <p>No executive reports available yet.</p>
      ) : (
        <>
          <ReportSummaryCard report={selectedReport} />
          <ReportEvidencePanel claims={selectedReport.claims} />
        </>
      )}

      {legacyPdfUrl ? (
        <section className="report-pdf-section" aria-label="Executive report PDFs">
          <h2>Report PDFs</h2>
          <div className="report-pdf-grid">
            <article className="report-pdf-item" aria-label="Technical report PDF">
              <h3>Technical Report</h3>
              <iframe src={technicalPdfUrl || legacyPdfUrl} title="Technical report PDF" className="report-pdf-frame" />
            </article>
            <article className="report-pdf-item" aria-label="Non-technical report PDF">
              <h3>Non-Technical Report</h3>
              <iframe
                src={nonTechnicalPdfUrl || legacyPdfUrl}
                title="Non-technical report PDF"
                className="report-pdf-frame"
              />
            </article>
          </div>
        </section>
      ) : (
        <section className="report-pdf-section" aria-label="Executive report PDF">
          <h2>Report PDFs</h2>
          <p>
            Trigger a fresh analysis from the <Link href={runsHref}>runs page</Link> to generate new technical and
            non-technical PDFs.
          </p>
        </section>
      )}
    </section>
  );
}
