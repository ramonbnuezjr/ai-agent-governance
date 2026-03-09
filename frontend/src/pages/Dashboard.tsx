import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Stats, Session } from "../types";

export function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [s, list] = await Promise.all([api.getStats(), api.getSessions({ limit: 10 })]);
        if (!cancelled) {
          setStats(s);
          setSessions(list);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (loading) return <p className="loading">Loading dashboard…</p>;
  if (error) return <p className="error-msg">{error}</p>;

  return (
    <>
      <h1 className="page-title">Dashboard</h1>
      {stats && (
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          <div className="card" style={{ minWidth: "180px" }}>
            <div style={{ color: "#8a8f98", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
              Agent Sessions{" "}
              <span
                title="Each session represents one governed agent run with a specific objective. The agent plans, executes tools, and records observations."
              >
                ⓘ
              </span>
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 600 }}>{stats.total_sessions}</div>
          </div>
          <div className="card" style={{ minWidth: "180px" }}>
            <div style={{ color: "#8a8f98", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
              Telemetry Events{" "}
              <span
                title="Total events recorded using the Agentic Telemetry Schema (ATS). Includes Plans, Tool Calls, Observations, and Memory Writes."
              >
                ⓘ
              </span>
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 600 }}>{stats.total_events}</div>
          </div>
          <div className="card" style={{ minWidth: "180px" }}>
            <div style={{ color: "#8a8f98", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
              Policy Violations{" "}
              <span
                title="Actions that failed a governance policy check. Violations increase the ARI score and indicate the agent acted outside allowed bounds."
              >
                ⓘ
              </span>
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 600 }}>{stats.total_violations}</div>
          </div>
          <div className="card" style={{ minWidth: "180px" }}>
            <div style={{ color: "#8a8f98", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
              Avg ARI{" "}
              <span
                title="Average Agency-Risk Index (ARI) across all sessions. Higher values indicate higher governance risk."
              >
                ⓘ
              </span>
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 600 }}>{stats.avg_ari_score}</div>
          </div>
        </div>
      )}
      <div className="card">
        <h2 style={{ fontSize: "1rem", margin: "0 0 0.75rem", color: "#e2e4e8" }}>Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p style={{ color: "#8a8f98", margin: 0 }}>No sessions yet. Start one from Agent Runner.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>ARI</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td><span className={`badge ${s.status}`}>{s.status}</span></td>
                  <td>{s.ari_score.toFixed(1)}</td>
                  <td><Link to={`/event-stream?session=${s.id}`}>View events</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
