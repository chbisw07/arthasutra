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
- Scaffold backend app with FastAPI, health endpoint, and project layout:
  - `src/arthasutra/api` (routers, deps)
  - `src/arthasutra/db` (models, session)
  - `src/arthasutra/services` (engines, workers)
  - `tests/`
- Run scripts:
  - `arthasutra-api` (options: `--host`, `--port`, `--no-reload`)
  - `pytest -q`

Deliverables & Acceptance

- `pip install -e ".[dev]"` succeeds (or `pip install -r requirements.txt`).
- `uvicorn` starts FastAPI and responds 200 on `/healthz`.
- `pytest -q` passes initial smoke tests.

Open Questions

- Do we want `pre-commit` hooks (ruff/black) now or add later in Phase‑08 (hardening)?
