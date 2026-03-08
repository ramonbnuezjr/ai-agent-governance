"""Conformance Engine: run all enabled policies on each ATS event, persist evaluations, update ARI."""

import logging
from typing import Any, Callable

from src.governance.ari import apply_delta
from src.governance.policies.base import PolicyEvalOutput
from src.governance.policies.memory_sanitizer import memory_sanitizer_policy
from src.governance.policies.objective_alignment import objective_alignment_policy
from src.governance.policies.write_approval import write_approval_policy
from src.governance.schema import ATSEvent, PolicyEvaluationRecord, PolicyRecord
from src.governance.storage import IStorage

logger = logging.getLogger(__name__)

# Policy id -> policy descriptor (evaluate, optional record_approval, record_timeout)
POLICY_REGISTRY: dict[str, dict[str, Any]] = {
    "write_approval": write_approval_policy,
    "memory_sanitizer": memory_sanitizer_policy,
    "objective_alignment": objective_alignment_policy,
}


def _run_policy(
    policy_id: str,
    policy_desc: dict[str, Any],
    session_id: str,
    event: ATSEvent,
    policy_record: PolicyRecord,
    context: dict[str, Any],
) -> PolicyEvalOutput:
    """Run one policy's evaluate(); objective_alignment gets context."""
    evaluate_fn: Callable[..., PolicyEvalOutput] = policy_desc["evaluate"]
    if policy_id == "objective_alignment":
        return evaluate_fn(session_id, event, policy_record.config, context=context)
    return evaluate_fn(session_id, event, policy_record.config)


def evaluate_event(
    storage: IStorage,
    session_id: str,
    event: ATSEvent,
    session_objective: str,
    on_evaluation: Callable[[PolicyEvaluationRecord], None] | None = None,
) -> float:
    """
    Run all enabled policies on the event; persist each evaluation; update and return new ARI.
    Returns the new ARI score for the session after applying all deltas.
    """
    session = storage.get_session(session_id)
    if not session:
        logger.warning("Session %s not found for conformance", session_id)
        return 0.0

    policies = storage.list_policies()
    context = {"session_objective": session_objective}
    total_delta = 0.0
    current_ari = session.ari_score

    for p in policies:
        if not p.enabled:
            continue
        desc = POLICY_REGISTRY.get(p.id)
        if not desc:
            continue
        try:
            out = _run_policy(p.id, desc, session_id, event, p, context)
        except Exception as e:
            logger.exception("Policy %s failed: %s", p.id, e)
            continue
        record = PolicyEvaluationRecord(
            session_id=session_id,
            policy_id=p.id,
            result=out.result,
            reason=out.reason,
            ari_impact=out.ari_impact,
            event_sequence=event.sequence,
        )
        persisted = storage.create_evaluation(record)
        total_delta += out.ari_impact
        if on_evaluation:
            on_evaluation(persisted)
    new_ari = apply_delta(current_ari, total_delta)
    storage.update_session(session_id, ari_score=new_ari)
    return new_ari


def record_write_approval(storage: IStorage, session_id: str) -> None:
    """Call when user approves a pending write. Transitions write_approval FSM to Approved."""
    write_approval_policy["record_approval"](session_id)


def record_write_timeout(
    storage: IStorage,
    session_id: str,
    on_evaluation: Callable[[PolicyEvaluationRecord], None] | None = None,
) -> float:
    """
    Call when write approval times out. Returns new ARI after applying violation.
    Persists the fail evaluation and updates session ARI.
    """
    policy_record = storage.get_policy("write_approval")
    if not policy_record:
        session = storage.get_session(session_id)
        return session.ari_score if session else 0.0
    config = policy_record.config
    out = write_approval_policy["record_timeout"](session_id, config)
    record = PolicyEvaluationRecord(
        session_id=session_id,
        policy_id="write_approval",
        result=out.result,
        reason=out.reason,
        ari_impact=out.ari_impact,
        event_sequence=-1,
    )
    persisted = storage.create_evaluation(record)
    if on_evaluation:
        on_evaluation(persisted)
    session = storage.get_session(session_id)
    current = session.ari_score if session else 0.0
    new_ari = apply_delta(current, out.ari_impact)
    storage.update_session(session_id, ari_score=new_ari)
    return new_ari


def is_write_pending(session_id: str) -> bool:
    """True if write_approval has a pending write for this session."""
    return write_approval_policy["is_pending"](session_id)
