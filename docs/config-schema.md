# Config Schema (`config.yaml`)

Purpose

- Specify per‑portfolio configuration knobs and defaults; ensure validation and safe ranges.

Scope

- Portfolio metadata, data provider settings, risk caps, policy weights, overlay parameters, alerts.

Schema (illustrative)

```yaml
portfolio:
  name: "Core India"
  base_ccy: "INR"
  timezone: "Asia/Kolkata"

data:
  provider: "kite"
  symbols: ["NSE:BSE", "NSE:HDFCBANK", "NSE:RELIANCE"]
  refresh_seconds: 60  # 60–3600

risk:
  max_risk_per_trade_pct: 0.75
  capital_per_trade_cap_pct: 5
  max_position_pct: 12
  max_sector_pct: 35
  slippage_bps: 10
  fees_model: "zerodha_default"

policy:
  rebalance: { type: "annual_band", band_pp: 5 }
  composite_weights: { Q: 0.4, T: 0.4, V: 0.2 }
  min_liquidity_avg_turnover_inr: 1000000

overlay:
  enabled: true
  anchor: { type: "manual", value: 2700 }
  tp1_percent: 8
  tp1_trim_pct: 20
  buyback_percent: -3
  buyback_add_pct: 20
  atr_mult_stop: 2.0
  atr_mult_tp: 2.5
  net_units_target: 30
  net_units_window_days: 30
  restoration: "flexible"

alerts:
  earnings_watch: ["NSE:INFY", "NSE:TCS"]
  rules: ["price_move", "atr_band", "rebalance_band", "risk_limit"]
```

Decisions (final)

- Validate with Pydantic models; enforce safe ranges (e.g., 60–3600 for refresh_seconds).

Tasks / TODOs

- Define Pydantic v2 models for config sections and loader.
- Add JSON schema export for frontend validation.

Deliverables & Acceptance

- Configs persist to `configs` table; API returns validated config; invalid config rejected with clear errors.

Open Questions

- Do we want per‑symbol overrides for overlay aggression in MVP or later?

Unified CSV Schema (positions)

- Canonical columns: `symbol` (e.g., HDFCBANK), `exchange` (e.g., NSE), `qty`, `avg_price`, optional `sector`, optional `name`, optional `ltp`.
- Header aliases accepted by importer:
  - symbol: `symbol`, `Symbol`, `Ticker`, `Instrument`
  - qty: `qty`, `Qty.`, `quantity`, `Quantity`, `Shares`
  - avg_price: `avg_price`, `Avg. cost`, `Avg Buy Price (Rs.)`
  - ltp: `LTP`, `Current Price (Rs.)`
  - sector: `sector`, `Sector`
  - name: `name`, `Name`
- Numbers may contain commas or `%`; negatives in parentheses are handled.
- If `exchange` missing, defaults to `NSE`. If `ltp` present, a synthetic EOD row for today is seeded.
