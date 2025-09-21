import { useEffect, useMemo, useState } from 'react'
import Papa from 'papaparse'
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from '@mui/material'

type Mapping = {
  symbol?: string
  exchange?: string
  qty?: string
  avg_price?: string
  sector?: string
  name?: string
  ltp?: string
}

const CANONICAL = ['symbol', 'exchange', 'qty', 'avg_price', 'sector', 'name', 'ltp'] as const

const DEFAULT_ALIASES: Record<string, string[]> = {
  symbol: ['symbol', 'Symbol', 'Ticker', 'Instrument', 'instrument'],
  exchange: ['exchange', 'Exchange'],
  qty: ['qty', 'Qty.', 'quantity', 'Quantity', 'Shares', 'shares'],
  avg_price: ['avg_price', 'Avg. cost', 'Avg Buy Price (Rs.)', 'avgPrice', 'average_price'],
  sector: ['sector', 'Sector'],
  name: ['name', 'Name'],
  ltp: ['LTP', 'Current Price (Rs.)', 'ltp'],
}

function guessMapping(headers: string[]): Mapping {
  const map: Mapping = {}
  for (const key of CANONICAL) {
    const aliases = DEFAULT_ALIASES[key] || []
    const found = headers.find((h) => aliases.includes(h))
    if (found) (map as any)[key] = found
  }
  return map
}

export default function ColumnMapperDialog({
  open,
  onClose,
  onImport,
}: {
  open: boolean
  onClose: () => void
  onImport: (file: File) => Promise<void> | void
}) {
  const [file, setFile] = useState<File | null>(null)
  const [rows, setRows] = useState<any[]>([])
  const [headers, setHeaders] = useState<string[]>([])
  const [mapping, setMapping] = useState<Mapping>({})
  const [defaultExchange, setDefaultExchange] = useState('NSE')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!file) return
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (res) => {
        const data = (res.data as any[]).slice(0, 50)
        setRows(data)
        const hdrs = res.meta.fields || Object.keys(data[0] || {})
        setHeaders(hdrs)
        setMapping(guessMapping(hdrs))
      },
    })
  }, [file])

  const previewRows = useMemo(() => rows.slice(0, 5), [rows])

  const handleImport = async () => {
    if (!rows.length) return
    // Re-map to canonical headers
    const remapped = rows.map((r) => {
      const out: any = {}
      out.symbol = mapping.symbol ? r[mapping.symbol] : ''
      out.exchange = (mapping.exchange ? r[mapping.exchange] : '') || defaultExchange
      out.qty = mapping.qty ? r[mapping.qty] : ''
      out.avg_price = mapping.avg_price ? r[mapping.avg_price] : ''
      out.sector = mapping.sector ? r[mapping.sector] : ''
      out.name = mapping.name ? r[mapping.name] : ''
      out.ltp = mapping.ltp ? r[mapping.ltp] : ''
      return out
    })
    const csv = Papa.unparse(remapped, { columns: CANONICAL as unknown as string[] })
    const blob = new Blob([csv], { type: 'text/csv' })
    const mappedFile = new File([blob], 'mapped_holdings.csv', { type: 'text/csv' })
    setBusy(true)
    try {
      await onImport(mappedFile)
      onClose()
      setFile(null)
      setRows([])
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>CSV Column Mapper</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />

          {headers.length > 0 && (
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              {CANONICAL.map((key) => (
                <FormControl key={key} size="small" sx={{ minWidth: 160 }}>
                  <InputLabel>{key}</InputLabel>
                  <Select
                    value={(mapping as any)[key] || ''}
                    label={key}
                    onChange={(e) => setMapping((m) => ({ ...m, [key]: e.target.value }))}
                  >
                    <MenuItem value=""><em>None</em></MenuItem>
                    {headers.map((h) => (
                      <MenuItem key={h} value={h}>{h}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ))}
              <TextField
                size="small"
                label="Default Exchange"
                value={defaultExchange}
                onChange={(e) => setDefaultExchange(e.target.value)}
                sx={{ minWidth: 160 }}
              />
            </Stack>
          )}

          {previewRows.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>Preview (first 5 rows)</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {headers.map((h) => (
                      <TableCell key={h}>{h}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {previewRows.map((r, i) => (
                    <TableRow key={i}>
                      {headers.map((h) => (
                        <TableCell key={h}>{r[h]}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button onClick={handleImport} variant="contained" disabled={!rows.length || busy}>Import</Button>
      </DialogActions>
    </Dialog>
  )
}

