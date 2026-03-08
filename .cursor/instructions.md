# Project Instructions

## Project Overview
agent_ops is an AI Governance tooling project that includes the **AgentOps Governance Harness (MI9-in-a-Box)**: runtime observability and policy enforcement for AI agents. It emits Agentic Telemetry Schema (ATS) events, runs a Conformance Engine with FSM-based policies (Write Approval Gate, Memory Sanitizer, Objective Alignment), computes an Agency-Risk Index (ARI), and exposes a REST + WebSocket API for dashboards and live intervention. It also provides config-driven settings, Anthropic/OpenAI clients, and optional MCP/GPIO. Cloud target is not yet defined; MCP server type is TBD.

## Project Mode
**Current Mode: PRODUCTION**
> To switch modes, update this line and add a note in activity_log.md.

## Supported Features
- **Governance Harness:** ATS events (plan, tool_call, observation, memory_write), Conformance Engine, ARI scoring, Agent Runner (LLM plan + simulated tool execution), REST API (FastAPI), WebSocket for live events/evaluations, Scenario Presets, approve/deny write (Live Intervention)
- Environment config via pydantic-settings
- Anthropic/OpenAI client wrappers with error handling
- MCP client stub with Pydantic-validated responses (server type TBD)
- Hardware-conditional GPIO layer for edge use (optional)
- Governed Python toolchain (Black, Ruff, mypy strict, Bandit, pytest-cov)

## Non-Goals
- Not a general-purpose chatbot or chat UI
- Not a model training or fine-tuning platform
- No cloud deployment until a target is chosen
- No MCP server implementation (client only; server type TBD)

## Key Dependencies
- Python 3.11+
- Anthropic SDK / OpenAI SDK
- MCP (Model Context Protocol)
- Pydantic v2 for all data validation
- Raspberry Pi GPIO (conditionally enabled via HARDWARE_ENABLED env var)

## How Cursor Should Behave
- Read this file, architecture.md, and roadmap.md before any structural change.
- Reference all rules/*.mdc files on every generation.
- Flag ambiguity before acting, not after.
- Never generate incomplete placeholder code in src/.
- Tests live in tests/ mirroring src/ structure exactly.
- All secrets via environment variables. See .env.example.
