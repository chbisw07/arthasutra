from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from arthasutra.db.models import (
    Portfolio,
    Security,
    Holding,
    Lot,
    PriceEOD,
)
from arthasutra.db.session import get_session
from arthasutra.services.csv_importer import parse_positions_csv


router = APIRouter()


class PortfolioCreate(BaseModel):
    name: str
    base_ccy: str = "INR"
    tz: str = "Asia/Kolkata"


class PositionItem(BaseModel):
    symbol: str
    exchange: str
    qty: float
    avg_price: float
    last_price: float
    pnl_inr: float


class DashboardResponse(BaseModel):
    portfolio_id: int
    portfolio_name: str
    equity_value: float
    pnl_inr: float
    positions: list[PositionItem]
    actions: list[dict[str, Any]]


@router.post("", response_model=Portfolio)
def create_portfolio(payload: PortfolioCreate, session: Session = Depends(get_session)) -> Portfolio:
    pf = Portfolio(name=payload.name, base_ccy=payload.base_ccy, tz=payload.tz)
    session.add(pf)
    session.commit()
    session.refresh(pf)
    return pf


@router.post("/{portfolio_id}/import-csv")
def import_csv(
    portfolio_id: int,
    file: UploadFile,
    session: Session = Depends(get_session),
) -> dict:
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    rows = parse_positions_csv(file.file)
    # Upsert securities and set holdings to CSV snapshot; create a lot per row
    for r in rows:
        symbol = r.symbol
        exchange = r.exchange
        qty = float(r.qty)
        avg_price = float(r.avg_price)
        sector = r.sector

        sec = session.exec(
            select(Security).where(Security.symbol == symbol, Security.exchange == exchange)
        ).first()
        if not sec:
            sec = Security(symbol=symbol, exchange=exchange, name=symbol, sector=sector)
            session.add(sec)
            session.flush()

        holding = session.exec(
            select(Holding).where(Holding.portfolio_id == portfolio_id, Holding.security_id == sec.id)
        ).first()
        if not holding:
            holding = Holding(portfolio_id=portfolio_id, security_id=sec.id, qty_total=qty, avg_price=avg_price)
            session.add(holding)
            session.flush()
        else:
            # Snapshot import: overwrite with provided quantities and avg price
            holding.qty_total = qty
            holding.avg_price = avg_price

        lot = Lot(holding_id=holding.id, qty=qty, price=avg_price, account="main", tax_status="unknown")
        session.add(lot)

    session.commit()
    return {"status": "ok", "rows": len(rows)}


@router.get("/{portfolio_id}/dashboard", response_model=DashboardResponse)
def get_dashboard(portfolio_id: int, session: Session = Depends(get_session)) -> DashboardResponse:
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = session.exec(select(Holding).where(Holding.portfolio_id == portfolio_id)).all()

    positions: list[PositionItem] = []
    total_equity = 0.0
    total_pnl = 0.0

    for h in holdings:
        sec: Optional[Security] = session.get(Security, h.security_id)
        if not sec:
            # Skip inconsistent rows
            continue
        # Latest EOD price if present
        latest: Optional[PriceEOD] = session.exec(
            select(PriceEOD)
            .where(PriceEOD.security_id == sec.id)
            .order_by(PriceEOD.date.desc())
        ).first()
        last_price = float(latest.close) if latest else float(h.avg_price)
        pnl = float(h.qty_total) * (last_price - float(h.avg_price))
        equity = float(h.qty_total) * last_price
        total_equity += equity
        total_pnl += pnl
        positions.append(
            PositionItem(
                symbol=sec.symbol,
                exchange=sec.exchange,
                qty=float(h.qty_total),
                avg_price=float(h.avg_price),
                last_price=last_price,
                pnl_inr=pnl,
            )
        )

    return DashboardResponse(
        portfolio_id=portfolio.id,
        portfolio_name=portfolio.name,
        equity_value=total_equity,
        pnl_inr=total_pnl,
        positions=positions,
        actions=[],
    )

