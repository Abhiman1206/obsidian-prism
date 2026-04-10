import { RunStatus } from "../contracts";
import { resolveApiBaseUrl } from "./base-url";

export interface RunRecord {
  run_id: string;
  status: RunStatus;
  updated_at: string;
  message: string | null;
}

export async function getRunStatus(runId: string): Promise<RunRecord | null> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/runs/${runId}`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as RunRecord;
    if (!payload || typeof payload !== "object") {
      return null;
    }

    return payload;
  } catch {
    return null;
  }
}

export function inferRunIds(repositoryId: string): string[] {
  const safe = repositoryId.replaceAll("/", "-");
  return [
    `run-${safe}`,
    "run-latest",
    "run-123",
  ];
}
