# Architecture

Purpose

- Define system components, boundaries, and key data flows to keep implementation consistent and testable.

Scope

- Services: API Gateway (FastAPI), Decision Engine, Overlay Engine, Backtest Engine, Alerts Orchestrator, AI Orchestrator.
- Storage: SQLite (tables per domain‑model), optional parquet feature store.
- Integrations: Zerodha Kite (REST/WebSocket), TradingView webhook, News/announcements (later).

Decisions (final)

- Persistence: SQLite to start; indexes on `(security_id, date)` and `(portfolio_id, security_id)`.
- Live comms: WebSocket for alerts push.
- Scheduling: APScheduler for jobs (EOD/minute pipelines).
- Concurrency: `concurrent.futures`/multiprocessing initially; consider Ray/Dask later for heavy workloads (backtests, simulations).

High‑Level Components

- API Gateway: REST endpoints and auth, delegates to engines and workers.
- Decision Engine: composite scoring (Q/T/V), rules → actions, guardrails.
- Overlay Engine: TP/buyback, ATR bands, net‑units stabilizer.
- Backtest Engine: uses same calculators as live (parity requirement).
- Alerts Orchestrator: consumes minute bars/LTP, evaluates rules, emits WS alerts.
- AI Orchestrator (bounded): optional nudges (size/score) within risk caps.

Data Flows (summary)

- UI ↔ API for dashboards, actions, configs; UI ↔ WS for alerts.
- Collectors write prices to SQLite; engines read holdings/prices/signals to compute KPIs and actions.
- Order Manager (later) validates against Risk Engine then routes to broker.

Tasks / TODOs

- Document service interfaces and error contracts for each engine.
- Add sequence diagrams for: dashboard load, minute tick alert, backtest run, order placement (later).

Deliverables & Acceptance

- Component boundaries documented; parity constraint called out for backtest vs live.

Open Questions

- Finalize whether to adopt a lightweight event bus for internal fan‑out (e.g., asyncio queues) versus direct service calls.

