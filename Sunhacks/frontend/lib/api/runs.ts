import { CreateRunRequest, CreateRunResponse, RunStatus } from "../contracts";
import { buildAuthHeaders } from "./auth";
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

export async function createRun(payload: CreateRunRequest): Promise<CreateRunResponse | null> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/runs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...buildAuthHeaders(),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      return null;
    }

    const body = (await response.json()) as CreateRunResponse;
    if (!body || typeof body !== "object") {
      return null;
    }

    return body;
  } catch {
    return null;
  }
}
