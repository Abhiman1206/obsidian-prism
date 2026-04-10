import { ExecutiveReportSummary } from "../contracts";
import { analyzeRepository } from "./repositories";
import { resolveApiBaseUrl } from "./base-url";

const DEFAULT_REPOSITORY_URL = "https://github.com/Abhiman1206/AI_APP.git";

type CreateRunResponse = {
  run_id: string;
  status: string;
  created_at: string;
};

function createFallbackReportFromRepositoryAnalysis(runId: string, repositoryUrl: string): Promise<ExecutiveReportSummary[] | null> {
  return analyzeRepository(repositoryUrl).then((analysis) => {
    if (!analysis) {
      return null;
    }

    const healthGap = Math.max(0, 100 - analysis.health.score);
    const issuesCost = analysis.open_issues * 900;
    const stabilityCost = healthGap * 120;
    const contributorRiskCost = Math.max(0, 3 - analysis.contributor_count) * 3000;
    const totalExposure = issuesCost + stabilityCost + contributorRiskCost;

    const topRisks = [
      {
        component_id: "issue-backlog",
        expected_total_cost: issuesCost,
        expected_engineering_hours: Math.max(8, analysis.open_issues * 2),
        expected_downtime_hours: Number((analysis.open_issues * 0.2).toFixed(1)),
      },
      {
        component_id: "system-health",
        expected_total_cost: stabilityCost,
        expected_engineering_hours: Math.max(6, Math.round(healthGap / 2)),
        expected_downtime_hours: Number((healthGap / 25).toFixed(1)),
      },
      {
        component_id: "ownership-capacity",
        expected_total_cost: contributorRiskCost,
        expected_engineering_hours: Math.max(4, (3 - analysis.contributor_count) * 6),
        expected_downtime_hours: Number((Math.max(0, 3 - analysis.contributor_count) * 1.2).toFixed(1)),
      },
    ].filter((risk) => risk.expected_total_cost > 0);

    const generatedAt = analysis.pushed_at ?? new Date().toISOString();

    const report: ExecutiveReportSummary = {
      report_id: `repo-fallback-${analysis.repository_name.replace(/[\/]/g, "-")}`,
      run_id: runId,
      executive_summary: `${analysis.repository_name} is currently at health score ${analysis.health.score}/100 with ${analysis.open_issues} open issues and ${analysis.contributor_count} active contributors. Projected 90-day cost of inaction is estimated at $${totalExposure.toLocaleString()} based on backlog pressure, health degradation, and ownership concentration risk. Prioritize issue-burndown and reliability hardening first to reduce operational exposure.`,
      cost_of_inaction_estimate: totalExposure,
      top_risks: topRisks,
      cost_of_inaction: {
        expected_total_cost: totalExposure,
        summary: "Estimate derived from live repository analysis signals: open issues, repository health score, and contributor concentration.",
      },
      recommended_priorities: [
        {
          component_id: "issue-backlog",
          action: `Close or triage at least ${Math.max(5, Math.ceil(analysis.open_issues * 0.35))} high-impact open issues in the next sprint.`,
          expected_total_cost: issuesCost,
        },
        {
          component_id: "system-health",
          action: "Raise repository health score through reliability tests, CI hardening, and release quality gates.",
          expected_total_cost: stabilityCost,
        },
        {
          component_id: "ownership-capacity",
          action: "Expand code ownership coverage to reduce key-person risk and incident response bottlenecks.",
          expected_total_cost: contributorRiskCost,
        },
      ].filter((item) => item.expected_total_cost > 0),
      claims: [
        {
          claim_id: "claim-1",
          claim_text: `Open issue load (${analysis.open_issues}) materially contributes to delivery and incident exposure.`,
          lineage_refs: [`${analysis.repository_name}:open_issues`],
        },
        {
          claim_id: "claim-2",
          claim_text: `Repository health score (${analysis.health.score}/100) indicates reliability-improvement opportunity.`,
          lineage_refs: [`${analysis.repository_name}:health_score`],
        },
        {
          claim_id: "claim-3",
          claim_text: `Contributor count (${analysis.contributor_count}) may increase ownership concentration risk.`,
          lineage_refs: [`${analysis.repository_name}:contributor_count`],
        },
      ],
      generated_at: generatedAt,
    };

    return [report];
  });
}

async function evaluateRepositoryAndFetchReports(repositoryUrl: string): Promise<ExecutiveReportSummary[] | null> {
  const analysis = await analyzeRepository(repositoryUrl);
  if (!analysis) {
    return null;
  }

  const baseUrl = resolveApiBaseUrl();
  const runRequestBody = {
    repository_id: analysis.repository_name,
    provider: "github",
    branch: analysis.default_branch || null,
  };

  const runResponse = await fetch(`${baseUrl}/api/runs`, {
    method: "POST",
    cache: "no-store",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(runRequestBody),
  });

  if (!runResponse.ok) {
    return null;
  }

  const runPayload = (await runResponse.json()) as CreateRunResponse;
  if (!runPayload?.run_id) {
    return null;
  }

  const reportsResponse = await fetch(`${baseUrl}/api/executive-reports/${encodeURIComponent(runPayload.run_id)}`, {
    cache: "no-store",
    headers: {
      Accept: "application/json",
    },
  });

  if (!reportsResponse.ok) {
    return null;
  }

  const generatedReports = (await reportsResponse.json()) as ExecutiveReportSummary[];
  if (!Array.isArray(generatedReports) || generatedReports.length === 0) {
    return null;
  }

  return [...generatedReports].sort((left, right) => right.generated_at.localeCompare(left.generated_at));
}

export async function getExecutiveReports(
  runId: string = "latest",
  repositoryUrl: string = DEFAULT_REPOSITORY_URL,
): Promise<ExecutiveReportSummary[]> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/executive-reports/${runId}`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      const evaluatedReports = await evaluateRepositoryAndFetchReports(repositoryUrl);
      if (evaluatedReports && evaluatedReports.length > 0) {
        return evaluatedReports;
      }
      return (await createFallbackReportFromRepositoryAnalysis(runId, repositoryUrl)) ?? [];
    }

    const payload = (await response.json()) as ExecutiveReportSummary[];
    if (!Array.isArray(payload)) {
      return (await createFallbackReportFromRepositoryAnalysis(runId, repositoryUrl)) ?? [];
    }

    if (payload.length === 0) {
      const evaluatedReports = await evaluateRepositoryAndFetchReports(repositoryUrl);
      if (evaluatedReports && evaluatedReports.length > 0) {
        return evaluatedReports;
      }
      return (await createFallbackReportFromRepositoryAnalysis(runId, repositoryUrl)) ?? [];
    }

    return [...payload].sort((left, right) => right.generated_at.localeCompare(left.generated_at));
  } catch {
    const evaluatedReports = await evaluateRepositoryAndFetchReports(repositoryUrl);
    if (evaluatedReports && evaluatedReports.length > 0) {
      return evaluatedReports;
    }
    return (await createFallbackReportFromRepositoryAnalysis(runId, repositoryUrl)) ?? [];
  }
}

export function getExecutiveReportPdfUrl(runId: string, reportId: string): string {
  const baseUrl = resolveApiBaseUrl();
  const encodedRunId = encodeURIComponent(runId);
  const encodedReportId = encodeURIComponent(reportId);
  return `${baseUrl}/api/executive-reports/${encodedRunId}/${encodedReportId}/pdf`;
}
