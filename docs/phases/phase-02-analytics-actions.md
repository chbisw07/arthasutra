# Phase 02 — Analytics & Actions v1

Purpose

- Add basic analytics for positions and a minimal decision engine to surface actions on the dashboard; expose positions endpoint and data import helpers.

Scope (in/out)

- In: services analytics (pnl, pct_today), decision rules v1 (SMA50/200 trend), endpoints for positions and yfinance EOD import, frontend tables for positions and action inbox.
- Out: overlay engine, alerts WS, parity harness (next phases).

Deliverables & Acceptance

- GET `/portfolios/{id}/positions` returns symbol, qty, avg_price, last_price, prev_close, pct_today, pnl_inr.
- GET `/portfolios/{id}/dashboard` includes `actions` from rules v1.
- POST `/data/prices-eod/import-csv` and `/data/prices-eod/yf` work.
- Frontend shows positions and action inbox; demo seed button populates recent EOD data.
- Tests cover positions/actions flow.

Tasks / TODOs

- Implement analytics service: latest/prev close, pct_today, PnL.
- Implement decision_engine v1: SMA50/200 trend rules (EXIT/TRIM/ADD/KEEP).
- Add positions endpoint; extend dashboard to return actions.
- Add yfinance import helper in backend; wire frontend seed button.
- Frontend: CSV column‑mapper dialog and upload.

Open Questions

- Thresholds for TRIM/ADD in v1; configurable in future via config.yaml.

