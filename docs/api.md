# API (FastAPI)

Purpose

- Define REST endpoints, WebSocket topics, and contracts for backend–frontend integration.

Scope

- Portfolio CRUD, imports, dashboards, positions, backtests, overlay simulation, alerts, quotes, orders.

REST Endpoints (high‑level)

- POST /portfolios — create
- GET /portfolios | /portfolios/{id} — list/read
- DELETE /portfolios/{id} — delete portfolio (and dependent holdings/lots/configs)
- POST /portfolios/{id}/import-csv — seed holdings/lots
- GET /portfolios/{id}/dashboard — summary KPIs + actions
- GET /portfolios/{id}/positions — tiles (`pct_today`, `pnl_inr`, `score`)
- POST /portfolios/{id}/rebalance/propose — drift fix proposal
- POST /portfolios/{id}/overlay/simulate — run overlay rule simulation
- POST /backtests/run — policy + overlay backtest; body: date range, config
- GET /alerts | POST /alerts/ack — outstanding alerts + acknowledgements
- GET /quotes?symbols=... — live quotes (Kite wrapper)
  - Current implementation uses yfinance polling to populate quotes_live; response includes ltp and timestamp.
- POST /orders/place — submit order via Zerodha (later phase)
- POST /orders/cancel — cancel order
- GET /orders/status/{id} — track status

Data Import

- POST /data/prices-eod/import-csv — bulk import historical EOD prices (symbol, exchange, date, open, high, low, close, volume)
- POST /data/prices-eod/yf?symbols=NSE:HDFCBANK,BSE:BSE&start=YYYY-MM-DD&end=YYYY-MM-DD — fetch EOD from Yahoo Finance and persist
- GET /data/quotes?symbols=NSE:SYM1,NSE:SYM2 — get current LTP (from quotes_live)

WebSocket

- /ws/alerts — push band hits, risk breaches, earnings reminders

Auth & RBAC

- JWT‑based; roles: user, admin. Admin routes for defaults, integrations, and audit.

Tasks / TODOs

- Define request/response models (Pydantic) and error contracts.
- Add OpenAPI tags and examples; wire up WS with simple heartbeat.

Deliverables & Acceptance

- OpenAPI docs render; sample responses available; WS messages validated.

Open Questions

- Pagination and filtering defaults for list endpoints (e.g., positions, alerts).
