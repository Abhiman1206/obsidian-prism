const DEFAULT_RUNTIME_API_URL = "http://localhost:8000";
const DEFAULT_REQUEST_TIMEOUT_MS = 10000;
const DEFAULT_ALLOWED_ORIGIN = "http://localhost:5173";

function toBool(raw: string | undefined, defaultValue: boolean): boolean {
  if (raw === undefined) {
    return defaultValue;
  }
  const normalized = raw.trim().toLowerCase();
  if (normalized === "true") {
    return true;
  }
  if (normalized === "false") {
    return false;
  }
  return defaultValue;
}

function toPositiveInt(raw: string | undefined, defaultValue: number): number {
  if (raw === undefined || !raw.trim()) {
    return defaultValue;
  }
  const parsed = Number.parseInt(raw, 10);
  if (Number.isNaN(parsed) || parsed <= 0) {
    return defaultValue;
  }
  return parsed;
}

function normalizeUrl(raw: string | undefined): string {
  if (!raw || !raw.trim()) {
    return DEFAULT_RUNTIME_API_URL;
  }

  const normalized = raw.trim().replace(/\/+$/, "");
  return normalized || DEFAULT_RUNTIME_API_URL;
}

export const runtimeEnv = {
  runtimeApiUrl: normalizeUrl(import.meta.env.VITE_RUNTIME_API_URL),
  useMock: toBool(import.meta.env.VITE_USE_MOCK, false),
  requestTimeoutMs: toPositiveInt(
    import.meta.env.VITE_RUNTIME_TIMEOUT_MS,
    DEFAULT_REQUEST_TIMEOUT_MS
  ),
  defaultFrontendOrigin: import.meta.env.VITE_FRONTEND_ORIGIN ?? DEFAULT_ALLOWED_ORIGIN,
} as const;
