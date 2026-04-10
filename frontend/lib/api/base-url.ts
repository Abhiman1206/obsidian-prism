export function resolveApiBaseUrl(): string {
  const configured =
    process.env.API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:10000";

  return configured.replace(/\/$/, "");
}
