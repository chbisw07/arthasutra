# ArthaSutra (backend)

Developer quickstart

- Create venv and install in editable mode:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e ".[dev]"`
- Run API: `arthasutra-api` (defaults to 127.0.0.1:8000 with reload)
- Test: `pytest -q`

Environment

- Copy `.env.example` to `.env` and set `DATABASE_URL` (defaults to sqlite file) and CORS origins.

