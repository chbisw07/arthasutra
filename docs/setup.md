# Setup

Purpose

- Define a reproducible local dev environment for backend (and optionally frontend) so contributors can run, test, and iterate quickly.

Scope

- Backend: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy/SQLModel, SQLite, pytest.
- Optional (later): Frontend React + Vite + Material UI.

Decisions (final)

- Python: 3.11.
- Package management: `pip` + `requirements.txt` (lock later if needed).
- Env: `.env` for secrets (never commit real keys).
- Test framework: `pytest`.

Tasks / TODOs

- Prefer editable install for dev (avoids PYTHONPATH):
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e ".[dev]"`
- Add `.env` from `.env.example` and set `DATABASE_URL` (defaults to sqlite file).
  - For live quotes via Zerodha, set: `KITE_API_KEY`, `KITE_ACCESS_TOKEN`.
  - Choose provider with env var: `LIVE_PROVIDER=kite` (Kite WS) or `LIVE_PROVIDER=yf` (default yfinance poller).
- Scaffold backend app with FastAPI, health endpoint, and project layout:
  - `src/arthasutra/api` (routers, deps)
  - `src/arthasutra/db` (models, session)
  - `src/arthasutra/services` (engines, workers)
  - `tests/`
- Run scripts:
  - `arthasutra-api` (options: `--host`, `--port`, `--no-reload`, `--reload-dir`)
    - The CLI limits reload watching to `src/arthasutra` by default to prevent OS file watcher exhaustion; add more watched paths with `--reload-dir` if needed.
  - `pytest -q`

Live quotes (dev)

- The backend starts a yfinance polling job by default (interval `LIVE_POLL_SECONDS`, default 60s) to populate `quotes_live`.
- Configure env var: `LIVE_POLL_SECONDS=30 arthasutra-api` to tighten cadence.
- Production: swap to broker WS (Zerodha Kite) in a later phase for real-time LTP.

Frontend (dev)

- Prereqs: Node.js 18+ (or 20+)
- Install deps: `cd frontend && npm install`
- Start dev server: `npm run dev`
  - Vite dev server runs on http://localhost:5173 and proxies `/api` → http://127.0.0.1:8000
  - Ensure backend CORS allows http://localhost:5173 (default in `.env.example`).
  - If you hit "too many open files" (EMFILE) on Linux, use polling: `npm run dev:poll`.
    - Alternatively, raise inotify limits: `sudo sysctl fs.inotify.max_user_watches=524288 fs.inotify.max_user_instances=1024` (persist in `/etc/sysctl.conf`).

Deliverables & Acceptance

- `pip install -e ".[dev]"` succeeds (or `pip install -r requirements.txt`).
- `uvicorn` starts FastAPI and responds 200 on `/healthz`.
- `pytest -q` passes initial smoke tests.

Open Questions

- Do we want `pre-commit` hooks (ruff/black) now or add later in Phase‑08 (hardening)?
