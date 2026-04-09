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
    expect(screen.getByRole("link", { name: "Home" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Runs" })).toHaveAttribute("href", "/runs");
    expect(screen.getByRole("link", { name: "Reports" })).toHaveAttribute("href", "/reports");
  });

  it("renders homepage placeholders", () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response);

    return HomePage({ searchParams: Promise.resolve({ run_id: "run-123" }) }).then((page) => {
      render(page);

      expect(screen.getByRole("heading", { name: "Repository Risk Dashboard" })).toBeInTheDocument();
      expect(screen.getByText("No risk forecast data available for this run.")).toBeInTheDocument();
    });
  });

  it("renders runs page placeholders", () => {
    render(createElement(RunsPage));

    expect(screen.getByRole("heading", { name: "Analysis Runs" })).toBeInTheDocument();
    expect(screen.getByLabelText("run-list-placeholder")).toBeInTheDocument();
  });
});
