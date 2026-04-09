import { render, screen } from "@testing-library/react";
import { createElement } from "react";

import AppShell from "../components/layout/app-shell";
import HomePage from "../app/page";
import RunsPage from "../app/runs/page";

describe("app shell", () => {
  it("renders shared shell container and navigation links", () => {
    render(createElement(AppShell, null, createElement("div", null, "child")));

    expect(screen.getByTestId("app-shell")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Home" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Runs" })).toHaveAttribute("href", "/runs");
  });

  it("renders homepage placeholders", () => {
    render(createElement(HomePage));

    expect(screen.getByRole("heading", { name: "Repository Risk Dashboard" })).toBeInTheDocument();
    expect(screen.getByLabelText("kpi-summary-placeholder")).toBeInTheDocument();
  });

  it("renders runs page placeholders", () => {
    render(createElement(RunsPage));

    expect(screen.getByRole("heading", { name: "Analysis Runs" })).toBeInTheDocument();
    expect(screen.getByLabelText("run-list-placeholder")).toBeInTheDocument();
  });
});
