# AgentOps Governance Dashboard

Vite + React + TypeScript UI for the AgentOps Governance API.

## Setup

```bash
npm install
cp .env.example .env   # optional: set VITE_API_URL (default http://localhost:8000)
```

## Dev

```bash
npm run dev
```

Open http://localhost:5173. Ensure the backend is running (`python -m src.api` from repo root).

## Build

```bash
npm run build
```

Output in `dist/`. For Vercel, set the project root to `frontend` (or deploy `dist` as a static site).
