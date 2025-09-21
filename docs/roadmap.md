# Roadmap & Acceptance Gates

Purpose

- Sequence delivery into phases with clear acceptance gates and dependencies.

Phases

- Phase 01 — Data layer + CSV import + basic dashboard
- Phase 02 — EOD analytics + Action Inbox v1
- Phase 03 — Overlay engine + Alerts (WebSocket)
- Phase 04 — Backtest Lab + parity harness
- Phase 05 — Live quotes integration (read‑only)
- Phase 06 — Rebalance proposals + lot‑aware tax estimates
- Phase 07 — Broker order execution (Kite) + Order Manager
- Phase 08 — Hardening, tests, parallelization (Ray/Dask), UX polish

Acceptance Gates

- Unit coverage ≥70% overall; critical paths ≥85%.
- Broker execution tests passing with mocks.
- Parity harness enforces backtest ↔ live equivalence.
- Docs include test instructions and fixtures.

Dependencies

- Order Manager depends on Decision Engine and Broker Integration; integrates with Risk Engine before broker.

Tasks / TODOs

- Keep this roadmap in sync with phase docs; adjust acceptance gates as needed.

Deferred (TBD for live-market phase)

- Snapshot table for last/prev closes to remove N+1 queries.
- Batch/semi-parallel yfinance fetch with a small worker pool.
- quotes_live table for LTP and session-aware pct_today.
