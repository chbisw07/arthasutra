from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlmodel import Session, select

from arthasutra.db.models import Holding, Security, PriceEOD


@dataclass
class Action:
    action: str  # KEEP | ADD | TRIM | EXIT
    symbol: str
    reason: str
    qty: Optional[float] = None
    score: Optional[int] = None


def _sma(values: list[float], window: int) -> Optional[float]:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def _get_closes(session: Session, security_id: int, limit: int = 220) -> list[float]:
    rows = session.exec(
        select(PriceEOD).where(PriceEOD.security_id == security_id).order_by(PriceEOD.date.asc())
    ).all()
    closes = [float(r.close) for r in rows][-limit:]
    return closes


def propose_actions(session: Session, portfolio_id: int) -> list[dict]:
    holdings = session.exec(select(Holding).where(Holding.portfolio_id == portfolio_id)).all()
    actions: list[dict] = []
    for h in holdings:
        sec: Security | None = session.get(Security, h.security_id)
        if not sec:
            continue
        closes = _get_closes(session, sec.id)
        if not closes:
            actions.append({
                "action": "KEEP",
                "symbol": f"{sec.exchange}:{sec.symbol}",
                "reason": "no_price_history",
                "qty": None,
                "score": 50,
            })
            continue
        last = closes[-1]
        sma50 = _sma(closes, 50)
        sma200 = _sma(closes, 200)
        score = 50
        if sma50:
            score += 10 if last > sma50 else -10
        if sma200:
            score += 10 if last > sma200 else -10

        # Rules v1 (simple):
        # - EXIT if below 200SMA and score low
        # - TRIM if extended vs 50SMA by 8%
        # - ADD if above 50SMA and score high
        if sma200 and last < sma200 and score < 50:
            actions.append({
                "action": "EXIT",
                "symbol": f"{sec.exchange}:{sec.symbol}",
                "reason": "below_200sma",
                "qty": h.qty_total,
                "score": max(score, 0),
            })
            continue

        if sma50 and last > 1.08 * sma50:
            actions.append({
                "action": "TRIM",
                "symbol": f"{sec.exchange}:{sec.symbol}",
                "reason": "extended_vs_50sma",
                "qty": round(h.qty_total * 0.1, 4),
                "score": min(score + 5, 100),
            })
            continue

        if sma50 and last >= sma50 and score >= 60:
            actions.append({
                "action": "ADD",
                "symbol": f"{sec.exchange}:{sec.symbol}",
                "reason": "trend_ok_above_50sma",
                "qty": round(h.qty_total * 0.1, 4),
                "score": min(score + 5, 100),
            })
            continue

        actions.append({
            "action": "KEEP",
            "symbol": f"{sec.exchange}:{sec.symbol}",
            "reason": "default",
            "qty": None,
            "score": score,
        })

    return actions

