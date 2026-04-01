import { describe, expect, it, vi } from "vitest";

describe("runtimeEnv", () => {
  it("uses safe defaults when deployment vars are not set", async () => {
    vi.resetModules();
    vi.stubEnv("VITE_RUNTIME_API_URL", "");
    vi.stubEnv("VITE_USE_MOCK", "");
    vi.stubEnv("VITE_RUNTIME_TIMEOUT_MS", "");

    const { runtimeEnv } = await import("../src/config/env");

    expect(runtimeEnv.runtimeApiUrl).toBe("http://localhost:8000");
    expect(runtimeEnv.useMock).toBe(false);
    expect(runtimeEnv.requestTimeoutMs).toBe(10000);
  });

  it("normalizes VITE_RUNTIME_API_URL by trimming and removing trailing slashes", async () => {
    vi.resetModules();
    vi.stubEnv("VITE_RUNTIME_API_URL", "  https://api.example.com///  ");

    const { runtimeEnv } = await import("../src/config/env");

    expect(runtimeEnv.runtimeApiUrl).toBe("https://api.example.com");
  });
});