from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo
from typing import Optional

from sqlmodel import Session, select

from arthasutra.db.models import QuoteLive


IST = ZoneInfo("Asia/Kolkata")


def is_market_session(now: Optional[dt.datetime] = None) -> bool:
    now = now or dt.datetime.now(IST)
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    if now.weekday() >= 5:  # Sat, Sun
        return False
    # Simple session window (09:15–15:30 IST); holidays are not accounted for here
    start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return start <= now <= end


def upsert_ltp(session: Session, security_id: int, ltp: float, source: str = "yf") -> None:
    row = session.exec(select(QuoteLive).where(QuoteLive.security_id == security_id)).first()
    now = dt.datetime.now(dt.UTC)
    if row:
        row.ltp = float(ltp)
        row.ts = now
        row.updated_at = now
    else:
        session.add(QuoteLive(security_id=security_id, ltp=float(ltp), ts=now, updated_at=now, source=source))


def get_fresh_ltp(session: Session, security_id: int, freshness_seconds: int = 120) -> Optional[float]:
    row = session.exec(select(QuoteLive).where(QuoteLive.security_id == security_id)).first()
    if not row:
        return None
    age = (dt.datetime.now(dt.UTC) - row.ts).total_seconds()
    if age <= freshness_seconds:
        return float(row.ltp)
    return None
