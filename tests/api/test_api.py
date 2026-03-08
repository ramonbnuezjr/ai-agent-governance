"""Tests for FastAPI endpoints."""

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    with TestClient(app) as c:
        yield c
    Path(db_path).unlink(missing_ok=True)


def test_list_presets(client: TestClient) -> None:
    r = client.get("/api/presets")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    ids = [p["id"] for p in data]
    assert "compliance_checker" in ids
    assert "rogue_agent" in ids


def test_create_session(client: TestClient) -> None:
    r = client.post("/api/sessions", json={"name": "Test", "objective": "Do it"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test"
    assert data["objective"] == "Do it"
    assert data["status"] == "pending"
    assert "id" in data


def test_get_sessions(client: TestClient) -> None:
    client.post("/api/sessions", json={"name": "S1", "objective": "O1"})
    r = client.get("/api/sessions")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_stats(client: TestClient) -> None:
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_sessions" in data
    assert "total_events" in data
    assert "total_violations" in data
    assert "avg_ari_score" in data


def test_root_returns_links(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "AgentOps Governance API"
    assert data["docs"] == "/docs"
    assert "presets" in data["api"]


def test_get_session_success(client: TestClient) -> None:
    create = client.post("/api/sessions", json={"name": "S1", "objective": "O1"})
    sid = create.json()["id"]
    r = client.get(f"/api/sessions/{sid}")
    assert r.status_code == 200
    assert r.json()["name"] == "S1"


def test_get_session_404(client: TestClient) -> None:
    r = client.get("/api/sessions/nonexistent-id")
    assert r.status_code == 404


def test_create_session_from_preset(client: TestClient) -> None:
    r = client.post("/api/sessions/from-preset/compliance_checker")
    assert r.status_code == 200
    assert r.json()["name"] == "Compliance Checker"


def test_list_events(client: TestClient) -> None:
    create = client.post("/api/sessions", json={"name": "E1", "objective": "O1"})
    sid = create.json()["id"]
    r = client.get(f"/api/sessions/{sid}/events")
    assert r.status_code == 200
    assert r.json() == []


def test_list_policies(client: TestClient) -> None:
    r = client.get("/api/policies")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 3
    ids = [p["id"] for p in data]
    assert "write_approval" in ids


def test_pending_write(client: TestClient) -> None:
    create = client.post("/api/sessions", json={"name": "P1", "objective": "O1"})
    sid = create.json()["id"]
    r = client.get(f"/api/sessions/{sid}/pending-write")
    assert r.status_code == 200
    assert "pending" in r.json()


def test_approve_write(client: TestClient) -> None:
    create = client.post("/api/sessions", json={"name": "A1", "objective": "O1"})
    sid = create.json()["id"]
    r = client.post(f"/api/sessions/{sid}/approve-write")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"


def test_deny_write(client: TestClient) -> None:
    create = client.post("/api/sessions", json={"name": "D1", "objective": "O1"})
    sid = create.json()["id"]
    r = client.post(f"/api/sessions/{sid}/deny-write")
    assert r.status_code == 200
    assert r.json()["status"] == "denied"


def test_list_evaluations_for_session(client: TestClient) -> None:
    create = client.post("/api/sessions", json={"name": "Ev1", "objective": "O1"})
    sid = create.json()["id"]
    r = client.get(f"/api/sessions/{sid}/evaluations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_evaluations_global(client: TestClient) -> None:
    r = client.get("/api/evaluations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_toggle_policy(client: TestClient) -> None:
    r = client.patch("/api/policies/write_approval", json={"enabled": False})
    assert r.status_code == 200
    r2 = client.patch("/api/policies/write_approval", json={"enabled": True})
    assert r2.status_code == 200


def test_run_agent_returns_409_if_already_running(client: TestClient) -> None:
    """Run agent returns 409 when session is already running."""
    create = client.post("/api/sessions", json={"name": "Run1", "objective": "O1"})
    sid = create.json()["id"]
    from src.api.app import get_storage
    storage = get_storage()
    storage.update_session(sid, status="running")
    r = client.post(f"/api/sessions/{sid}/run")
    assert r.status_code == 409
