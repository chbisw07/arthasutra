# ArthaSutra — Overview

Purpose

- Summarize the product vision, goals, and success criteria to keep scope aligned as we build in phases.

Scope

- In: India cash equity to start (NSE/BSE), rules‑driven portfolio with explainable actions, risk caps, backtest→live parity, optional AI (bounded), broker order execution (Zerodha) in later phase.
- Out (initially): Derivatives, leverage, smart order routing (may come later), premium data sources.

Decisions (final)

- UI Kit: Material UI (React). Update cadence defaults: 60s (configurable up to 60m).
- Overlay restoration: flexible/opportunistic with aggression levels.
- Risk defaults tuned for Indian equities; Zerodha fees/taxes template.

Success Criteria

- Action Inbox with quantified, explainable Keep/Add/Trim/Exit suggestions.
- Backtest → Deploy parity using the same calculators.
- Risk managed: position/sector caps, per‑trade risk, bounded drawdowns.
- Low friction: CSV import, multi‑portfolio CRUD, config‑driven knobs.
- Executable: place orders via broker (later phase validated with mocks first).

Tasks / TODOs

- Keep this document current when higher‑level scope changes.
- Link to phase documents for actionable work.

Deliverables & Acceptance

- This doc acts as the single source for vision and non‑goals; referenced by phase docs and architecture.

Open Questions

- Visual explainability details (drill‑downs layout), portfolio goals in config, premium data/news APIs, expansion cadence (multi‑broker vs advanced analytics), opt‑in user action logging for AI personalization.

