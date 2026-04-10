import {
  RepositoryAnalysis,
  RepositoryRegistrationRequest,
  RepositoryRegistrationResponse,
  RepositoryRevalidateRequest,
  RepositoryRevalidateResponse,
} from "../contracts";
import { buildAuthHeaders } from "./auth";
import { resolveApiBaseUrl } from "./base-url";

export async function analyzeRepository(repositoryUrl: string): Promise<RepositoryAnalysis | null> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/repositories/analyze`, {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ repository_url: repositoryUrl }),
    });

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as RepositoryAnalysis;
    if (!payload || typeof payload !== "object") {
      return null;
    }

    return payload;
  } catch {
    return null;
  }
}

export async function registerRepository(
  payload: RepositoryRegistrationRequest,
): Promise<RepositoryRegistrationResponse | null> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/repositories/register`, {
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

    const body = (await response.json()) as RepositoryRegistrationResponse;
    if (!body || typeof body !== "object") {
      return null;
    }

    return body;
  } catch {
    return null;
  }
}

export async function revalidateRepositoryAccess(
  payload: RepositoryRevalidateRequest,
): Promise<RepositoryRevalidateResponse | null> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}/api/repositories/revalidate`, {
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

    const body = (await response.json()) as RepositoryRevalidateResponse;
    if (!body || typeof body !== "object") {
      return null;
    }

    return body;
  } catch {
    return null;
  }
}
