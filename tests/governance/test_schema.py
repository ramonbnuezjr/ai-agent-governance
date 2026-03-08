"""Tests for ATS schema."""

from datetime import datetime, timezone

import pytest

from src.governance.schema import (
    ATSEvent,
    PolicyEvaluationRecord,
    SessionRecord,
    ToolCallPayload,
)


def test_tool_call_payload_is_write() -> None:
    p = ToolCallPayload(name="report_writer", args={}, is_write=True)
    assert p.is_write is True


def test_atsevent_is_write_operation() -> None:
    ev = ATSEvent(session_id="s1", type="tool_call", payload={"name": "w", "args": {}, "is_write": True})
    assert ev.is_write_operation() is True
    ev2 = ATSEvent(session_id="s1", type="observation", payload={})
    assert ev2.is_write_operation() is False
    ev3 = ATSEvent(session_id="s1", type="memory_write", payload={})
    assert ev3.is_write_operation() is True


def test_atsevent_get_tool_call() -> None:
    ev = ATSEvent(
        session_id="s1",
        type="tool_call",
        payload={"name": "paper_reader", "args": {"q": "x"}, "is_write": False},
    )
    tc = ev.get_tool_call()
    assert tc is not None
    assert tc.name == "paper_reader"
    assert tc.args == {"q": "x"}
    assert tc.is_write is False


def test_session_record_defaults() -> None:
    s = SessionRecord(id="id1", name="n", objective="o")
    assert s.status == "pending"
    assert s.ari_score == 0.0
    assert s.demo is False
