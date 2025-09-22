import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableRow, Paper, Typography, TableSortLabel, Chip, Stack } from '@mui/material'
import type { PositionItem } from '../api/client'

type Order = 'asc' | 'desc'

export default function PositionTable({ positions }: { positions: PositionItem[] }) {
  const fmtINR = (n: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(n)
  const fmtNum = (n: number) => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(n)
  const fmtPct = (n: number) => `${n.toFixed(2)}%`

  const [order, setOrder] = React.useState<Order>('asc')
  const [orderBy, setOrderBy] = React.useState<
    'symbol' | 'qty' | 'avg_price' | 'last_price' | 'pct_today' | 'pnl_inr'
  >('symbol')

  const getVal = (p: PositionItem, key: typeof orderBy) => {
    switch (key) {
      case 'symbol':
        return `${p.exchange}:${p.symbol}`
      case 'qty':
        return p.qty
      case 'avg_price':
        return p.avg_price
      case 'last_price':
        return p.last_price
      case 'pct_today':
        return p.pct_today ?? Number.NEGATIVE_INFINITY
      case 'pnl_inr':
        return p.pnl_inr
    }
  }

  const sorted = React.useMemo(() => {
    const arr = [...positions]
    arr.sort((a, b) => {
      const va = getVal(a, orderBy)
      const vb = getVal(b, orderBy)
      let cmp: number
      if (typeof va === 'string' && typeof vb === 'string') {
        cmp = va.localeCompare(vb)
      } else {
        cmp = (va as number) - (vb as number)
      }
      return order === 'asc' ? cmp : -cmp
    })
    return arr
  }, [positions, order, orderBy])

  const createSortHandler = (prop: typeof orderBy) => () => {
    if (orderBy === prop) {
      setOrder(order === 'asc' ? 'desc' : 'asc')
    } else {
      setOrderBy(prop)
      setOrder('asc')
    }
  }
  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Positions</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sortDirection={orderBy === 'symbol' ? order : false as any}>
              <TableSortLabel active={orderBy === 'symbol'} direction={order} onClick={createSortHandler('symbol')}>
                Symbol
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'qty' ? order : false as any}>
              <TableSortLabel active={orderBy === 'qty'} direction={order} onClick={createSortHandler('qty')}>
                Qty
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'avg_price' ? order : false as any}>
              <TableSortLabel active={orderBy === 'avg_price'} direction={order} onClick={createSortHandler('avg_price')}>
                Avg Px
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'last_price' ? order : false as any}>
              <TableSortLabel active={orderBy === 'last_price'} direction={order} onClick={createSortHandler('last_price')}>
                Last
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'pct_today' ? order : false as any}>
              <TableSortLabel active={orderBy === 'pct_today'} direction={order} onClick={createSortHandler('pct_today')}>
                Pct Today
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'pnl_inr' ? order : false as any}>
              <TableSortLabel active={orderBy === 'pnl_inr'} direction={order} onClick={createSortHandler('pnl_inr')}>
                PnL (₹)
              </TableSortLabel>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sorted.map((p) => (
            <TableRow key={`${p.exchange}:${p.symbol}`}>
              <TableCell>{p.exchange}:{p.symbol}</TableCell>
              <TableCell align="right">{fmtNum(p.qty)}</TableCell>
              <TableCell align="right" className="num">{fmtINR(p.avg_price)}</TableCell>
              <TableCell align="right" className="num">{fmtINR(p.last_price)}</TableCell>
              <TableCell align="right">
                <Stack direction="row" spacing={0.5} justifyContent="flex-end" alignItems="center">
                  <span className="num">{p.pct_today != null ? fmtPct(p.pct_today) : '-'}</span>
                  {p.price_source && (
                    <Chip
                      size="small"
                      variant="outlined"
                      label={p.price_source === 'live' ? 'LIVE' : p.price_source === 'snapshot' ? 'SNAP' : 'EOD'}
                      color={p.price_source === 'live' ? 'success' : p.price_source === 'snapshot' ? 'info' : 'default'}
                      sx={{ height: 20, fontSize: 10, px: 0.75 }}
                    />
                  )}
                </Stack>
              </TableCell>
              <TableCell align="right" className="num">{fmtINR(p.pnl_inr)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  )
}
