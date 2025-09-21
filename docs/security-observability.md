# Security & Observability

Purpose

- Protect secrets, control access, and instrument the system for diagnostics.

Scope

- Secrets handling, CORS, RBAC, logging, metrics, request tracing.

Practices

- Secrets: `.env` for dev; never commit real keys. Use role‑scoped tokens.
- CORS: locked to configured domains; rate limits on public endpoints.
- Auth: JWTs with role claim (user, admin); server‑side RBAC enforcement.
- Logging: structured JSON via loguru; request ID correlation.
- Metrics: Prom‑style counters (jobs run, alerts fired); optional Grafana later.

Tasks / TODOs

- Add request/trace IDs in API responses; log correlation middleware.
- Document audit log for admin changes with versioning & rollback.

Deliverables & Acceptance

- Secrets stored safely; logs and metrics available for core pipelines; admin mutations audited.

Open Questions

- Which metrics to expose first (alerts/min, pipeline durations, error rates).

