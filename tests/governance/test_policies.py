"""Tests for governance policies."""

from datetime import datetime, timezone

import pytest

from src.governance.policies.memory_sanitizer import evaluate as mem_eval
from src.governance.policies.objective_alignment import evaluate as obj_eval
from src.governance.policies.write_approval import (
    evaluate as write_eval,
    is_pending,
    record_approval,
    record_timeout,
)
from src.governance.schema import ATSEvent


def test_write_approval_not_write_pass() -> None:
    ev = ATSEvent(session_id="s1", type="observation", payload={})
    out = write_eval("s1", ev, {})
    assert out.result == "pass"
    assert out.ari_impact == 0.0


def test_write_approval_tool_write_pending() -> None:
    ev = ATSEvent(
        session_id="s1",
        type="tool_call",
        payload={"name": "report_writer", "args": {}, "is_write": True},
    )
    out = write_eval("s1", ev, {"timeoutSeconds": 30})
    assert out.result == "warn"
    assert is_pending("s1") is True


def test_write_approval_approve_then_pass() -> None:
    ev = ATSEvent(
        session_id="s2",
        type="tool_call",
        payload={"name": "w", "args": {}, "is_write": True},
    )
    write_eval("s2", ev, {})
    record_approval("s2")
    ev2 = ATSEvent(session_id="s2", type="observation", payload={})
    out = write_eval("s2", ev2, {})
    assert out.result == "pass"
    assert out.ari_impact == -0.5


def test_write_approval_timeout_violation() -> None:
    ev = ATSEvent(
        session_id="s3",
        type="tool_call",
        payload={"name": "w", "args": {}, "is_write": True},
    )
    write_eval("s3", ev, {"violationAriDelta": 15})
    out = record_timeout("s3", {"violationAriDelta": 15})
    assert out.result == "fail"
    assert out.ari_impact == 15.0


def test_memory_sanitizer_not_memory_pass() -> None:
    ev = ATSEvent(session_id="s1", type="tool_call", payload={})
    out = mem_eval("s1", ev, {})
    assert out.result == "pass"


def test_memory_sanitizer_clean_pass() -> None:
    ev = ATSEvent(
        session_id="s1",
        type="memory_write",
        payload={"content": "Safe summary text"},
    )
    out = mem_eval("s1", ev, {})
    assert out.result == "pass"


def test_memory_sanitizer_sensitive_fail() -> None:
    ev = ATSEvent(
        session_id="s1",
        type="memory_write",
        payload={"content": "The password is secret123"},
    )
    out = mem_eval("s1", ev, {"violationAriDelta": 20})
    assert out.result == "fail"
    assert out.ari_impact == 20.0


def test_objective_alignment_not_tool_call_pass() -> None:
    ev = ATSEvent(session_id="s1", type="plan", payload={})
    out = obj_eval("s1", ev, {}, context={})
    assert out.result == "pass"


def test_objective_alignment_dangerous_fail() -> None:
    ev = ATSEvent(
        session_id="s1",
        type="tool_call",
        payload={"name": "shell", "args": {"cmd": "rm -rf /"}, "is_write": False},
    )
    out = obj_eval("s1", ev, {"dangerousOpsAriDelta": 25}, context={"session_objective": "research"})
    assert out.result == "fail"
    assert out.ari_impact == 25.0
