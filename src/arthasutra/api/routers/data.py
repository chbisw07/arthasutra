from __future__ import annotations

import csv
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query
from sqlmodel import Session, select

from arthasutra.db.models import Security, PriceEOD, QuoteLive
from arthasutra.db.session import get_session
from arthasutra.services.marketdata.yfinance_client import fetch_eod_to_db
from arthasutra.services.kite_client import maybe_start_kite_ws


router = APIRouter()


@router.post("/prices-eod/import-csv")
def import_prices_eod(file: UploadFile, session: Session = Depends(get_session)) -> dict:
    content = file.file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    count = 0
    for row in reader:
        symbol = (row.get("symbol") or row.get("Symbol") or "").strip()
        exchange = (row.get("exchange") or row.get("Exchange") or "NSE").strip()
        date_s = (row.get("date") or row.get("Date") or "").strip()
        if not symbol or not date_s:
            continue
        sec = session.exec(select(Security).where(Security.symbol == symbol, Security.exchange == exchange)).first()
        if not sec:
            sec = Security(symbol=symbol, exchange=exchange, name=symbol)
            session.add(sec)
            session.flush()
        dt = datetime.fromisoformat(date_s)
        o = float(row.get("open") or row.get("Open") or 0)
        h = float(row.get("high") or row.get("High") or 0)
        l = float(row.get("low") or row.get("Low") or 0)
        c = float(row.get("close") or row.get("Close") or 0)
        v = row.get("volume") or row.get("Volume")
        pe = PriceEOD(security_id=sec.id, date=dt.date(), open=o, high=h, low=l, close=c, volume=float(v) if v else None)
        session.add(pe)
        count += 1
    session.commit()
    return {"status": "ok", "rows": count}


@router.post("/prices-eod/yf")
def import_prices_yfinance(
    symbols: str = Query(..., description="Comma-separated list, e.g., NSE:HDFCBANK,BSE:BSE"),
    start: str = Query(..., description="YYYY-MM-DD"),
    end: str = Query(..., description="YYYY-MM-DD"),
    session: Session = Depends(get_session),
) -> dict:
    from datetime import date

    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)
    total = 0
    for token in symbols.split(","):
        token = token.strip()
        if ":" in token:
            ex, sym = token.split(":", 1)
        else:
            ex, sym = "NSE", token
        total += fetch_eod_to_db(session, sym, ex, start_d, end_d)
    return {"status": "ok", "rows": total}


@router.get("/quotes")
def get_quotes(symbols: str = Query(..., description="Comma-separated list, e.g., NSE:HDFCBANK,BSE:BSE"), session: Session = Depends(get_session)) -> dict:
    out = {}
    for token in symbols.split(","):
        token = token.strip()
        if ":" in token:
            ex, sym = token.split(":", 1)
        else:
            ex, sym = "NSE", token
        sec = session.exec(select(Security).where(Security.symbol == sym, Security.exchange == ex)).first()
        if not sec:
            out[token] = None
            continue
        q = session.exec(select(QuoteLive).where(QuoteLive.security_id == sec.id)).first()
        out[token] = {"ltp": q.ltp, "ts": q.ts.isoformat()} if q else None
    return {"quotes": out}


@router.post("/kite/tokens")
def set_kite_tokens(payload: dict[str, int], session: Session = Depends(get_session)) -> dict:
    # payload: { "NSE:HDFCBANK": 12345, ... }
    updated = 0
    for key, token in payload.items():
        if ":" in key:
            ex, sym = key.split(":", 1)
        else:
            ex, sym = "NSE", key
        sec = session.exec(select(Security).where(Security.symbol == sym, Security.exchange == ex)).first()
        if sec:
            sec.kite_token = int(token)
            updated += 1
    session.commit()
    # Optionally restart/ensure WS subscription
    try:
        maybe_start_kite_ws(session)
    except Exception:
        pass
    return {"status": "ok", "updated": updated}
