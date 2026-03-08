"""Agentic Telemetry Schema (ATS): Pydantic models for events, sessions, policies, evaluations."""

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---- ATS Event types ----

ATSEventType = Literal["plan", "tool_call", "observation", "memory_write"]

EvalResult = Literal["pass", "fail", "warn"]

SessionStatus = Literal["pending", "running", "completed", "failed"]


class ToolCallPayload(BaseModel):
    """Payload for tool_call events: tool name, args, and whether it is a write operation."""

    name: str = Field(..., description="Tool name (e.g. report_writer, paper_reader).")
    args: dict[str, Any] = Field(default_factory=dict, description="Tool arguments.")
    is_write: bool = Field(default=False, description="True if this tool performs a write operation.")


class ATSEvent(BaseModel):
    """
    A single Agentic Telemetry Schema event.
    Emitted by the agent runner for every plan, tool call, observation, memory write.
    """

    session_id: str = Field(..., description="Session this event belongs to.")
    type: ATSEventType = Field(..., description="Event type.")
    payload: dict[str, Any] = Field(default_factory=dict, description="Type-specific payload.")
    sequence: int = Field(default=0, description="Order within session.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional server-assigned id after persist
    id: str | None = Field(default=None, description="Storage id when persisted.")

    def get_tool_call(self) -> ToolCallPayload | None:
        """If type is tool_call, return parsed ToolCallPayload; else None."""
        if self.type != "tool_call":
            return None
        return ToolCallPayload.model_validate(self.payload)

    def is_memory_write(self) -> bool:
        """True if this is a memory_write event."""
        return self.type == "memory_write"

    def is_write_operation(self) -> bool:
        """True if this is a tool_call with is_write=True or a memory_write."""
        if self.type == "memory_write":
            return True
        tc = self.get_tool_call()
        return tc.is_write if tc else False


# ---- Session ----

class SessionRecord(BaseModel):
    """A single agent session: name, objective, status, ARI score."""

    id: str = Field(..., description="Unique session id.")
    name: str = Field(..., description="Human-readable session name.")
    objective: str = Field(..., description="Declared objective for this run.")
    status: SessionStatus = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    ari_score: float = Field(default=0.0, ge=0, le=100, description="Current Agency-Risk Index.")
    demo: bool = Field(default=False, description="If true, ephemeral for public demo.")


# ---- Policy (config) ----

class PolicyRecord(BaseModel):
    """A governance policy: name, enabled, optional config."""

    id: str = Field(..., description="Policy id (e.g. write_approval, memory_sanitizer).")
    name: str = Field(..., description="Human-readable name.")
    enabled: bool = Field(default=True)
    config: dict[str, Any] = Field(default_factory=dict, description="Policy-specific config.")


# ---- Policy evaluation (audit log row) ----

class PolicyEvaluationRecord(BaseModel):
    """One row in the audit log: result of evaluating one policy on one event."""

    id: str | None = Field(default=None, description="Storage id when persisted.")
    session_id: str = Field(...)
    policy_id: str = Field(...)
    result: EvalResult = Field(...)  # pass | fail | warn
    reason: str = Field(default="", description="Human-readable reason.")
    ari_impact: float = Field(default=0.0, description="Delta applied to session ARI.")
    event_sequence: int = Field(default=0, description="ATS event sequence this evaluated.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---- Scenario presets ----

class ScenarioPreset(BaseModel):
    """A predefined scenario for demo: name, objective, optional flags."""

    id: str = Field(..., description="Preset id (e.g. compliance_checker, rogue_agent).")
    name: str = Field(..., description="Display name.")
    objective: str = Field(..., description="Session objective text.")
    description: str = Field(default="", description="Short description for UI.")
