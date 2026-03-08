# agent_ops

## Prerequisites
- Python 3.11+
- [Node.js if applicable]

## Setup

```bash
# Clone and enter project
git clone <repo-url> && cd <project-dir>

# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env — fill in required values
```

## Running Tests

```bash
pytest                          # Run all tests with coverage
pytest tests/unit/              # Unit tests only
pytest --no-cov                 # Skip coverage (faster iteration)
```

## Running the Application

```bash
# CLI entrypoint (config load, MCP stub, GPIO no-op)
python -m src.main

# Governance API (REST + WebSocket) — for dashboard/frontend
python -m src.api
# Serves on http://0.0.0.0:8000 by default. Set API_HOST/API_PORT in .env.
# Endpoints: GET/POST /api/sessions, POST /api/sessions/{id}/run, GET /api/events, GET /api/evaluations, POST /api/sessions/{id}/approve-write, GET /api/presets, WebSocket /ws/{session_id}
```

## Environment Variables

See `.env.example` for all required and optional variables with descriptions. For the Governance Harness, set `ANTHROPIC_API_KEY` to run the agent; `DATABASE_URL` defaults to SQLite.

## Hardware Notes (Raspberry Pi)

Set `HARDWARE_ENABLED=false` in `.env` for non-Pi environments.
GPIO functionality degrades gracefully when disabled.
