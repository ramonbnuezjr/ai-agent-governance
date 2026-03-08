/** API types aligned with FastAPI responses */

export type SessionStatus = "pending" | "running" | "completed" | "failed";
export type EvalResult = "pass" | "fail" | "warn";

export interface Session {
  id: string;
  name: string;
  objective: string;
  status: SessionStatus;
  ari_score: number;
  demo: boolean;
}

export interface Preset {
  id: string;
  name: string;
  objective: string;
  description: string;
}

export interface Stats {
  total_sessions: number;
  total_events: number;
  total_violations: number;
  avg_ari_score: number;
}

export interface Policy {
  id: string;
  name: string;
  enabled: boolean;
  config: Record<string, unknown>;
}

export interface ATSEventPayload {
  session_id: string;
  type: string;
  payload: Record<string, unknown>;
  sequence: number;
  timestamp: string;
}

export interface EvaluationPayload {
  session_id: string;
  policy_id: string;
  result: EvalResult;
  reason: string;
  ari_impact: number;
  event_sequence: number;
  timestamp: string;
}
