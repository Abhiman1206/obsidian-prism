import { describe, expect, it } from "vitest";
import { validatePipelineInput } from "../src/lib/validation";

describe("validatePipelineInput", () => {
  it("accepts a valid payload", () => {
    const result = validatePipelineInput({
      applicant_id: " app_100 ",
      document_id: " document_valid_123 ",
      mode: "crewai",
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      throw new Error("Expected valid result.");
    }

    expect(result.data).toEqual({
      applicant_id: "app_100",
      document_id: "document_valid_123",
      mode: "crewai",
    });
  });

  it("rejects missing required fields", () => {
    const result = validatePipelineInput({
      applicant_id: " ",
      document_id: "",
      mode: "",
    });

    expect(result.ok).toBe(false);
    if (result.ok) {
      throw new Error("Expected invalid result.");
    }

    expect(result.errors.applicant_id).toContain("required");
    expect(result.errors.document_id).toContain("required");
    expect(result.errors.mode).toContain("required");
  });

  it("rejects unsupported modes", () => {
    const result = validatePipelineInput({
      applicant_id: "app_101",
      document_id: "document_valid_555",
      mode: "manual",
    });

    expect(result.ok).toBe(false);
    if (result.ok) {
      throw new Error("Expected invalid result.");
    }

    expect(result.errors.mode).toContain("crewai");
  });
});
