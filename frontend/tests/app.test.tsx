import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import App from "../src/App";
import { submitPipeline } from "../src/lib/api";

vi.mock("../src/lib/api", () => {
  return {
    submitPipeline: vi.fn(),
  };
});

const submitPipelineMock = vi.mocked(submitPipeline);

describe("App", () => {
  it("shows validation errors and blocks submission when fields are invalid", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.clear(screen.getByLabelText("Applicant ID"));
    await user.clear(screen.getByLabelText("Document ID"));
    await user.click(screen.getByRole("button", { name: "Run Pipeline" }));

    expect(submitPipelineMock).not.toHaveBeenCalled();
    expect(screen.getByText("Applicant ID is required.")).toBeInTheDocument();
    expect(screen.getByText("Document ID is required.")).toBeInTheDocument();
    expect(screen.getByText(/Fix validation errors before submitting/)).toBeInTheDocument();
    expect(screen.getByText(/Lifecycle: Failure/)).toBeInTheDocument();
  });

  it("runs a valid submit flow and renders success output", async () => {
    submitPipelineMock.mockResolvedValueOnce({
      status: "success",
      decision: "approved",
      mode: "crewai",
      stages: { validation: { status: "ok" } },
      error: null,
    });

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText("Applicant ID"), "app_404");
    await user.type(screen.getByLabelText("Document ID"), "document_valid_444");
    await user.selectOptions(screen.getByLabelText("Execution Mode"), "crewai");
    await user.click(screen.getByRole("button", { name: "Run Pipeline" }));

    await waitFor(() => {
      expect(submitPipelineMock).toHaveBeenCalledWith({
        applicant_id: "app_404",
        document_id: "document_valid_444",
        mode: "crewai",
      });
    });

    const decisionSummaryHeading = await screen.findByRole("heading", {
      name: "Decision Summary",
    });
    expect(decisionSummaryHeading.closest("section")).toHaveTextContent(
      /Decision:\s*approved/
    );
    expect(screen.getByText(/Lifecycle: Success/)).toBeInTheDocument();
  });

  it("renders structured mission-report failure from API response", async () => {
    submitPipelineMock.mockResolvedValueOnce({
      status: "failure",
      decision: "declined",
      mode: "langgraph",
      stages: { risk: { status: "failed" } },
      error: {
        code: "MISSION_REPORT",
        message: "Risk checks failed for submitted document.",
      },
    });

    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText("Applicant ID"), "app_808");
    await user.type(screen.getByLabelText("Document ID"), "document_fail_808");
    await user.selectOptions(screen.getByLabelText("Execution Mode"), "langgraph");
    await user.click(screen.getByRole("button", { name: "Run Pipeline" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /Error Code:\s*MISSION_REPORT/
    );
    expect(screen.getByText(/Lifecycle: Failure/)).toBeInTheDocument();
  });
});
