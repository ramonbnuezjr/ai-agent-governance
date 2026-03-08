# agent_ops

## Prerequisites
- Python 3.11+
- Node.js 20+ (for the dashboard frontend)

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

## Frontend (Dashboard)

The UI lives in `frontend/` (Vite + React + TypeScript).

```bash
cd frontend
cp .env.example .env   # optional: set VITE_API_URL if API is not on http://localhost:8000
npm install
npm run dev            # http://localhost:5173
```

For production build: `npm run build`; output is in `frontend/dist/` (e.g. deploy to Vercel with root `frontend`).

## Deploy backend on Render

1. **New Web Service** — Connect GitHub repo `ramonbnuezjr/ai-agent-governance`. Do **not** set Root Directory (use repo root so Render sees `pyproject.toml` and `src/`).

2. **Build & start**
   - **Build Command:** `pip install .`
   - **Start Command:** `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`

3. **Environment variables** (Settings → Environment):

   | Key | Value | Required |
   |-----|--------|----------|
   | `GEMINI_API_KEY` | Your Gemini API key | Yes (or use Anthropic below) |
   | `ANTHROPIC_API_KEY` | Your Anthropic key | Yes if not using Gemini |
   | `CORS_ORIGINS` | Your Vercel frontend URL | Yes for Vercel UI (e.g. `https://ai-agent-governance.vercel.app`) |
   | `DATABASE_URL` | `sqlite:///agent_ops.db` | No (default); data is ephemeral unless you add a Render Disk |
   | `HARDWARE_ENABLED` | `false` | No |

   Add other vars from `.env.example` if you use them (e.g. `GEMINI_MODEL`, `LOG_LEVEL`).

4. **Database:** The default SQLite file is lost on each deploy/restart. For persistent data, add a [Render Disk](https://render.com/docs/disks) and set `DATABASE_URL=sqlite:////data/agent_ops.db` (mount the disk at `/data`).

5. After deploy, copy the service URL (e.g. `https://your-service.onrender.com`) and set **Vercel** env var `VITE_API_URL` to that URL, then redeploy the frontend.

## Environment Variables

See `.env.example` for all required and optional variables with descriptions. For the Governance Harness, set `ANTHROPIC_API_KEY` to run the agent; `DATABASE_URL` defaults to SQLite.

## Hardware Notes (Raspberry Pi)

Set `HARDWARE_ENABLED=false` in `.env` for non-Pi environments.
GPIO functionality degrades gracefully when disabled.
