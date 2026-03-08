"""Seed default policies and optional demo data."""

from src.governance.schema import PolicyRecord
from src.governance.storage import IStorage

DEFAULT_POLICIES: list[PolicyRecord] = [
    PolicyRecord(
        id="write_approval",
        name="Write Approval Gate",
        enabled=True,
        config={
            "timeoutSeconds": 30,
            "requireExplicitApproval": True,
            "violationAriDelta": 15,
            "staleApprovalAriDelta": 5,
        },
    ),
    PolicyRecord(
        id="memory_sanitizer",
        name="Memory Sanitizer",
        enabled=True,
        config={
            "maxContentLength": 10 * 1024,
            "violationAriDelta": 20,
            "patterns": ["password", "api_key", "secret", "ssn", "credit_card", "token"],
        },
    ),
    PolicyRecord(
        id="objective_alignment",
        name="Objective Alignment Monitor",
        enabled=True,
        config={
            "minAlignmentPercent": 50,
            "dangerousOpsAriDelta": 25,
            "lowAlignmentAriDelta": 5,
            "dangerousKeywords": ["delete", "drop", "truncate", "rm -rf", "rm -r", "format"],
        },
    ),
]


def seed_default_policies(storage: IStorage) -> None:
    """Insert default policies if they do not already exist."""
    for policy in DEFAULT_POLICIES:
        if storage.get_policy(policy.id) is None:
            storage.create_policy(policy)
