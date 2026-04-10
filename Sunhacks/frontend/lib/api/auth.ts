export function buildAuthHeaders(): Record<string, string> {
  const configured = process.env.NEXT_PUBLIC_AUTH_USER_ID;
  if (configured && configured.trim().length > 0) {
    return { "x-user-id": configured.trim() };
  }
  return { "x-user-id": "user-local" };
}
