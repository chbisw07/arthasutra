# ArthaSutra (backend)

Developer quickstart

- Create venv and install in editable mode:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e ".[dev]"`
- Run API: `arthasutra-api` (defaults to 127.0.0.1:8000 with reload)
  - To avoid OS file watcher limits, the CLI watches only the package dir by default.
  - Options: `--reload-dir <path>` to add more, `--reload-polling` to force a low‑FD polling watcher, or `--no-reload` to disable.
- Test: `pytest -q`

Environment

- Copy `.env.example` to `.env` and set `DATABASE_URL` (defaults to sqlite file) and CORS origins.
