# Product Requirements Document

## Problem Statement
Teams adopting AI/LLM workflows need governance: consistent configuration, auditability, and controlled use of models and tools. agent_ops solves this for operators and engineers who run or automate AI workloads. It provides a governed, config-driven layer over Anthropic/OpenAI and MCP so policies and secrets are centralized and behavior is repeatable.

## Core User Flow
1. Operator configures environment (e.g. `.env`) and optional governance policies.
2. Operator runs the application (CLI or programmatic entrypoint).
3. Application loads settings via pydantic-settings and validates required secrets.
4. Application uses AI clients and/or MCP (when configured) to perform governed workflows.
5. Logging and structure support audit and debugging without exposing secrets.

## Non-Goals
- Building a chat UI or conversational product
- Model training, fine-tuning, or hosting
- Implementing an MCP server (client only; server type TBD)
- Cloud deployment until a target is chosen
- Replacing existing IDEs or editors

## Success Criteria
- [x] Settings load from environment and fail fast when required secrets are missing
- [x] At least one AI provider (Anthropic) is usable with retry and error handling
- [x] MCP client stub accepts configuration and validates responses with Pydantic
- [x] Toolchain (tests, lint, type-check, security) runs and is enforced via pre-commit
- [x] Governance Harness: ATS events, Conformance Engine (Write Approval, Memory Sanitizer, Objective Alignment), ARI, Agent Runner, REST API, WebSocket, Scenario Presets, approve/deny write (Live Intervention)

---
*Engineering rules live in .cursor/rules/. This document is scope-only.*
