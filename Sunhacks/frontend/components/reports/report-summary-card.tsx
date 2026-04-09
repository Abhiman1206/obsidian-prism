import React from "react";

import { ExecutiveReportSummary } from "../../lib/contracts";

type ReportSummaryCardProps = {
  report: ExecutiveReportSummary;
};

export function ReportSummaryCard({ report }: ReportSummaryCardProps) {
  return (
    <article className="report-summary-card">
      <h2>Executive Summary</h2>
      <p>{report.executive_summary}</p>

      <h3>Top Risks</h3>
      {report.top_risks.length === 0 ? (
        <p>No high-priority components were returned for this run.</p>
      ) : (
        <ul>
          {report.top_risks.map((risk) => (
            <li key={risk.component_id}>
              {risk.component_id}: ${risk.expected_total_cost.toLocaleString()} expected cost
            </li>
          ))}
        </ul>
      )}

      <h3>Recommended Priorities</h3>
      {report.recommended_priorities.length === 0 ? (
        <p>No priority actions were generated for this run.</p>
      ) : (
        <ul>
          {report.recommended_priorities.map((priority) => (
            <li key={`${priority.component_id}-${priority.action}`}>
              {priority.action}
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
