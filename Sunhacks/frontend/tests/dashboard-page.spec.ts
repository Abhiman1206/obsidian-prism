import { render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import HomePage from "../app/page";

function mockRiskResponse(payload: unknown) {
  vi.spyOn(global, "fetch").mockResolvedValue({
    ok: true,
    json: async () => payload,
  } as Response);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("dashboard page", () => {
  it("renders ranked component rows in descending risk order", async () => {
    mockRiskResponse([
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

    render(await HomePage({ searchParams: { run_id: "run-123" } }));

    const rows = screen.getAllByRole("row").slice(1);
    expect(within(rows[0]).getByText("api-gateway")).toBeInTheDocument();
    expect(within(rows[1]).getByText("worker-engine")).toBeInTheDocument();
    expect(within(rows[2]).getByText("ui-console")).toBeInTheDocument();
  });

  it("renders KPI cards from risk data", async () => {
    mockRiskResponse([
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

    render(await HomePage({ searchParams: { run_id: "run-123" } }));

    expect(screen.getByText("Total Components")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("High Risk Components")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("Average Confidence")).toBeInTheDocument();
    expect(screen.getByText("77%"))
      .toBeInTheDocument();
  });

  it("renders empty-state copy when API returns no records", async () => {
    mockRiskResponse([]);

    render(await HomePage({ searchParams: { run_id: "run-empty" } }));

    expect(screen.getByText("No risk forecast data available for this run.")).toBeInTheDocument();
  });
});
