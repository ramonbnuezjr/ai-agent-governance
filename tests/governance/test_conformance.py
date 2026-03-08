"""Tests for conformance engine."""

import tempfile
from pathlib import Path

import pytest

from src.governance.conformance import evaluate_event
from src.governance.schema import ATSEvent, SessionRecord
from src.governance.seed import seed_default_policies
from src.governance.storage import SQLiteStorage


@pytest.fixture
def storage() -> SQLiteStorage:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    st = SQLiteStorage(path)
    st.create_tables()
    seed_default_policies(st)
    yield st
    Path(path).unlink(missing_ok=True)


def test_evaluate_event_updates_ari(storage: SQLiteStorage) -> None:
    storage.create_session(SessionRecord(id="s1", name="n", objective="Research AI safety"))
    ev = ATSEvent(session_id="s1", type="observation", payload={}, sequence=0)
    new_ari = evaluate_event(storage, "s1", ev, "Research AI safety")
    assert new_ari >= 0
    session = storage.get_session("s1")
    assert session is not None
    assert session.ari_score == new_ari


def test_evaluate_event_persists_evaluations(storage: SQLiteStorage) -> None:
    storage.create_session(SessionRecord(id="s1", name="n", objective="Do research"))
    ev = ATSEvent(session_id="s1", type="tool_call", payload={"name": "read", "args": {}, "is_write": False}, sequence=1)
    evaluate_event(storage, "s1", ev, "Do research")
    evals = storage.list_evaluations(session_id="s1")
    assert len(evals) >= 1
