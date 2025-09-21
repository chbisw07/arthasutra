# Decision Engine

Purpose

- Compute explainable actions (Keep/Add/Trim/Exit) with quantities, prices, and reasons using composite scores and rules within risk caps.

Scope

- Composite score, rule evaluation, sizing, guardrails, provenance logging.

Logic (v1)

- Composite Score: 0.4*Q + 0.4*T + 0.2*V
- Rules → Actions:
  - EXIT: score < 40 and <200DMA and EPS_rev_neg (or stop hit)
  - TRIM: overweight vs target or extended vs 50DMA with momentum fading
  - ADD: score > 70, underweight, budget ok, liquidity ok
  - KEEP: otherwise
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

