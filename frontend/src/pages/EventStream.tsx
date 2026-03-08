import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { api, wsUrl } from "../api/client";
import type { ATSEventPayload } from "../types";

export function EventStream() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session") ?? "";
  const [events, setEvents] = useState<ATSEventPayload[]>([]);
  const [loading, setLoading] = useState(!!sessionId);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setEvents([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    api.getEvents(sessionId).then((list) => {
      setEvents(list);
      setLoading(false);
    }).catch((e) => {
      setError(e instanceof Error ? e.message : "Failed to load events");
      setLoading(false);
    });
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    const ws = new WebSocket(wsUrl(sessionId));
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data as string);
        if (data.event) setEvents((prev) => [...prev, { ...data.event, timestamp: data.event?.timestamp ?? new Date().toISOString() }]);
        if (data.evaluation) {
          // Optional: append evaluation to a separate list or ignore for event stream
        }
      } catch {
        // ignore
      }
    };
    ws.onerror = () => {};
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId]);

  return (
    <>
      <h1 className="page-title">Event Stream</h1>
      {!sessionId ? (
        <p className="loading">Select a session from the Dashboard or Agent Runner to view events.</p>
      ) : loading ? (
        <p className="loading">Loading events…</p>
      ) : error ? (
        <p className="error-msg">{error}</p>
      ) : (
        <div className="card">
          <p style={{ color: "#8a8f98", fontSize: "0.85rem", margin: "0 0 0.75rem" }}>
            Session: <code>{sessionId}</code> — {events.length} event(s)
          </p>
          <div style={{ maxHeight: "60vh", overflow: "auto" }}>
            {events.length === 0 ? (
              <p style={{ color: "#8a8f98", margin: 0 }}>No events yet. Run the agent to see activity.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Type</th>
                    <th>Time</th>
                    <th>Payload</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((e, i) => (
                    <tr key={i}>
                      <td>{e.sequence}</td>
                      <td><span className="badge pending">{e.type}</span></td>
                      <td style={{ fontSize: "0.8rem", color: "#8a8f98" }}>
                        {e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : "—"}
                      </td>
                      <td style={{ fontSize: "0.85rem", maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis" }}>
                        <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
                          {JSON.stringify(e.payload)}
                        </pre>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </>
  );
}
