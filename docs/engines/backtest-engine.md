# Backtest Engine

Purpose

- Evaluate policies and overlay on historical data, producing metrics and trade logs.

Scope

- Inputs/outputs, metrics, parity with live engine, performance considerations.

Inputs

- Portfolio snapshot (CSV), date range, policy & overlay config, historical prices.

Outputs

- CAGR, Sharpe/Sortino, MaxDD, turnover, overlay P&L, trade log, attribution.

Decisions (final)

- Use the same calculators and config path as live (no duplicate logic).

Tasks / TODOs

- Implement data loaders and deterministic calculators reused by live engine.
- Add parity tests on synthetic paths vs live code paths.

Deliverables & Acceptance

- Backtests reproducible; parity tests pass; metrics match expected on fixtures.

Open Questions

- Sampling frequency for indicators (minute vs EOD) in overlay sims for MVP.

