from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlmodel import Session, select

from arthasutra.db.models import Holding, Security, PriceEOD
from arthasutra.services.live import get_fresh_ltp, is_market_session


@dataclass
class PositionStats:
    symbol: str
    exchange: str
    qty: float
    avg_price: float
    last_price: float
    prev_close: float | None
    pnl_inr: float
    pct_today: float | None
    price_source: str | None = None


def latest_and_prev_close(session: Session, security_id: int) -> tuple[Optional[float], Optional[float]]:
    rows = session.exec(
        select(PriceEOD).where(PriceEOD.security_id == security_id).order_by(PriceEOD.date.desc()).limit(2)
    ).all()
    if not rows:
        return None, None
    latest = float(rows[0].close)
    prev = float(rows[1].close) if len(rows) > 1 else None
    return latest, prev


def compute_position_stats(session: Session, holding: Holding) -> Optional[PositionStats]:
    sec = session.get(Security, holding.security_id)
    if not sec:
        return None
    last, prev = latest_and_prev_close(session, sec.id)
    # Prefer fresh LTP during session; else fall back to EOD last
    ltp = get_fresh_ltp(session, sec.id) if is_market_session() else None
    ref_last = ltp if ltp is not None else last
    last_price = float(ref_last) if ref_last is not None else float(holding.avg_price)
    pnl = float(holding.qty_total) * (last_price - float(holding.avg_price))
    base_for_pct = prev if prev is not None else last
    pct_today = ((last_price - base_for_pct) / base_for_pct * 100.0) if (base_for_pct and last_price is not None) else None
    return PositionStats(
        symbol=sec.symbol,
        exchange=sec.exchange,
        qty=float(holding.qty_total),
        avg_price=float(holding.avg_price),
        last_price=last_price,
        prev_close=prev,
        pnl_inr=pnl,
        pct_today=pct_today,
        price_source="live" if ltp is not None else "eod",
    )


def portfolio_equity_and_pnl(session: Session, portfolio_id: int) -> tuple[float, float]:
    holdings = session.exec(select(Holding).where(Holding.portfolio_id == portfolio_id)).all()
    total_equity = 0.0
    total_pnl = 0.0
    for h in holdings:
        stats = compute_position_stats(session, h)
        if not stats:
            continue
        total_equity += stats.qty * stats.last_price
        total_pnl += stats.pnl_inr
    return total_equity, total_pnl
