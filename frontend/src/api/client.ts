const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(Array.isArray(err.detail) ? err.detail[0]?.msg ?? res.statusText : err.detail ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getStats: () => request<import("../types").Stats>("/api/stats"),
  getPresets: () => request<import("../types").Preset[]>("/api/presets"),
  getSessions: (params?: { demo_only?: boolean; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.demo_only != null) q.set("demo_only", String(params.demo_only));
    if (params?.limit != null) q.set("limit", String(params.limit));
    return request<import("../types").Session[]>(`/api/sessions?${q}`);
  },
  getSession: (id: string) => request<import("../types").Session>(`/api/sessions/${id}`),
  createSession: (body: { name: string; objective: string; demo?: boolean }) =>
    request<import("../types").Session>("/api/sessions", { method: "POST", body: JSON.stringify(body) }),
  createSessionFromPreset: (presetId: string) =>
    request<import("../types").Session>(`/api/sessions/from-preset/${presetId}`, { method: "POST" }),
  runSession: (sessionId: string) =>
    request<{ status: string; session_id: string }>(`/api/sessions/${sessionId}/run`, { method: "POST" }),
  getPendingWrite: (sessionId: string) =>
    request<{ pending: boolean }>(`/api/sessions/${sessionId}/pending-write`),
  approveWrite: (sessionId: string) =>
    request<{ status: string }>(`/api/sessions/${sessionId}/approve-write`, { method: "POST" }),
  denyWrite: (sessionId: string) =>
    request<{ status: string }>(`/api/sessions/${sessionId}/deny-write`, { method: "POST" }),
  getEvents: (sessionId: string, limit = 200) =>
    request<import("../types").ATSEventPayload[]>(`/api/sessions/${sessionId}/events?limit=${limit}`),
  getEvaluations: (sessionId: string, limit = 500) =>
    request<import("../types").EvaluationPayload[]>(`/api/sessions/${sessionId}/evaluations?limit=${limit}`),
  getEvaluationsGlobal: (limit = 500) =>
    request<import("../types").EvaluationPayload[]>(`/api/evaluations?limit=${limit}`),
  getPolicies: () => request<import("../types").Policy[]>("/api/policies"),
  togglePolicy: (policyId: string, enabled: boolean) =>
    request<{ status: string }>(`/api/policies/${policyId}`, {
      method: "PATCH",
      body: JSON.stringify({ enabled }),
    }),
};

/** WebSocket URL for live events/evaluations for a session */
export function wsUrl(sessionId: string): string {
  const u = new URL(base);
  u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
  u.pathname = `/ws/${sessionId}`;
  return u.toString();
}
