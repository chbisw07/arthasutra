import { useCallback, useEffect, useMemo, useState } from 'react'
import { AppBar, Box, Button, Container, Stack, TextField, Toolbar, Typography, Paper, Grid, Alert, LinearProgress, FormControl, InputLabel, Select, MenuItem, Snackbar, FormControlLabel, Switch } from '@mui/material'
import { createPortfolio, deletePortfolio, getDashboard, getPortfolios, getPositions, importEodCSV, importEodYf, importHoldingsCSV, type Dashboard, type Portfolio } from './api/client'
import PositionTable from './components/PositionTable'
import ActionInbox from './components/ActionInbox'
import ColumnMapperDialog from './components/ColumnMapperDialog'

export default function App() {
  const [portfolioName, setPortfolioName] = useState('Core India')
  const [portfolioId, setPortfolioId] = useState<number | null>(null)
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mapperOpen, setMapperOpen] = useState(false)
  const [seeding, setSeeding] = useState(false)
  const [seedDone, setSeedDone] = useState(0)
  const [seedTotal, setSeedTotal] = useState(0)
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [snack, setSnack] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' | 'warning' }>({ open: false, message: '', severity: 'success' })
  const [autoRefresh, setAutoRefresh] = useState(false)

  const notify = (message: string, severity: 'success' | 'error' | 'info' | 'warning' = 'success') => setSnack({ open: true, message, severity })
  const closeSnack = () => setSnack((s) => ({ ...s, open: false }))

  // Format helpers (Indian numbering)
  const fmtINR = (n: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(n)
  const fmtNum = (n: number) => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(n)
  const fmtPct = (n: number) => `${n.toFixed(2)}%`

  const investedValue = (dash: Dashboard | null): number => {
    if (!dash?.positions) return 0
    return dash.positions.reduce((acc, p) => acc + p.qty * p.avg_price, 0)
  }

  const canQuery = useMemo(() => portfolioId != null, [portfolioId])

  const refresh = useCallback(async () => {
    if (!portfolioId) return
    setLoading(true)
    setError(null)
    try {
      const d = await getDashboard(portfolioId)
      setDashboard(d)
    } catch (e: any) {
      setError(e?.message || 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }, [portfolioId])

  useEffect(() => {
    // Load last selected portfolio from localStorage
    const saved = localStorage.getItem('arthasutra.portfolioId')
    if (saved) setPortfolioId(parseInt(saved, 10))
    // Load portfolios list
    void (async () => {
      try {
        setPortfolios(await getPortfolios())
      } catch {}
    })()
  }, [])

  useEffect(() => {
    if (portfolioId) {
      localStorage.setItem('arthasutra.portfolioId', String(portfolioId))
      void refresh()
    }
  }, [portfolioId, refresh])

  // Auto refresh positions when enabled
  useEffect(() => {
    if (!autoRefresh || !portfolioId) return
    const id = setInterval(() => { void refresh() }, 30000)
    return () => clearInterval(id)
  }, [autoRefresh, portfolioId, refresh])

  async function onCreatePortfolio() {
    setLoading(true)
    setError(null)
    try {
      const pf = await createPortfolio(portfolioName || 'Portfolio')
      setPortfolioId(pf.id)
      setPortfolios(await getPortfolios())
      notify('Portfolio created', 'success')
    } catch (e: any) {
      const msg = e?.message || 'Failed to create portfolio'
      setError(msg)
      notify(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  async function onDeletePortfolio() {
    if (!portfolioId) return
    if (!confirm('Delete this portfolio? This removes holdings/lots for it.')) return
    try {
      await deletePortfolio(portfolioId)
      const list = await getPortfolios()
      setPortfolios(list)
      const next = list.length ? list[0].id : null
      setPortfolioId(next)
      if (!next) {
        localStorage.removeItem('arthasutra.portfolioId')
        setDashboard(null)
      }
      notify('Portfolio deleted', 'success')
    } catch (e: any) {
      const msg = e?.message || 'Failed to delete portfolio'
      setError(msg)
      notify(msg, 'error')
    }
  }

  async function onUploadHoldings(ev: React.ChangeEvent<HTMLInputElement>) {
    if (!portfolioId || !ev.target.files?.length) return
    const file = ev.target.files[0]
    setLoading(true)
    setError(null)
    try {
      const res = await importHoldingsCSV(portfolioId, file)
      await refresh()
      notify(`Imported holdings (${res?.rows ?? 'OK'})`, 'success')
    } catch (e: any) {
      const msg = e?.message || 'Failed to import holdings'
      setError(msg)
      notify(msg, 'error')
    } finally {
      setLoading(false)
      ev.target.value = ''
    }
  }

  async function onUploadEod(ev: React.ChangeEvent<HTMLInputElement>) {
    if (!ev.target.files?.length) return
    const file = ev.target.files[0]
    setLoading(true)
    setError(null)
    try {
      const res = await importEodCSV(file)
      await refresh()
      notify(`Imported EOD prices (${res?.rows ?? 'OK'})`, 'success')
    } catch (e: any) {
      const msg = e?.message || 'Failed to import EOD prices'
      setError(msg)
      notify(msg, 'error')
    } finally {
      setLoading(false)
      ev.target.value = ''
    }
  }

  async function onSeedDemo() {
    try {
      if (!portfolioId) return
      setLoading(true)
      setSeeding(true)
      setSeedDone(0)
      setError(null)
      // prefer symbols from current dashboard; fallback to positions endpoint
      let symbols: string[] = []
      if (dashboard?.positions?.length) {
        symbols = dashboard.positions.map((p) => `${p.exchange}:${p.symbol}`)
      } else {
        const positions = await getPositions(portfolioId)
        symbols = positions.map((p) => `${p.exchange}:${p.symbol}`)
      }
      if (!symbols.length) {
        setError('No positions found to seed. Import holdings first.')
        return
      }
      setSeedTotal(symbols.length)
      // last 210 days up to today
      const end = new Date()
      const start = new Date(end)
      start.setDate(end.getDate() - 210)
      const toIso = (d: Date) => d.toISOString().slice(0, 10)
      // Seed sequentially to show incremental progress; refresh every 5 symbols
      let count = 0
      for (const token of symbols) {
        await importEodYf([token], toIso(start), toIso(end))
        count += 1
        setSeedDone(count)
        if (count % 5 === 0 || count === symbols.length) {
          await refresh()
        }
      }
      await refresh()
    } catch (e: any) {
      const msg = e?.message || 'Failed to seed demo data'
      setError(msg)
      notify(msg, 'error')
    } finally {
      setLoading(false)
      setSeeding(false)
      notify(`Seeding complete (${seedDone}/${seedTotal})`, 'success')
    }
  }

  async function onMapperImport(mapped: File) {
    if (!portfolioId) return
    try {
      const res = await importHoldingsCSV(portfolioId, mapped)
      await refresh()
      notify(`Imported holdings (${res?.rows ?? 'OK'})`, 'success')
    } catch (e: any) {
      const msg = e?.message || 'Failed to import holdings via mapper'
      setError(msg)
      notify(msg, 'error')
    }
  }

  return (<>
    <Box sx={{ height: '100%' }}>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>ArthaSutra</Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>API: {import.meta.env.VITE_API_BASE || '/api'}</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" className="container">
        <Stack spacing={2} className="section">
          {error && <Alert severity="error">{error}</Alert>}

          <Paper sx={{ p: 2 }}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ xs: 'stretch', md: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 220 }}>
                <InputLabel>Portfolio</InputLabel>
                <Select
                  label="Portfolio"
                  value={portfolioId ?? ''}
                  onChange={(e) => setPortfolioId(Number(e.target.value))}
                >
                  {portfolios.map(p => (
                    <MenuItem key={p.id} value={p.id}>{p.name} (#{p.id})</MenuItem>
                  ))}
                  {!portfolios.length && <MenuItem value=""><em>None</em></MenuItem>}
                </Select>
              </FormControl>
              <TextField label="New Portfolio Name" size="small" value={portfolioName} onChange={(e) => setPortfolioName(e.target.value)} />
              <Button variant="contained" onClick={onCreatePortfolio} disabled={loading}>Create</Button>
              <Button color="error" onClick={onDeletePortfolio} disabled={!portfolioId || loading || seeding}>Delete</Button>
              {portfolioId && <Typography variant="body2">Current ID: {portfolioId}</Typography>}
            </Stack>
          </Paper>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Upload Holdings CSV</Typography>
                <input type="file" accept=".csv" onChange={onUploadHoldings} disabled={!canQuery || loading} />
                <Button size="small" sx={{ ml: 2 }} onClick={() => setMapperOpen(true)} disabled={!canQuery}>Column Mapper…</Button>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Upload EOD Prices CSV</Typography>
                <input type="file" accept=".csv" onChange={onUploadEod} disabled={loading} />
              </Paper>
            </Grid>
          </Grid>

          <Stack direction="row" spacing={2} alignItems="center">
            <Button variant="outlined" onClick={refresh} disabled={!canQuery || loading}>Refresh Dashboard</Button>
            <Button variant="outlined" onClick={onSeedDemo} disabled={!canQuery || loading}>Seed Demo Data</Button>
            {loading && <Typography variant="body2">Loading…</Typography>}
            <FormControlLabel control={<Switch checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />} label="Auto Refresh" />
          </Stack>
          {seeding && (
            <Box sx={{ width: '100%' }}>
              <LinearProgress variant="determinate" value={seedTotal ? (seedDone / seedTotal) * 100 : 0} />
              <Typography variant="caption">Seeding {seedDone} / {seedTotal}</Typography>
            </Box>
          )}

          {dashboard && (
            <>
              <Grid container spacing={2}>
                <Grid item xs={12} md={7}><PositionTable positions={dashboard.positions} /></Grid>
                <Grid item xs={12} md={5}><ActionInbox actions={dashboard.actions} positions={dashboard.positions} /></Grid>
              </Grid>
              <Paper sx={{ p: 2, mt: 2 }}>
                <Typography variant="subtitle1">KPIs</Typography>
                <Typography variant="body2">
                  Equity: {fmtINR(dashboard.equity_value)} · PnL: {fmtINR(dashboard.pnl_inr)} · PnL %: {
                    (() => {
                      const inv = investedValue(dashboard)
                      const pct = inv > 0 ? (dashboard.pnl_inr / inv) * 100 : 0
                      return fmtPct(pct)
                    })()
                  }
                </Typography>
              </Paper>
            </>
          )}
        </Stack>
      </Container>
    </Box>
    <ColumnMapperDialog open={mapperOpen} onClose={() => setMapperOpen(false)} onImport={onMapperImport} />
    <Snackbar
      open={snack.open}
      autoHideDuration={3000}
      onClose={closeSnack}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    >
      <Alert onClose={closeSnack} severity={snack.severity} variant="filled" sx={{ width: '100%' }}>
        {snack.message}
      </Alert>
    </Snackbar>
  </>)
}
