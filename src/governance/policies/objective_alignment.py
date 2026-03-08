"""Objective Alignment Monitor: tool calls must align with session objective; flag dangerous ops."""

from src.governance.policies.base import PolicyConfig, PolicyEvalOutput
from src.governance.schema import ATSEvent


def _alignment_percent(objective: str, tool_name: str, args: dict) -> float:
    """Crude keyword overlap: words in objective vs tool name + args string. Returns 0-100."""
    obj_words = set(objective.lower().split())
    tool_str = f"{tool_name} {' '.join(str(v) for v in args.values())}".lower()
    tool_words = set(tool_str.split())
    if not obj_words:
        return 100.0
    overlap = len(obj_words & tool_words) / len(obj_words)
    return min(100.0, overlap * 100.0)


def evaluate(
    session_id: str,
    event: ATSEvent,
    config: PolicyConfig,
    *,
    context: dict | None = None,
) -> PolicyEvalOutput:
    """
    Only evaluates tool_call events. Dangerous ops get fail +25; low alignment get warn +5.
    """
    if event.type != "tool_call":
        return PolicyEvalOutput(result="pass", reason="Not a tool call.", ari_impact=0.0)

    tool = event.get_tool_call()
    if not tool:
        return PolicyEvalOutput(result="pass", reason="Tool call missing payload.", ari_impact=0.0)

    dangerous_delta = config.get("dangerousOpsAriDelta", 25)
    low_align_delta = config.get("lowAlignmentAriDelta", 5)
    min_align = config.get("minAlignmentPercent", 50)
    dangerous_kw = config.get("dangerousKeywords", ["delete", "drop", "truncate", "rm -rf", "rm -r", "format"])

    tool_str = f"{tool.name} {' '.join(str(v) for v in tool.args.values())}".lower()
    for kw in dangerous_kw:
        if kw.lower() in tool_str:
            return PolicyEvalOutput(
                result="fail",
                reason=f"Dangerous operation detected: {kw!r}.",
                ari_impact=float(dangerous_delta),
            )

    session_objective = (context or {}).get("session_objective", "")
    if not session_objective:
        return PolicyEvalOutput(result="pass", reason="No objective to align to.", ari_impact=0.0)

    pct = _alignment_percent(session_objective, tool.name, tool.args)
    if pct < min_align:
        return PolicyEvalOutput(
            result="warn",
            reason=f"Tool call alignment with objective low ({pct:.0f}%).",
            ari_impact=float(low_align_delta),
        )
    return PolicyEvalOutput(
        result="pass",
        reason=f"Tool call aligned with objective ({pct:.0f}%).",
        ari_impact=-0.5,
    )


objective_alignment_policy = {
    "id": "objective_alignment",
    "evaluate": evaluate,
}
