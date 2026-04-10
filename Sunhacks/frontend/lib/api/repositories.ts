import { RepositoryAnalysis } from "../contracts";
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
