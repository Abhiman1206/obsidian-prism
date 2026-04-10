import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import RepositoryPage from "../app/repository/page";

function mockAnalysisResponse(payload: unknown) {
  vi.spyOn(global, "fetch").mockResolvedValue({
    ok: true,
    json: async () => payload,
  } as Response);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("repository page", () => {
  it("renders repository analysis details for the provided URL", async () => {
    mockAnalysisResponse({
      provider: "github",
      repository_url: "https://github.com/Abhiman1206/AI_APP",
      repository_name: "Abhiman1206/AI_APP",
      description: "AI repository",
      default_branch: "main",
      stars: 12,
      forks: 4,
      watchers: 3,
      open_issues: 1,
      contributor_count: 5,
      archived: false,
      has_readme: true,
      primary_language: "Python",
      languages: [
        { language: "Python", bytes: 1000, percentage: 80 },
        { language: "Jupyter Notebook", bytes: 250, percentage: 20 },
      ],
      topics: ["ai", "ml"],
      recent_commits: [
        {
          sha: "abc123",
          message: "Add inference flow",
          author: "abhiman",
          committed_at: "2026-04-10T00:00:00Z",
          url: "https://github.com/Abhiman1206/AI_APP/commit/abc123",
        },
      ],
      pushed_at: "2026-04-10T00:00:00Z",
      health: {
        score: 84,
        summary: "Strong repository health with active maintenance signals.",
      },
    });

    render(await RepositoryPage({ searchParams: Promise.resolve({ repository_url: "https://github.com/Abhiman1206/AI_APP.git" }) }));

    expect(screen.getByRole("heading", { name: "Repository Explorer" })).toBeInTheDocument();
    expect(screen.getByText("Abhiman1206/AI_APP")).toBeInTheDocument();
    expect(screen.getByText("Health Score: 84/100")).toBeInTheDocument();
    expect(screen.getByText("Language Breakdown")).toBeInTheDocument();
    expect(screen.getByText("Recent Commits")).toBeInTheDocument();
    expect(screen.getByText("Add inference flow")).toBeInTheDocument();
  });

  it("renders fallback messaging when analysis is unavailable", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      json: async () => ({}),
    } as Response);

    render(await RepositoryPage({ searchParams: Promise.resolve({}) }));

    expect(
      screen.getByText(
        "Analysis could not be generated. Verify the repository URL is public and that the backend API is running.",
      ),
    ).toBeInTheDocument();
  });
});
