"""Write Approval Gate: any tool:write must be preceded by human approval within N seconds."""

import time
from typing import Any

from src.governance.policies.base import PolicyConfig, PolicyEvalOutput
from src.governance.schema import ATSEvent

# In-memory FSM state per session: "idle" | "pending" | "approved" | "violation"
_state: dict[str, dict[str, Any]] = {}


def _get_state(session_id: str) -> dict[str, Any]:
    if session_id not in _state:
        _state[session_id] = {"state": "idle", "pending_since": None, "event_sequence": None}
    return _state[session_id]


def evaluate(session_id: str, event: ATSEvent, config: PolicyConfig) -> PolicyEvalOutput:
    """
    FSM: Idle -> Pending (on tool:write); Pending -> Approved (record_approval) or Violation (record_timeout);
    Approved -> Idle on next event (with pass credit).
    """
    state = _get_state(session_id)
    timeout_sec = config.get("timeoutSeconds", 30)
    violation_delta = config.get("violationAriDelta", 15)
    stale_delta = config.get("staleApprovalAriDelta", 5)
    pass_credit = -0.5

    if state["state"] == "approved":
        # Next event after approval: reset to idle and give pass credit
        state["state"] = "idle"
        state["pending_since"] = None
        return PolicyEvalOutput(
            result="pass",
            reason="Write operation approved by human within time window.",
            ari_impact=pass_credit,
        )

    if state["state"] == "violation":
        # Already violated; subsequent events for this session still get evaluated
        # but we don't double-penalize. Return pass with 0 impact for non-write events.
        if not event.is_write_operation():
            state["state"] = "idle"
        return PolicyEvalOutput(
            result="pass",
            reason="Not a write operation.",
            ari_impact=0.0,
        )

    if not event.is_write_operation():
        return PolicyEvalOutput(result="pass", reason="Not a write operation.", ari_impact=0.0)

    # tool:write or memory_write
    if state["state"] == "idle":
        state["state"] = "pending"
        state["pending_since"] = time.monotonic()
        state["event_sequence"] = event.sequence
        return PolicyEvalOutput(
            result="warn",
            reason="Write operation pending human approval.",
            ari_impact=0.0,
        )

    # state is pending - should not see another write before approve/timeout
    # If we do (e.g. another write), treat as violation
    state["state"] = "violation"
    return PolicyEvalOutput(
        result="fail",
        reason="Write operation timed out waiting for human approval.",
        ari_impact=float(violation_delta),
    )


def record_approval(session_id: str) -> None:
    """Call when user clicks Approve; transitions Pending -> Approved."""
    state = _get_state(session_id)
    if state["state"] == "pending":
        state["state"] = "approved"


def record_timeout(session_id: str, config: PolicyConfig) -> PolicyEvalOutput:
    """Call when approval timeout expires; transitions Pending -> Violation, returns fail evaluation."""
    state = _get_state(session_id)
    violation_delta = config.get("violationAriDelta", 15)
    if state["state"] == "pending":
        state["state"] = "violation"
        return PolicyEvalOutput(
            result="fail",
            reason="Write operation timed out waiting for human approval.",
            ari_impact=float(violation_delta),
        )
    return PolicyEvalOutput(result="pass", reason="No pending write.", ari_impact=0.0)


def is_pending(session_id: str) -> bool:
    """True if session has a write pending approval."""
    return _get_state(session_id)["state"] == "pending"


def get_pending_since(session_id: str) -> float | None:
    """Monotonic time when write went pending; None if not pending."""
    state = _get_state(session_id)
    return state.get("pending_since")


# Policy descriptor for conformance engine
write_approval_policy = {
    "id": "write_approval",
    "evaluate": evaluate,
    "record_approval": record_approval,
    "record_timeout": record_timeout,
    "is_pending": is_pending,
}
