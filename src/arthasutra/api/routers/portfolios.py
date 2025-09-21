from __future__ import annotations

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
    ConfigText,
)
from arthasutra.db.session import get_session
from arthasutra.services.analytics import portfolio_equity_and_pnl, compute_position_stats
from arthasutra.services.decision_engine import propose_actions
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
    prev_close: float | None = None
    pct_today: float | None = None
    pnl_inr: float


class DashboardResponse(BaseModel):
    portfolio_id: int
    portfolio_name: str
    equity_value: float
    pnl_inr: float
    positions: list[PositionItem]
    actions: list[dict[str, Any]]


@router.get("", response_model=list[Portfolio])
def list_portfolios(session: Session = Depends(get_session)) -> list[Portfolio]:
    return session.exec(select(Portfolio).order_by(Portfolio.id.asc())).all()


@router.get("/{portfolio_id}", response_model=Portfolio)
def get_portfolio(portfolio_id: int, session: Session = Depends(get_session)) -> Portfolio:
    pf = session.get(Portfolio, portfolio_id)
    if not pf:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return pf


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
    from datetime import date as _date
    today = _date.today()
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
            sec = Security(symbol=symbol, exchange=exchange, name=r.name or symbol, sector=sector)
            session.add(sec)
            session.flush()
        else:
            # Update security details if provided
            if r.name and not sec.name:
                sec.name = r.name
            if sector and not sec.sector:
                sec.sector = sector

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

        # If LTP is present, seed a PriceEOD for today if missing to enable immediate KPIs
        if r.ltp is not None:
            exists = session.exec(
                select(PriceEOD).where(PriceEOD.security_id == sec.id, PriceEOD.date == today)
            ).first()
            if not exists:
                pe = PriceEOD(security_id=sec.id, date=today, open=r.ltp, high=r.ltp, low=r.ltp, close=r.ltp)
                session.add(pe)

    session.commit()
    return {"status": "ok", "rows": len(rows)}


@router.get("/{portfolio_id}/dashboard", response_model=DashboardResponse)
def get_dashboard(portfolio_id: int, session: Session = Depends(get_session)) -> DashboardResponse:
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = session.exec(select(Holding).where(Holding.portfolio_id == portfolio_id)).all()
    positions: list[PositionItem] = []
    total_equity, total_pnl = portfolio_equity_and_pnl(session, portfolio_id)
    for h in holdings:
        stats = compute_position_stats(session, h)
        if not stats:
            continue
        positions.append(
            PositionItem(
                symbol=stats.symbol,
                exchange=stats.exchange,
                qty=stats.qty,
                avg_price=stats.avg_price,
                last_price=stats.last_price,
                prev_close=stats.prev_close,
                pct_today=stats.pct_today,
                pnl_inr=stats.pnl_inr,
            )
        )

    return DashboardResponse(
        portfolio_id=portfolio.id,
        portfolio_name=portfolio.name,
        equity_value=total_equity,
        pnl_inr=total_pnl,
        positions=positions,
        actions=propose_actions(session, portfolio_id),
    )


@router.get("/{portfolio_id}/positions", response_model=list[PositionItem])
def list_positions(portfolio_id: int, session: Session = Depends(get_session)) -> list[PositionItem]:
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    items: list[PositionItem] = []
    holdings = session.exec(select(Holding).where(Holding.portfolio_id == portfolio_id)).all()
    for h in holdings:
        stats = compute_position_stats(session, h)
        if not stats:
            continue
        items.append(
            PositionItem(
                symbol=stats.symbol,
                exchange=stats.exchange,
                qty=stats.qty,
                avg_price=stats.avg_price,
                last_price=stats.last_price,
                prev_close=stats.prev_close,
                pct_today=stats.pct_today,
                pnl_inr=stats.pnl_inr,
            )
        )
    return items


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int, session: Session = Depends(get_session)) -> dict:
    pf = session.get(Portfolio, portfolio_id)
    if not pf:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Delete dependent rows: lots -> holdings -> configs
    holdings = session.exec(select(Holding).where(Holding.portfolio_id == portfolio_id)).all()
    for h in holdings:
        lots = session.exec(select(Lot).where(Lot.holding_id == h.id)).all()
        for lot in lots:
            session.delete(lot)
        session.delete(h)
    cfgs = session.exec(select(ConfigText).where(ConfigText.portfolio_id == portfolio_id)).all()
    for c in cfgs:
        session.delete(c)
    session.delete(pf)
    session.commit()
    return {"status": "deleted", "id": portfolio_id}
