# Decision Engine

Purpose

- Compute explainable actions (Keep/Add/Trim/Exit) with quantities, prices, and reasons using composite scores and rules within risk caps.

Scope

- Composite score, rule evaluation, sizing, guardrails, provenance logging.

Logic (v1)

- Composite Score: placeholder trend‑based score using 50/200 SMA.
- Rules → Actions (implemented minimal):
  - EXIT: below 200SMA and score low.
  - TRIM: last close > 1.08 × 50SMA (extended).
  - ADD: above 50SMA with healthy score.
  - KEEP: otherwise or insufficient history.
- Sizing: Qty = risk_budget / stop_distance(ATR), bounded by capital & max_position%

Decisions (final)

- Use a single calculator shared by backtest and live to guarantee parity.

Tasks / TODOs

- Implement score + rules with clear reasons and thresholds from config.
- Add risk checks (per‑trade, position, sector caps) before action finalization.
- Log provenance (rules/AI/TV) and explanations per action.

Deliverables & Acceptance

- Unit tests for score, trigger rules, sizing; integration test from CSV → actions.

Open Questions

- Final default thresholds for momentum/fade and liquidity cutoffs.
