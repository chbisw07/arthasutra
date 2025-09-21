# Zerodha Kite Integration

Purpose

- Document usage of Kite REST/WebSocket for quotes, prices, and order routing (later phase), including testing with mocks.

Scope

- Auth, rate limits, data coverage (EOD/minute/LTP), wrapper design, mock strategy for tests.

Decisions (final)

- Store keys in `.env`; never ship real credentials.
- Cache 1 day of minute data locally; fallback to Kite/Yahoo if missing.

Tasks / TODOs

- Create a lightweight client wrapper (quotes, instruments, historical candles).
- Add WebSocket consumer for LTP/mini‑bars feeding Alerts Orchestrator.
- Provide pytest mocks for REST and WS flows; simulate order placement in tests.

Deliverables & Acceptance

- Wrapper tested; rate limit handling verified; retry/backoff policy documented.

Open Questions

- Precise per‑endpoint rate limits and recommended batching strategies for MVP.

