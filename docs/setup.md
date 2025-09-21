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

- Create `requirements.txt` with minimal Phase‑01 deps (fastapi, uvicorn, pydantic>=2, sqlalchemy, sqlmodel, pandas, python-dotenv, pytest, httpx, loguru).
- Add `.env.example` with placeholders: `KITE_API_KEY`, `KITE_API_SECRET`, `KITE_ACCESS_TOKEN` (later), `DATABASE_URL` (default sqlite path).
- Scaffold backend app with FastAPI, health endpoint, and project layout:
  - `src/arthasutra/api` (routers, deps)
  - `src/arthasutra/db` (models, session)
  - `src/arthasutra/services` (engines, workers)
  - `tests/`
- Add run scripts:
  - `PYTHONPATH=src uvicorn arthasutra.api.main:app --reload`
  - `pytest -q`

Deliverables & Acceptance

- `pip install -r requirements.txt` succeeds.
- `uvicorn` starts FastAPI and responds 200 on `/healthz`.
- `pytest -q` passes initial smoke tests.

Open Questions

- Do we want `pre-commit` hooks (ruff/black) now or add later in Phase‑08 (hardening)?
