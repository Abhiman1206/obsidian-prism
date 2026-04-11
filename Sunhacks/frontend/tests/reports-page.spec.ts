import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ReportsPage from "../app/reports/page";

function mockReportsResponse(payload: unknown) {
  vi.spyOn(global, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);

    if (url.includes("/api/executive-reports/")) {
      return {
        ok: true,
        json: async () => payload,
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

describe("reports page", () => {
  it("renders executive summary, top risks, and recommended priorities", async () => {
    mockReportsResponse([
      {
        report_id: "report-1",
        run_id: "run-123",
        executive_summary: "The API layer is the primary risk concentration.",
        cost_of_inaction_estimate: 95000,
        top_risks: [
          {
            component_id: "api-gateway",
            expected_total_cost: 70000,
            expected_engineering_hours: 120,
            expected_downtime_hours: 16,
          },
        ],
        cost_of_inaction: {
          expected_total_cost: 95000,
          summary: "Cost growth expected over the next 90 days.",
        },
        recommended_priorities: [
          {
            component_id: "api-gateway",
            action: "Increase integration test coverage for high-risk paths.",
            expected_total_cost: 70000,
          },
        ],
        claims: [
          {
            claim_id: "claim-1",
            claim_text: "Release churn is driving outage probability.",
            lineage_refs: ["risk_forecast:api-gateway", "health_score:api-gateway"],
          },
        ],
        generated_at: "2026-04-10T00:00:00Z",
      },
    ]);

    render(await ReportsPage({ searchParams: Promise.resolve({ run_id: "run-123" }) }));

    expect(screen.getByRole("heading", { name: "Executive Report" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Executive report content" })).toBeInTheDocument();
    expect(screen.getByText("The API layer is the primary risk concentration.")).toBeInTheDocument();
    expect(screen.getByText("Top Risks")).toBeInTheDocument();
    expect(screen.getByText("Recommended Priorities")).toBeInTheDocument();
  });

  it("reveals claim text and lineage references when evidence is expanded", async () => {
    mockReportsResponse([
      {
        report_id: "report-1",
        run_id: "run-123",
        executive_summary: "Evidence drill-down should be available.",
        cost_of_inaction_estimate: 95000,
        top_risks: [],
        cost_of_inaction: {
          expected_total_cost: 95000,
          summary: "Cost growth expected over the next 90 days.",
        },
        recommended_priorities: [],
        claims: [
          {
            claim_id: "claim-1",
            claim_text: "Release churn is driving outage probability.",
            lineage_refs: ["risk_forecast:api-gateway", "health_score:api-gateway"],
          },
        ],
        generated_at: "2026-04-10T00:00:00Z",
      },
    ]);

    render(await ReportsPage({ searchParams: Promise.resolve({ run_id: "run-123" }) }));

    fireEvent.click(screen.getByRole("button", { name: "Toggle evidence for claim-1" }));

    expect(screen.getByText("Release churn is driving outage probability.")).toBeInTheDocument();
    expect(screen.getByText("risk_forecast:api-gateway")).toBeInTheDocument();
    expect(screen.getByText("health_score:api-gateway")).toBeInTheDocument();
  });

  it("renders empty-state messaging for unknown or empty runs", async () => {
    mockReportsResponse([]);

    render(await ReportsPage({ searchParams: Promise.resolve({ run_id: "run-empty" }) }));

    expect(screen.getByText("No executive reports available yet.")).toBeInTheDocument();
  });

  it("renders empty-state messaging when no report exists and run_id is missing", async () => {
    mockReportsResponse([]);

    render(await ReportsPage({ searchParams: Promise.resolve({}) }));

    expect(screen.getByText("No executive reports available yet.")).toBeInTheDocument();
  });
});
