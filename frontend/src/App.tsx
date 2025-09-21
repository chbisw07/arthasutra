import { useCallback, useEffect, useMemo, useState } from 'react'
import { AppBar, Box, Button, Container, Stack, TextField, Toolbar, Typography, Paper, Grid, Alert } from '@mui/material'
import { createPortfolio, getDashboard, importEodCSV, importHoldingsCSV, type Dashboard } from './api/client'
import PositionTable from './components/PositionTable'
import ActionInbox from './components/ActionInbox'

export default function App() {
  const [portfolioName, setPortfolioName] = useState('Core India')
  const [portfolioId, setPortfolioId] = useState<number | null>(null)
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
    if (portfolioId) {
      void refresh()
    }
  }, [portfolioId, refresh])

  async function onCreatePortfolio() {
    setLoading(true)
    setError(null)
    try {
      const pf = await createPortfolio(portfolioName || 'Portfolio')
      setPortfolioId(pf.id)
    } catch (e: any) {
      setError(e?.message || 'Failed to create portfolio')
    } finally {
      setLoading(false)
    }
  }

  async function onUploadHoldings(ev: React.ChangeEvent<HTMLInputElement>) {
    if (!portfolioId || !ev.target.files?.length) return
    const file = ev.target.files[0]
    setLoading(true)
    setError(null)
    try {
      await importHoldingsCSV(portfolioId, file)
      await refresh()
    } catch (e: any) {
      setError(e?.message || 'Failed to import holdings')
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
      await importEodCSV(file)
      await refresh()
    } catch (e: any) {
      setError(e?.message || 'Failed to import EOD prices')
    } finally {
      setLoading(false)
      ev.target.value = ''
    }
  }

  return (
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
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
              <TextField label="Portfolio Name" size="small" value={portfolioName} onChange={(e) => setPortfolioName(e.target.value)} />
              <Button variant="contained" onClick={onCreatePortfolio} disabled={loading}>Create Portfolio</Button>
              {portfolioId && <Typography variant="body2">Current ID: {portfolioId}</Typography>}
            </Stack>
          </Paper>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>Upload Holdings CSV</Typography>
                <input type="file" accept=".csv" onChange={onUploadHoldings} disabled={!canQuery || loading} />
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
            {loading && <Typography variant="body2">Loading…</Typography>}
          </Stack>

          {dashboard && (
            <>
              <Grid container spacing={2}>
                <Grid item xs={12} md={7}><PositionTable positions={dashboard.positions} /></Grid>
                <Grid item xs={12} md={5}><ActionInbox actions={dashboard.actions} /></Grid>
              </Grid>
              <Paper sx={{ p: 2, mt: 2 }}>
                <Typography variant="subtitle1">KPIs</Typography>
                <Typography variant="body2">Equity: ₹{dashboard.equity_value.toFixed(2)} · PnL: ₹{dashboard.pnl_inr.toFixed(2)}</Typography>
              </Paper>
            </>
          )}
        </Stack>
      </Container>
    </Box>
  )
}

