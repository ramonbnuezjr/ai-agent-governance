"""Memory Sanitizer: scan memory writes for secrets/PII; block or warn on large content."""

import re
from typing import Any

from src.governance.policies.base import PolicyConfig, PolicyEvalOutput
from src.governance.schema import ATSEvent

# Default patterns (lowercase); content is lowercased for match
DEFAULT_PATTERNS = [
    "password",
    "api_key",
    "apikey",
    "secret",
    "ssn",
    "social security",
    "credit_card",
    "credit card",
    "token",
    "bearer ",
    "authorization:",
]

# Simple regex for SSN-like, card-like (not full validation)
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_PATTERN = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")


def _content_from_event(event: ATSEvent) -> str:
    """Extract content string from memory_write or tool_call payload."""
    if event.type == "memory_write":
        return str(event.payload.get("content", ""))
    if event.type == "tool_call":
        args = event.payload.get("args", {})
        return str(args.get("content", args.get("data", "")))
    return ""


def evaluate(session_id: str, event: ATSEvent, config: PolicyConfig) -> PolicyEvalOutput:
    """
    FSM: Idle -> Scanning on memory:write; Scanning -> Clean or Blocked.
    Violation on pattern match; warning on large content.
    """
    if not event.is_memory_write():
        return PolicyEvalOutput(result="pass", reason="Not a memory write.", ari_impact=0.0)

    content = _content_from_event(event)
    if not content:
        return PolicyEvalOutput(result="pass", reason="Empty memory write.", ari_impact=0.0)

    violation_delta = config.get("violationAriDelta", 20)
    max_len = config.get("maxContentLength", 10 * 1024)
    patterns = config.get("patterns", DEFAULT_PATTERNS)

    content_lower = content.lower()
    for p in patterns:
        if p.lower() in content_lower:
            return PolicyEvalOutput(
                result="fail",
                reason=f"Memory write contained sensitive pattern: {p!r}.",
                ari_impact=float(violation_delta),
            )
    if SSN_PATTERN.search(content):
        return PolicyEvalOutput(
            result="fail",
            reason="Memory write contained SSN-like value.",
            ari_impact=float(violation_delta),
        )
    if CARD_PATTERN.search(content):
        return PolicyEvalOutput(
            result="fail",
            reason="Memory write contained card-like value.",
            ari_impact=float(violation_delta),
        )

    if len(content) > max_len:
        return PolicyEvalOutput(
            result="warn",
            reason=f"Memory write exceeded max content length ({max_len} bytes).",
            ari_impact=5.0,
        )

    return PolicyEvalOutput(
        result="pass",
        reason="Memory write passed sanitization checks.",
        ari_impact=-0.5,
    )


memory_sanitizer_policy = {"id": "memory_sanitizer", "evaluate": evaluate}
