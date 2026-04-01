import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchHealth, fetchReadiness, submitPipeline } from "../src/lib/api";
import type { PipelineInput } from "../src/lib/types";

const baseInput: PipelineInput = {
  applicant_id: "app_100",
  document_id: "document_valid_123",
  mode: "crewai",
};

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("api integration", () => {
  it("maps successful /run response payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({
          status: "success",
          decision: "approved",
          mode: "crewai",
          stages: { validation: { status: "ok" } },
          error: null,
        }),
      })
    );

    const result = await submitPipeline(baseInput, undefined);

    expect(result.status).toBe("success");
    expect(result.decision).toBe("approved");
    expect(result.error).toBeNull();
  });

  it("maps structured failure from non-2xx payload envelope", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 429,
        json: vi.fn().mockResolvedValue({
          error: {
            code: "RATE_LIMIT",
            message: "rate limit reached",
            failure_category: "rate_limit",
            retry_count: 2,
            stage: "dispatch",
          },
        }),
      })
    );

    const result = await submitPipeline(baseInput, undefined);

    expect(result.status).toBe("failure");
    expect(result.error?.code).toBe("RATE_LIMIT");
    expect(result.error?.failure_category).toBe("rate_limit");
    expect(result.error?.retry_count).toBe(2);
    expect(result.error?.stage).toBe("dispatch");
  });

  it("returns unreachable health/readiness fallbacks when runtime is down", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    await expect(fetchHealth()).resolves.toEqual({ status: "unreachable" });
    await expect(fetchReadiness()).resolves.toEqual({
      status: "not_ready",
      checks: { runtime_api: false },
    });
  });
});
