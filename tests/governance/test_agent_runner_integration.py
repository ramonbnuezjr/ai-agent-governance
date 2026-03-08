"""Integration test: run session with write step, no approve -> violation in audit log."""

import tempfile
from pathlib import Path

import pytest

from src.governance.agent_runner import run_session
from src.governance.schema import SessionRecord
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


def test_run_session_write_no_approve_violation(storage: SQLiteStorage) -> None:
    """Run a session that has one write step; do not approve; expect violation in audit log."""
    session = SessionRecord(id="int-1", name="Integration", objective="Write a report")
    storage.create_session(session)

    def mock_llm(prompt: str, system: str | None) -> str:
        if "steps" in prompt.lower() or "objective" in prompt.lower():
            return '[{"tool_name": "report_writer", "is_write": true, "description": "Write report"}]'
        return "Observation: report written."

    run_session(
        storage,
        "int-1",
        mock_llm,
        write_approval_timeout_seconds=0.1,
    )

    evals = storage.list_evaluations(session_id="int-1")
    violations = [e for e in evals if e.result == "fail"]
    assert any(e.policy_id == "write_approval" for e in violations), "Expected write_approval violation"
    session_after = storage.get_session("int-1")
    assert session_after is not None
    assert session_after.ari_score > 0
