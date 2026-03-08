"""Agent Runner: LLM plan, emit ATS events, run conformance, optional write-approval gate."""

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Callable

from src.governance.conformance import (
    evaluate_event,
    is_write_pending,
    record_write_timeout,
)
from src.governance.schema import ATSEvent, SessionRecord, SessionStatus
from src.governance.storage import IStorage

logger = logging.getLogger(__name__)

# Session id -> Event; API sets event when user approves write
_pending_approval_events: dict[str, threading.Event] = {}
_lock = threading.Lock()


def signal_write_approval(session_id: str) -> None:
    """Call from API when user clicks Approve. Unblocks runner if waiting."""
    with _lock:
        ev = _pending_approval_events.get(session_id)
    if ev:
        ev.set()


def _wait_for_approval_or_timeout(
    session_id: str,
    timeout_seconds: float,
    storage: IStorage,
    on_timeout: Callable[[], None] | None = None,
) -> bool:
    """Returns True if approved, False if timed out. Calls on_timeout if timeout."""
    with _lock:
        ev = _pending_approval_events.setdefault(session_id, threading.Event())
        ev.clear()
    ok = ev.wait(timeout=timeout_seconds)
    if not ok:
        record_write_timeout(storage, session_id, on_evaluation=on_timeout)
        return False
    return True


PLAN_SYSTEM = """You are a planner for an AI agent. Given a user objective, output a JSON array of steps.
Each step is an object with: "tool_name" (string), "is_write" (boolean), "description" (string).
Use tool names like: paper_reader, analysis_engine, report_writer, search, summarize.
Only set is_write true for tools that persist or write data (e.g. report_writer).
Output only valid JSON, no markdown or extra text."""


def _parse_plan(text: str) -> list[dict[str, Any]]:
    """Extract JSON array of steps from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        return []


OBSERVATION_SYSTEM = """You simulate the result of a tool call. Given the tool name and step description, output a short realistic observation (1-3 sentences) as if the tool had run. Output only the observation text, no labels."""


def run_session(
    storage: IStorage,
    session_id: str,
    llm_complete: Callable[[str, str | None], str],
    *,
    on_event: Callable[[ATSEvent], None] | None = None,
    on_evaluation: Callable[[Any], None] | None = None,
    write_approval_timeout_seconds: float = 30.0,
) -> None:
    """
    Run the agent for one session: get plan from LLM, emit events, run conformance.
    Blocks until done. For write steps, waits for approval or timeout.
    """
    session = storage.get_session(session_id)
    if not session:
        logger.error("Session %s not found", session_id)
        return
    storage.update_session(session_id, status="running")
    objective = session.objective
    sequence = 0

    try:
        # 1. Plan
        plan_prompt = f"Objective: {objective}\n\nOutput the JSON array of steps."
        plan_text = llm_complete(plan_prompt, PLAN_SYSTEM)
        steps = _parse_plan(plan_text)
        if not steps:
            steps = [
                {"tool_name": "research", "is_write": False, "description": "Research the topic"},
                {"tool_name": "report_writer", "is_write": True, "description": "Write the report"},
            ]

        plan_event = ATSEvent(
            session_id=session_id,
            type="plan",
            payload={"steps": steps, "objective": objective},
            sequence=sequence,
        )
        sequence += 1
        persisted_plan = storage.create_event(plan_event)
        if on_event:
            on_event(persisted_plan)
        evaluate_event(
            storage,
            session_id,
            persisted_plan,
            objective,
            on_evaluation=on_evaluation,
        )

        # 2. For each step: tool_call -> (wait if write) -> observation -> optional memory_write
        for i, step in enumerate(steps):
            tool_name = step.get("tool_name", "unknown")
            is_write = bool(step.get("is_write", False))
            description = step.get("description", "")

            tool_payload = {
                "name": tool_name,
                "args": {"description": description, "step": i + 1},
                "is_write": is_write,
            }
            tool_event = ATSEvent(
                session_id=session_id,
                type="tool_call",
                payload=tool_payload,
                sequence=sequence,
            )
            sequence += 1
            persisted_tool = storage.create_event(tool_event)
            if on_event:
                on_event(persisted_tool)
            new_ari = evaluate_event(
                storage,
                session_id,
                persisted_tool,
                objective,
                on_evaluation=on_evaluation,
            )
            session = storage.get_session(session_id)
            if session:
                session.ari_score = new_ari

            if is_write and is_write_pending(session_id):
                approved = _wait_for_approval_or_timeout(
                    session_id,
                    write_approval_timeout_seconds,
                    storage,
                    on_timeout=on_evaluation,
                )
                if not approved:
                    logger.info("Write approval timed out for session %s", session_id)

            obs_prompt = f"Tool: {tool_name}. Description: {description}. Output the observation:"
            obs_text = llm_complete(obs_prompt, OBSERVATION_SYSTEM)
            obs_event = ATSEvent(
                session_id=session_id,
                type="observation",
                payload={"content": obs_text, "tool": tool_name},
                sequence=sequence,
            )
            sequence += 1
            persisted_obs = storage.create_event(obs_event)
            if on_event:
                on_event(persisted_obs)
            evaluate_event(
                storage,
                session_id,
                persisted_obs,
                objective,
                on_evaluation=on_evaluation,
            )

            if is_write and (i == len(steps) - 1 or tool_name == "report_writer"):
                mem_event = ATSEvent(
                    session_id=session_id,
                    type="memory_write",
                    payload={"content": obs_text[:500], "summary": f"Step {i+1} result"},
                    sequence=sequence,
                )
                sequence += 1
                persisted_mem = storage.create_event(mem_event)
                if on_event:
                    on_event(persisted_mem)
                evaluate_event(
                    storage,
                    session_id,
                    persisted_mem,
                    objective,
                    on_evaluation=on_evaluation,
                )

        storage.update_session(session_id, status="completed")
    except Exception as e:
        logger.exception("Agent run failed for session %s: %s", session_id, e)
        storage.update_session(session_id, status="failed")
    finally:
        with _lock:
            _pending_approval_events.pop(session_id, None)
