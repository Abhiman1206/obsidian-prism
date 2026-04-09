import { ExecutiveReportSummary } from "../contracts";

export async function getExecutiveReports(runId: string = "latest"): Promise<ExecutiveReportSummary[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

  try {
    const response = await fetch(`${baseUrl}/api/executive-reports/${runId}`, {
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
