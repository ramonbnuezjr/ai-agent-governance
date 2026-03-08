# Changelog

## [Unreleased]

## v0.2.0 — Governance Harness (Phase 1)
- ATS schema (ATSEvent, Session, Policy, Evaluation, ScenarioPreset) in src/governance/schema.py
- SQLite storage (sessions, ats_events, policies, policy_evaluations) in src/governance/storage.py
- Conformance Engine and three policies: Write Approval Gate, Memory Sanitizer, Objective Alignment (src/governance/policies/, conformance.py)
- ARI scoring (src/governance/ari.py)
- Agent Runner: LLM plan, emit events, write-approval gate (src/governance/agent_runner.py)
- REST API (FastAPI): sessions, run agent, events, evaluations, policies, approve/deny write, presets, stats
- WebSocket: subscribe by session_id, live events and evaluations
- Scenario presets: Compliance Checker, Rogue Agent, Approved Write
- Config: DATABASE_URL, API_HOST, API_PORT
- Tests: governance (ari, schema, policies, storage, conformance), API (presets, sessions, stats)
- Docs: instructions, architecture, PRD, .env.example, README updated

## v0.1.0 — MVP
- Config: `src.config.Settings` via pydantic-settings; `require_anthropic_key()` for fail-fast.
- Anthropic client: `src.clients.anthropic_client.AnthropicClient` with retry and explicit error handling.
- MCP stub: `src.mcp.client.MCPClientStub` and `MCPListToolsResponse` / `MCPToolSchema` (Pydantic).
- GPIO: `src.hardware.gpio.GPIOAdapter`; no-op when `HARDWARE_ENABLED=false`.
- Entrypoint: `python -m src.main` loads config, runs MCP stub and GPIO path, no live API.
- Tests: config, Anthropic client (mocked), MCP stub, GPIO adapter, e2e main.

## v0.0.1 — Bootstrap
- Initialized project scaffold via Cursor Bootstrap v2.0
- Layer 1: Cursor rules (standards, security, workflow, agent)
- Layer 2: pyproject.toml, .pre-commit-config.yaml, .env.example
- Layer 3: instructions.md, architecture.md, roadmap.md, activity_log.md
