"""Tests for storage."""

import tempfile
from pathlib import Path

import pytest

from src.governance.schema import ATSEvent, PolicyRecord, SessionRecord
from src.governance.storage import SQLiteStorage


@pytest.fixture
def storage() -> SQLiteStorage:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    st = SQLiteStorage(path)
    st.create_tables()
    yield st
    Path(path).unlink(missing_ok=True)


def test_create_and_get_session(storage: SQLiteStorage) -> None:
    session = SessionRecord(id="s1", name="Test", objective="Do something")
    storage.create_session(session)
    loaded = storage.get_session("s1")
    assert loaded is not None
    assert loaded.name == "Test"
    assert loaded.ari_score == 0.0


def test_create_event(storage: SQLiteStorage) -> None:
    storage.create_session(SessionRecord(id="s1", name="n", objective="o"))
    ev = ATSEvent(session_id="s1", type="plan", payload={"steps": []}, sequence=0)
    out = storage.create_event(ev)
    assert out.id is not None
    events = storage.list_events("s1")
    assert len(events) == 1
    assert events[0].type == "plan"


def test_list_evaluations(storage: SQLiteStorage) -> None:
    from src.governance.schema import PolicyEvaluationRecord
    storage.create_session(SessionRecord(id="s1", name="n", objective="o"))
    rec = PolicyEvaluationRecord(session_id="s1", policy_id="write_approval", result="pass", reason="ok")
    storage.create_evaluation(rec)
    evals = storage.list_evaluations(session_id="s1")
    assert len(evals) == 1
    assert evals[0].policy_id == "write_approval"
