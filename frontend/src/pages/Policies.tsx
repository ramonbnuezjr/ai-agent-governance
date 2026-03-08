import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Policy } from "../types";

export function Policies() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toggling, setToggling] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    api.getPolicies()
      .then(setPolicies)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const toggle = async (policyId: string, enabled: boolean) => {
    setToggling(policyId);
    setError(null);
    try {
      await api.togglePolicy(policyId, enabled);
      setPolicies((prev) => prev.map((p) => (p.id === policyId ? { ...p, enabled } : p)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setToggling(null);
    }
  };

  if (loading) return <p className="loading">Loading policies…</p>;

  return (
    <>
      <h1 className="page-title">Policies</h1>
      {error && <p className="error-msg">{error}</p>}
      <div className="card">
        <p style={{ color: "#8a8f98", fontSize: "0.85rem", margin: "0 0 0.75rem" }}>
          Governance policies applied during agent runs. Toggle to enable or disable.
        </p>
        <table>
          <thead>
            <tr>
              <th>Policy</th>
              <th>ID</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {policies.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td><code style={{ fontSize: "0.8rem" }}>{p.id}</code></td>
                <td>
                  <span className={`badge ${p.enabled ? "pass" : "pending"}`}>
                    {p.enabled ? "Enabled" : "Disabled"}
                  </span>
                </td>
                <td>
                  <button
                    type="button"
                    disabled={toggling === p.id}
                    onClick={() => toggle(p.id, !p.enabled)}
                  >
                    {toggling === p.id ? "…" : p.enabled ? "Disable" : "Enable"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {policies.length === 0 && (
          <p style={{ color: "#8a8f98", margin: "0.5rem 0 0" }}>No policies in storage.</p>
        )}
      </div>
    </>
  );
}
