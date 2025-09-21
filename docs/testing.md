# Testing Strategy

Purpose

- Ensure confidence via layered tests: unit, property, integration, and E2E smoke.

Scope

- Engines, pipelines, API endpoints, broker integration (mocks), parity harness.

Plan

- Unit: fee model, ATR, sizing, composite score, overlay triggers, lot accounting.
- Property: net‑units stabilizer tolerance over rolling window.
- Integration: CSV import → analytics → action inbox; backtest vs live parity.
- E2E smoke: create portfolio → import CSV → dashboard → backtest → actions.
- Broker execution: mock Kite API for place/modify/cancel flows.

Decisions (final)

- Coverage goals: ≥70% overall, ≥85% for critical paths (execution, risk, decision engines).

Tasks / TODOs

- Establish pytest fixtures (temp SQLite DB, sample CSV, price data).
- Add CI‑ready test commands and markers (e.g., `-m e2e` for smoke).

Deliverables & Acceptance

- Tests green locally; parity tests protect regressions; coverage thresholds met.

Open Questions

- Which tests to parallelize first (pytest‑xdist or later via Ray for sims).

