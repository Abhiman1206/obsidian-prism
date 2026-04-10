import { render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import HomePage from "../app/page";

const analysisPayload = {
  provider: "github",
  repository_url: "https://github.com/Abhiman1206/AI_APP.git",
  repository_name: "Abhiman1206/AI_APP",
  description: "Test repository",
  default_branch: "main",
  stars: 42,
  forks: 7,
  watchers: 15,
  open_issues: 3,
  contributor_count: 5,
  archived: false,
  has_readme: true,
  primary_language: "TypeScript",
  languages: [],
  topics: [],
  recent_commits: [
    {
      sha: "abc123",
      message: "feat: live metrics",
      author: "dev",
      committed_at: new Date().toISOString(),
      url: "https://github.com/Abhiman1206/AI_APP/commit/abc123",
    },
  ],
  pushed_at: new Date().toISOString(),
  health: {
    score: 70,
    summary: "Repository health score is 70/100.",
  },
};

function mockDashboardResponses(riskPayload: unknown, repositoryPayload: unknown = analysisPayload) {
  vi.spyOn(global, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/risk-forecasts/")) {
      return {
        ok: true,
        json: async () => riskPayload,
      } as Response;
    }

    if (url.includes("/api/repositories/analyze")) {
      return {
        ok: true,
        json: async () => repositoryPayload,
      } as Response;
    }

    return {
      ok: false,
      json: async () => ({}),
    } as Response;
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("dashboard page", () => {
  it("renders ranked component rows in descending risk order", async () => {
    mockDashboardResponses([
      {
        component_id: "worker-engine",
        horizon_days: 90,
        risk_probability: 0.61,
        confidence: 0.81,
        top_signals: [],
      },
      {
        component_id: "api-gateway",
        horizon_days: 90,
        risk_probability: 0.82,
        confidence: 0.76,
        top_signals: [],
      },
      {
        component_id: "ui-console",
        horizon_days: 90,
        risk_probability: 0.34,
        confidence: 0.74,
        top_signals: [],
      },
    ]);

    render(await HomePage({ searchParams: Promise.resolve({ run_id: "run-123" }) }));

    const rows = screen.getAllByRole("row").slice(1);
    expect(within(rows[0]).getByText("api-gateway")).toBeInTheDocument();
    expect(within(rows[1]).getByText("worker-engine")).toBeInTheDocument();
    expect(within(rows[2]).getByText("ui-console")).toBeInTheDocument();
  });

  it("renders KPI cards from risk data", async () => {
    mockDashboardResponses([
      {
        component_id: "api-gateway",
        horizon_days: 90,
        risk_probability: 0.82,
        confidence: 0.76,
        top_signals: [],
      },
      {
        component_id: "worker-engine",
        horizon_days: 90,
        risk_probability: 0.61,
        confidence: 0.81,
        top_signals: [],
      },
      {
        component_id: "ui-console",
        horizon_days: 90,
        risk_probability: 0.34,
        confidence: 0.74,
        top_signals: [],
      },
    ]);

    render(await HomePage({ searchParams: Promise.resolve({ run_id: "run-123" }) }));

    expect(screen.getByText("Repository Stars")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Open Issues")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Avg. Confidence")).toBeInTheDocument();
    expect(screen.getByText("77%"))
      .toBeInTheDocument();
    expect(screen.getByRole("table", { name: "Ranked risk components" })).toBeInTheDocument();
  });

  it("renders empty-state copy when API returns no records", async () => {
    mockDashboardResponses([]);

    render(await HomePage({ searchParams: Promise.resolve({ run_id: "run-empty" }) }));

    expect(screen.getByText("No risk forecast data available for this run. Showing repository risk baseline KPIs.")).toBeInTheDocument();
  });
});
