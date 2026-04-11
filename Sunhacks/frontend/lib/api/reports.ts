import { ExecutiveReportSummary } from "../contracts";
import { resolveApiBaseUrl } from "./base-url";

export async function getLatestExecutiveReport(): Promise<ExecutiveReportSummary | null> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/executive-reports/latest`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as ExecutiveReportSummary | null;
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      return null;
    }

    if (typeof payload.run_id !== "string" || typeof payload.report_id !== "string") {
      return null;
    }

    return payload;
  } catch {
    return null;
  }
}

export async function getExecutiveReports(runId: string): Promise<ExecutiveReportSummary[]> {
  const baseUrl = resolveApiBaseUrl();
  const normalizedRunId = runId.trim();
  if (!normalizedRunId) {
    return [];
  }

  try {
    const response = await fetch(`${baseUrl}/api/executive-reports/${encodeURIComponent(normalizedRunId)}`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as ExecutiveReportSummary[];
    if (!Array.isArray(payload)) {
      return [];
    }

    return [...payload].sort((left, right) => right.generated_at.localeCompare(left.generated_at));
  } catch {
    return [];
  }
}

export function getExecutiveReportPdfUrl(runId: string, reportId: string): string {
  const baseUrl = resolveApiBaseUrl();
  const encodedRunId = encodeURIComponent(runId);
  const encodedReportId = encodeURIComponent(reportId);
  return `${baseUrl}/api/executive-reports/${encodedRunId}/${encodedReportId}/pdf`;
}

export function getTechnicalReportPdfUrl(runId: string, reportId: string): string {
  const baseUrl = resolveApiBaseUrl();
  const encodedRunId = encodeURIComponent(runId);
  const encodedReportId = encodeURIComponent(reportId);
  return `${baseUrl}/api/executive-reports/${encodedRunId}/${encodedReportId}/technical-pdf`;
}

export function getNonTechnicalReportPdfUrl(runId: string, reportId: string): string {
  const baseUrl = resolveApiBaseUrl();
  const encodedRunId = encodeURIComponent(runId);
  const encodedReportId = encodeURIComponent(reportId);
  return `${baseUrl}/api/executive-reports/${encodedRunId}/${encodedReportId}/executive-pdf`;
}
