import { Table, TableBody, TableCell, TableHead, TableRow, Paper, Typography } from '@mui/material'
import type { PositionItem } from '../api/client'

export default function PositionTable({ positions }: { positions: PositionItem[] }) {
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
              <TableCell align="right">{p.qty}</TableCell>
              <TableCell align="right">{p.avg_price.toFixed(2)}</TableCell>
              <TableCell align="right">{p.last_price.toFixed(2)}</TableCell>
              <TableCell align="right">{p.pct_today != null ? p.pct_today.toFixed(2) + '%' : '-'}</TableCell>
              <TableCell align="right">{p.pnl_inr.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  )
}

