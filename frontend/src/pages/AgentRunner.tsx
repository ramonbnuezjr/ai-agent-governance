import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { Preset, Session } from "../types";

export function AgentRunner() {
  const navigate = useNavigate();
  const [presets, setPresets] = useState<Preset[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [pendingWrite, setPendingWrite] = useState(false);
  const [customName, setCustomName] = useState("");
  const [customObjective, setCustomObjective] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const [p, s] = await Promise.all([api.getPresets(), api.getSessions({ limit: 20 })]);
      setPresets(p);
      setSessions(s);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (!selectedSession?.id) {
      setPendingWrite(false);
      return;
    }
    let cancelled = false;
    api.getPendingWrite(selectedSession.id).then((r) => {
      if (!cancelled) setPendingWrite(r.pending);
    }).catch(() => { if (!cancelled) setPendingWrite(false); });
    const t = setInterval(() => {
      api.getPendingWrite(selectedSession.id).then((r) => {
        if (!cancelled) setPendingWrite(r.pending);
      }).catch(() => {});
    }, 2000);
    return () => { cancelled = true; clearInterval(t); };
  }, [selectedSession?.id]);

  const createFromPreset = async (presetId: string) => {
    setBusy(true);
    setError(null);
    try {
      const session = await api.createSessionFromPreset(presetId);
      setSessions((prev) => [session, ...prev]);
      setSelectedSession(session);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create session");
    } finally {
      setBusy(false);
    }
  };

  const createCustom = async () => {
    if (!customName.trim() || !customObjective.trim()) {
      setError("Name and objective are required");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const session = await api.createSession({ name: customName.trim(), objective: customObjective.trim() });
      setSessions((prev) => [session, ...prev]);
      setSelectedSession(session);
      setCustomName("");
      setCustomObjective("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create session");
    } finally {
      setBusy(false);
    }
  };

  const run = async () => {
    if (!selectedSession) return;
    setBusy(true);
    setError(null);
    try {
      await api.runSession(selectedSession.id);
      await load();
      const updated = await api.getSession(selectedSession.id);
      setSelectedSession(updated);
      navigate(`/event-stream?session=${selectedSession.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start run");
    } finally {
      setBusy(false);
    }
  };

  const approveWrite = async () => {
    if (!selectedSession) return;
    setBusy(true);
    setError(null);
    try {
      await api.approveWrite(selectedSession.id);
      setPendingWrite(false);
      await load();
      setSelectedSession(await api.getSession(selectedSession.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to approve");
    } finally {
      setBusy(false);
    }
  };

  const denyWrite = async () => {
    if (!selectedSession) return;
    setBusy(true);
    setError(null);
    try {
      await api.denyWrite(selectedSession.id);
      setPendingWrite(false);
      await load();
      setSelectedSession(await api.getSession(selectedSession.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to deny");
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <p className="loading">Loading…</p>;

  return (
    <>
      <h1 className="page-title">Agent Runner</h1>
      {error && <p className="error-msg">{error}</p>}

      <div className="card">
        <h2 style={{ fontSize: "1rem", margin: "0 0 0.75rem", color: "#e2e4e8" }}>Start from preset</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {presets.map((p) => (
            <button
              key={p.id}
              type="button"
              className="primary"
              disabled={busy}
              onClick={() => createFromPreset(p.id)}
            >
              {p.name}
            </button>
          ))}
        </div>
        <p style={{ color: "#8a8f98", fontSize: "0.85rem", margin: "0.5rem 0 0" }}>
          Creates a new session with the preset objective.
        </p>
      </div>

      <div className="card">
        <h2 style={{ fontSize: "1rem", margin: "0 0 0.75rem", color: "#e2e4e8" }}>Custom session</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxWidth: "400px" }}>
          <input
            placeholder="Session name"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
          />
          <textarea
            placeholder="Objective"
            value={customObjective}
            onChange={(e) => setCustomObjective(e.target.value)}
            rows={3}
          />
          <button type="button" className="primary" disabled={busy} onClick={createCustom}>
            Create session
          </button>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: "1rem", margin: "0 0 0.75rem", color: "#e2e4e8" }}>Current session</h2>
        <select
          value={selectedSession?.id ?? ""}
          onChange={(e) => {
            const s = sessions.find((x) => x.id === e.target.value);
            setSelectedSession(s ?? null);
          }}
          style={{ minWidth: "280px", marginBottom: "0.75rem" }}
        >
          <option value="">Select a session…</option>
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>{s.name} ({s.status})</option>
          ))}
        </select>
        {selectedSession && (
          <div style={{ marginTop: "0.5rem" }}>
            <p style={{ margin: "0 0 0.5rem", color: "#8a8f98", fontSize: "0.9rem" }}>
              Status: <span className={`badge ${selectedSession.status}`}>{selectedSession.status}</span>
              {" "}ARI: {selectedSession.ari_score.toFixed(1)}
            </p>
            {selectedSession.status !== "running" && (
              <button type="button" className="primary" disabled={busy} onClick={run}>
                Run agent
              </button>
            )}
            {pendingWrite && (
              <div style={{ marginTop: "1rem", padding: "0.75rem", background: "rgba(201, 162, 39, 0.15)", borderRadius: 6 }}>
                <p style={{ margin: "0 0 0.5rem" }}>Write pending approval</p>
                <button type="button" className="primary" disabled={busy} onClick={approveWrite}>Approve</button>
                {" "}
                <button type="button" className="danger" disabled={busy} onClick={denyWrite}>Deny</button>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
