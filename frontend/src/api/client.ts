import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || '/api'
export const api = axios.create({ baseURL })

export type Portfolio = { id: number; name: string; base_ccy: string; tz: string }

export type PositionItem = {
  symbol: string
  exchange: string
  qty: number
  avg_price: number
  last_price: number
  prev_close?: number | null
  pct_today?: number | null
  pnl_inr: number
  price_source?: 'live' | 'eod' | null
}

export type ActionItem = {
  action: 'KEEP' | 'ADD' | 'TRIM' | 'EXIT'
  symbol: string
  reason: string
  qty?: number | null
  score?: number | null
}

export type Dashboard = {
  portfolio_id: number
  portfolio_name: string
  equity_value: number
  pnl_inr: number
  positions: PositionItem[]
  actions: ActionItem[]
}

export async function createPortfolio(name: string): Promise<Portfolio> {
  const res = await api.post('/portfolios', { name })
  return res.data
}

export async function getPortfolios(): Promise<Portfolio[]> {
  const res = await api.get('/portfolios')
  return res.data
}

export async function deletePortfolio(id: number): Promise<void> {
  await api.delete(`/portfolios/${id}`)
}

export async function importHoldingsCSV(portfolioId: number, file: File): Promise<{ status: string; rows: number }> {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post(`/portfolios/${portfolioId}/import-csv`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function importEodCSV(file: File): Promise<{ status: string; rows: number }> {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post(`/data/prices-eod/import-csv`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function importEodYf(symbolTokens: string[], start: string, end: string): Promise<{ status: string; rows: number }> {
  const params = { symbols: symbolTokens.join(','), start, end }
  const res = await api.post(`/data/prices-eod/yf`, null, { params })
  return res.data
}

export async function getDashboard(portfolioId: number): Promise<Dashboard> {
  const res = await api.get(`/portfolios/${portfolioId}/dashboard`)
  return res.data
}

export async function getPositions(portfolioId: number): Promise<PositionItem[]> {
  const res = await api.get(`/portfolios/${portfolioId}/positions`)
  return res.data
}
