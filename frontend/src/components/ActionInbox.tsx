import React from 'react'
import { Chip, Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography, TableSortLabel } from '@mui/material'
import type { ActionItem, PositionItem } from '../api/client'

type Order = 'asc' | 'desc'

function ActionChip({ a }: { a: ActionItem }) {
  const color = a.action === 'EXIT' ? 'error' : a.action === 'TRIM' ? 'warning' : a.action === 'ADD' ? 'success' : 'default'
  return <Chip size="small" color={color as any} label={a.action} />
}

export default function ActionInbox({ actions, positions }: { actions: ActionItem[]; positions?: PositionItem[] }) {
  const pctMap = new Map<string, number | null>()
  positions?.forEach(p => pctMap.set(`${p.exchange}:${p.symbol}`, p.pct_today ?? null))

  const [order, setOrder] = React.useState<Order>('asc')
  const [orderBy, setOrderBy] = React.useState<'action' | 'symbol' | 'reason' | 'qty' | 'pct' | 'score'>('symbol')

  const getVal = (a: ActionItem, key: typeof orderBy): string | number => {
    switch (key) {
      case 'action':
        return a.action
      case 'symbol':
        return a.symbol
      case 'reason':
        return a.reason
      case 'qty':
        return a.qty ?? Number.NEGATIVE_INFINITY
      case 'pct':
        return pctMap.get(a.symbol) ?? Number.NEGATIVE_INFINITY
      case 'score':
        return a.score ?? Number.NEGATIVE_INFINITY
    }
  }

  const sorted = React.useMemo(() => {
    const arr = [...actions]
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
  }, [actions, order, orderBy])

  const createSortHandler = (prop: typeof orderBy) => () => {
    if (orderBy === prop) setOrder(order === 'asc' ? 'desc' : 'asc')
    else { setOrderBy(prop); setOrder('asc') }
  }
  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Action Inbox</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sortDirection={orderBy === 'action' ? order : false as any}>
              <TableSortLabel active={orderBy === 'action'} direction={order} onClick={createSortHandler('action')}>Action</TableSortLabel>
            </TableCell>
            <TableCell sortDirection={orderBy === 'symbol' ? order : false as any}>
              <TableSortLabel active={orderBy === 'symbol'} direction={order} onClick={createSortHandler('symbol')}>Symbol</TableSortLabel>
            </TableCell>
            <TableCell sortDirection={orderBy === 'reason' ? order : false as any}>
              <TableSortLabel active={orderBy === 'reason'} direction={order} onClick={createSortHandler('reason')}>Reason</TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'qty' ? order : false as any}>
              <TableSortLabel active={orderBy === 'qty'} direction={order} onClick={createSortHandler('qty')}>Qty</TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'pct' ? order : false as any}>
              <TableSortLabel active={orderBy === 'pct'} direction={order} onClick={createSortHandler('pct')}>Pct Chg</TableSortLabel>
            </TableCell>
            <TableCell align="right" sortDirection={orderBy === 'score' ? order : false as any}>
              <TableSortLabel active={orderBy === 'score'} direction={order} onClick={createSortHandler('score')}>Score</TableSortLabel>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sorted.map((a, idx) => (
            <TableRow key={`${a.symbol}-${idx}`}>
              <TableCell><ActionChip a={a} /></TableCell>
              <TableCell>{a.symbol}</TableCell>
              <TableCell>{a.reason}</TableCell>
              <TableCell align="right">{a.qty ?? '-'}</TableCell>
              <TableCell align="right">{
                (() => {
                  const v = pctMap.get(a.symbol)
                  return v === undefined || v === null ? '-' : `${v.toFixed(2)}%`
                })()
              }</TableCell>
              <TableCell align="right">{a.score ?? '-'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  )
}
