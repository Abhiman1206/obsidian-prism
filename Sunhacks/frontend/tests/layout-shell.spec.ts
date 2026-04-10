import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import { vi } from "vitest";

import AppShell from "../components/layout/app-shell";
import HomePage from "../app/page";
import RunsPage from "../app/runs/page";

describe("app shell", () => {
  it("renders shared shell container and navigation links", () => {
    render(createElement(AppShell, null, createElement("div", null, "child")));

    expect(screen.getByTestId("app-shell")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Activity Runs" })).toHaveAttribute("href", "/runs");
    expect(screen.getByRole("link", { name: "Detailed Reports" })).toHaveAttribute("href", "/reports");
  });

  it("renders homepage placeholders", () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response);

    return HomePage({ searchParams: Promise.resolve({ run_id: "run-123" }) }).then((page) => {
      render(page);

      expect(screen.getByRole("heading", { name: "Intelligent Dashboard" })).toBeInTheDocument();
      expect(screen.getByText("No risk forecast data available for this run. Showing repository risk baseline KPIs.")).toBeInTheDocument();
    });
  });

  it("renders runs page features", () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        provider: "github",
        repository_url: "https://github.com/Abhiman1206/AI_APP",
        repository_name: "Abhiman1206/AI_APP",
        description: "Repo",
        default_branch: "main",
        stars: 0,
        forks: 0,
        watchers: 0,
        open_issues: 0,
        contributor_count: 1,
        archived: false,
        has_readme: true,
        primary_language: "Python",
        languages: [],
        topics: [],
        recent_commits: [],
        pushed_at: "2026-04-10T00:00:00Z",
        health: {
          score: 70,
          summary: "Moderate repository health with room for process improvements.",
        },
      }),
    } as Response);

    return RunsPage({ searchParams: Promise.resolve({}) }).then((page) => {
      render(page);

      expect(screen.getByRole("heading", { name: "Analysis Runs" })).toBeInTheDocument();
      expect(screen.getByLabelText("run-list-panel")).toBeInTheDocument();
    });
  });
});
