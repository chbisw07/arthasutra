from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlmodel import SQLModel, Field


class Portfolio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    base_ccy: str = Field(default="INR")
    tz: str = Field(default="Asia/Kolkata")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Security(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    exchange: str = Field(index=True)
    name: Optional[str] = None
    sector: Optional[str] = Field(default=None, index=True)
    lot_size: Optional[int] = None
    tick_size: Optional[float] = None


class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(index=True, foreign_key="portfolio.id")
    security_id: int = Field(index=True, foreign_key="security.id")
    qty_total: float = 0.0
    avg_price: float = 0.0


class Lot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    holding_id: int = Field(index=True, foreign_key="holding.id")
    qty: float
    price: float
    date: datetime = Field(default_factory=datetime.utcnow)
    account: Optional[str] = None
    tax_status: Optional[str] = None


class PriceEOD(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    security_id: int = Field(index=True, foreign_key="security.id")
    date: date = Field(index=True)
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


class ConfigText(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(index=True, foreign_key="portfolio.id")
    yaml_text: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

