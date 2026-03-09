# Deployment (Vercel + Render)

This project uses a split deployment:

- **Vercel** — Frontend (React/Vite in `frontend/`). Serves the UI; users load the site from your Vercel URL.
- **Render** — Backend (FastAPI in `src/`). Runs the API and agent logic; the UI calls it from the browser.

When a user visits your site, their browser loads the UI from Vercel, then the app sends API requests to Render. Because those are different origins, the backend must allow the frontend origin via **CORS**.

---

## Backend (Render)

1. **Web Service** — Repo `ramonbnuezjr/ai-agent-governance`, **Root Directory** empty (repo root).
2. **Build:** `pip install .`
3. **Start:** `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
4. **Environment variables:**
   - `GEMINI_API_KEY` or `ANTHROPIC_API_KEY` — required for agent runs (set at least one).
   - `CORS_ORIGINS` — comma-separated list of allowed frontend origins, e.g.  
     `https://ai-agent-governance.vercel.app,https://ai-agent-governance-xxxx.vercel.app`  
     Include both your production URL and any Vercel preview URLs you use.
   - `HARDWARE_ENABLED` = `false`
   - Optional: `DATABASE_URL`, `LOG_LEVEL`, etc. (see `.env.example`).

After deploy, note the service URL (e.g. `https://ai-agent-governance.onrender.com`).

---

## Frontend (Vercel)

1. **Project** — Same repo; set **Root Directory** to `frontend`.
2. Vercel will detect Vite and build automatically.
3. **Environment variable:** `VITE_API_URL` = your Render backend URL (e.g. `https://ai-agent-governance.onrender.com`).
4. Redeploy after changing env vars so the build picks up `VITE_API_URL`.

Your live app will be at the Vercel URL (e.g. `https://ai-agent-governance.vercel.app`).

---

## Cold start (Render free tier)

Render free tier spins down the backend after ~15 minutes of inactivity. The first request after idle can take **30–60 seconds** while the service starts; the UI may show “failed to fetch” or hang until the backend responds. Later requests in the same session are fast.

**Options:**

- **Accept it** — Fine for personal/demo use.
- **UptimeRobot (free)** — Ping your Render URL every 14 minutes to prevent spin-down.
- **Paid Render tier** — Service stays up; no cold starts.

---

## CORS

If the UI shows “failed to fetch” and the backend is up, the cause is usually CORS: the browser blocks the response because the request origin is not allowed. Fix by adding the **exact** URL the user sees in the address bar (e.g. `https://ai-agent-governance.vercel.app`) to `CORS_ORIGINS` on Render, then redeploy the backend.
