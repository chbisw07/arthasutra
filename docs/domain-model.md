# Domain Model (SQLite)

Purpose

- Define the minimum viable schema for ArthaSutra and indexing strategy.

Scope

- Core entities required for Phase‑01/02 and forward compatibility with overlay/backtests.

Tables (minimum viable)

- portfolios (id, name, base_ccy, tz, created_at)
- securities (id, symbol, exchange, name, sector, lot_size, tick_size)
- holdings (id, portfolio_id, security_id, qty_total, avg_price)
- lots (id, holding_id, qty, price, date, account, tax_status)
- benchmarks (id, code, description)
- prices_eod (security_id, date, ohlc, volume)
- prices_intraday (security_id, ts, ohlc, volume)
- signals (id, portfolio_id, security_id, date, q, t, v, score, reason)
- orders (id, side, qty, limit, stop, tif, status, reason, created_at)
- trades (id, order_id, fill_qty, fill_px, fee, tax, lot_links)
- metrics_daily (portfolio_id, date, cagr, sharpe, sortino, maxdd, exposure_json)
- alerts (id, portfolio_id, type, security_id, rule_id, payload_json, status)
- configs (portfolio_id, yaml_text, updated_at)

Indexes

- prices: (security_id, date) and (security_id, ts)
- holdings/signals: (portfolio_id, security_id)

Decisions (final)

- Use SQLModel/SQLAlchemy models; migrations optional with Alembic (SQLite‑aware) if schema evolves frequently.

Tasks / TODOs

- Implement SQLModel classes and metadata with indexes.
- Seed fixtures for a tiny portfolio and EOD price samples for tests.

Deliverables & Acceptance

- CRUD works for portfolios/securities/holdings; basic queries performant with indexes.

Open Questions

- Normalize vs store denormalized metrics? Start normalized; add materialized views later if needed.

