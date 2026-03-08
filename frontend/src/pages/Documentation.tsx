import { Link } from "react-router-dom";

export function Documentation() {
  return (
    <>
      <h1 className="page-title">Documentation</h1>
      <div className="card">
        <h2 style={{ fontSize: "1.1rem", margin: "0 0 0.5rem", color: "#e2e4e8" }}>AgentOps Governance Harness</h2>
        <p style={{ color: "#9ca3af", margin: "0 0 1rem" }}>
          This dashboard controls the governance backend: sessions, agent runs, policies, and audit.
        </p>
        <h3 style={{ fontSize: "0.95rem", margin: "0 0 0.25rem", color: "#e2e4e8" }}>Pages</h3>
        <ul style={{ color: "#9ca3af", margin: "0 0 1rem", paddingLeft: "1.25rem" }}>
          <li><Link to="/">Dashboard</Link> — Stats and recent sessions.</li>
          <li><Link to="/agent-runner">Agent Runner</Link> — Create sessions (preset or custom), run the agent, approve/deny writes.</li>
          <li><Link to="/event-stream">Event Stream</Link> — View ATS events for a session (with live WebSocket updates).</li>
          <li><Link to="/policies">Policies</Link> — Enable/disable governance policies (write approval, memory sanitizer, objective alignment).</li>
          <li><Link to="/audit-log">Audit Log</Link> — All policy evaluations (pass/fail/warn) and ARI impact.</li>
        </ul>
        <h3 style={{ fontSize: "0.95rem", margin: "0 0 0.25rem", color: "#e2e4e8" }}>API</h3>
        <p style={{ color: "#9ca3af", margin: 0 }}>
          The backend runs at <code>VITE_API_URL</code> (default <code>http://localhost:8000</code>).
          OpenAPI docs: <a href={`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/docs`} target="_blank" rel="noreferrer">/docs</a>.
        </p>
      </div>
    </>
  );
}
