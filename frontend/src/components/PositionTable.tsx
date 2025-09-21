import { Table, TableBody, TableCell, TableHead, TableRow, Paper, Typography } from '@mui/material'
import type { PositionItem } from '../api/client'

export default function PositionTable({ positions }: { positions: PositionItem[] }) {
  const fmtINR = (n: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(n)
  const fmtNum = (n: number) => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(n)
  const fmtPct = (n: number) => `${n.toFixed(2)}%`
  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Positions</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Symbol</TableCell>
            <TableCell align="right">Qty</TableCell>
            <TableCell align="right">Avg Px</TableCell>
            <TableCell align="right">Last</TableCell>
            <TableCell align="right">Pct Today</TableCell>
            <TableCell align="right">PnL (₹)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {positions.map((p) => (
            <TableRow key={`${p.exchange}:${p.symbol}`}>
              <TableCell>{p.exchange}:{p.symbol}</TableCell>
              <TableCell align="right">{fmtNum(p.qty)}</TableCell>
              <TableCell align="right">{fmtINR(p.avg_price)}</TableCell>
              <TableCell align="right">{fmtINR(p.last_price)}</TableCell>
              <TableCell align="right">{p.pct_today != null ? fmtPct(p.pct_today) : '-'}</TableCell>
              <TableCell align="right">{fmtINR(p.pnl_inr)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  )
}
