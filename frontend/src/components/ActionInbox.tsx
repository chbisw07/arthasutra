import { Chip, Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material'
import type { ActionItem } from '../api/client'

function ActionChip({ a }: { a: ActionItem }) {
  const color = a.action === 'EXIT' ? 'error' : a.action === 'TRIM' ? 'warning' : a.action === 'ADD' ? 'success' : 'default'
  return <Chip size="small" color={color as any} label={a.action} />
}

export default function ActionInbox({ actions }: { actions: ActionItem[] }) {
  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Action Inbox</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Action</TableCell>
            <TableCell>Symbol</TableCell>
            <TableCell>Reason</TableCell>
            <TableCell align="right">Qty</TableCell>
            <TableCell align="right">Score</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {actions.map((a, idx) => (
            <TableRow key={`${a.symbol}-${idx}`}>
              <TableCell><ActionChip a={a} /></TableCell>
              <TableCell>{a.symbol}</TableCell>
              <TableCell>{a.reason}</TableCell>
              <TableCell align="right">{a.qty ?? '-'}</TableCell>
              <TableCell align="right">{a.score ?? '-'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  )
}

