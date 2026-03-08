"""Base types for policy evaluation."""

from dataclasses import dataclass
from typing import Any

from src.governance.schema import EvalResult


@dataclass
class PolicyEvalOutput:
    """Result of evaluating one policy on one event."""

    result: EvalResult
    reason: str
    ari_impact: float


# Type for policy config (from PolicyRecord.config)
PolicyConfig = dict[str, Any]
