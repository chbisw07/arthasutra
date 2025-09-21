# Phase 01 — Data Layer, CSV Import, Basic Dashboard

Purpose

- Establish the core backend skeleton, minimal schema, CSV import, and a simple dashboard API that surfaces basic KPIs and a placeholder Action Inbox.

Scope (in/out)

- In: FastAPI app skeleton, SQLite schema (subset), CSV import endpoint, dashboard endpoint with basic metrics, unit/integration tests, setup docs and requirements.
- Out: Overlay engine, alerts pipeline, backtests, broker execution (later phases).

Deliverables & Acceptance

- `requirements.txt` created; `pip install -r requirements.txt` succeeds.
- FastAPI app runs; `/healthz` returns 200.
- SQLite initialized with core tables; indices present.
- POST `/portfolios/{id}/import-csv` ingests sample CSV and populates holdings/lots.
- GET `/portfolios/{id}/dashboard` returns: equity value, P&L (from avg_price vs latest EOD), position list (symbol, qty, avg_price), and a placeholder `actions: []`.
- Tests: unit (CSV parsing, models), integration (import → dashboard) are green.

Architecture Notes

- Keep DB access via a single session factory; wire a per-request session in FastAPI deps.
- Data for Phase‑01 may use stubbed/latest EOD prices; actual collectors arrive later.

Tasks / TODOs

1) Repo & Environment
- Create `requirements.txt` with: fastapi, uvicorn, pydantic>=2, sqlalchemy, sqlmodel, pandas, python-dotenv, pytest, httpx, loguru.
- Add `.env.example` and load via `python-dotenv`.
- Scaffold `src/arthasutra/` with `api`, `db`, `services` packages and `tests/`.

2) Database
- Define SQLModel models for: portfolios, securities, holdings, lots, prices_eod (minimal), configs.
- Create engine and session factory; simple init script to create tables.

3) API Endpoints
- `GET /healthz` — health probe.
- `POST /portfolios` — create portfolio.
- `POST /portfolios/{id}/import-csv` — accepts CSV (symbol,exchange,qty,avg_price,sector); upsert securities, create holdings/lots.
- `GET /portfolios/{id}/dashboard` — compute equity value and P&L using `avg_price` vs latest price in `prices_eod` (or fallback to avg_price when price missing).

4) CSV Import
- Validate rows; map `NSE:SYMBOL` or split (`exchange`, `symbol`).
- Idempotent upsert for securities; aggregate holdings; store original lots.

5) Metrics (basic)
- Equity value = sum(qty * last_price) with fallback.
- Simple P&L = sum(qty * (last_price - avg_price)).

6) Testing
- Fixtures: temp SQLite, sample CSV, sample prices.
- Tests: models CRUD; import CSV success; dashboard metrics correct for fixture.

Open Questions

- Do we load initial EOD prices via a simple CSV file for Phase‑01, or mock a fetcher?
- Do we include Alembic for migrations now or defer until Phase‑02?

Notes

- Keep response shapes close to docs/api.md; evolve as Phase‑02 adds analytics and actions.

