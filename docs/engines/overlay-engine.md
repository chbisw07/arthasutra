# Overlay Engine

Purpose

- Harvest swings via trims/add‑backs while keeping net units stable over a window.

Scope

- TP/buyback thresholds, ATR bands, flexible restoration, net‑units stabilizer.

Rules (v1)

- Trim at +tp1_percent (e.g., +8%) by tp1_trim_pct (e.g., 20%).
- Buy back at buyback_percent from last trim (e.g., −3%) by buyback_add_pct.
- ATR‑based stops/targets (atr_mult_stop, atr_mult_tp).
- Net‑units stabilizer: target net units over rolling window (e.g., 30 over 30 days).

Decisions (final)

- Restoration is flexible/opportunistic with aggression levels.

Tasks / TODOs

- Implement overlay state machine referencing anchor price and executed legs.
- Property tests: net‑units stabilizer never drifts beyond tolerance.
- Plot markers for trims/add‑backs in Position Detail.

Deliverables & Acceptance

- Deterministic overlay decisions for synthetic paths; tests covering edge cases.

Open Questions

- How to encode aggression presets (week, month, quarter, target_price) in config.

