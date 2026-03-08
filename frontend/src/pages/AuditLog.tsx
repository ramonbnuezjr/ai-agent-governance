import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { EvaluationPayload } from "../types";

export function AuditLog() {
  const [searchParams] = useSearchParams();
  const sessionFilter = searchParams.get("session") ?? "";
  const [evaluations, setEvaluations] = useState<EvaluationPayload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    const fn = sessionFilter
      ? api.getEvaluations(sessionFilter, 500)
      : api.getEvaluationsGlobal(500);
    fn
      .then(setEvaluations)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [sessionFilter]);

  if (loading) return <p className="loading">Loading audit log…</p>;
  if (error) return <p className="error-msg">{error}</p>;

  return (
    <>
      <h1 className="page-title">Audit Log</h1>
      <div className="card">
        <p style={{ color: "#8a8f98", fontSize: "0.85rem", margin: "0 0 0.75rem" }}>
          Policy evaluations across all sessions{sessionFilter ? ` (session: ${sessionFilter})` : ""}.
        </p>
        <div style={{ maxHeight: "65vh", overflow: "auto" }}>
          {evaluations.length === 0 ? (
            <p style={{ color: "#8a8f98", margin: 0 }}>No evaluations yet. Run an agent to generate audit entries.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Session</th>
                  <th>Policy</th>
                  <th>Result</th>
                  <th>ARI impact</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {evaluations.map((e, i) => (
                  <tr key={i}>
                    <td style={{ fontSize: "0.8rem", color: "#8a8f98" }}>
                      {e.timestamp ? new Date(e.timestamp).toLocaleString() : "—"}
                    </td>
                    <td style={{ fontSize: "0.8rem" }}>{e.session_id.slice(0, 8)}…</td>
                    <td><code style={{ fontSize: "0.8rem" }}>{e.policy_id}</code></td>
                    <td><span className={`badge ${e.result}`}>{e.result}</span></td>
                    <td>{e.ari_impact}</td>
                    <td style={{ maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis" }}>{e.reason || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
