from __future__ import annotations

from datetime import date
from typing import Iterable, Dict, Tuple

import yfinance as yf
from sqlmodel import Session, select

from arthasutra.db.models import Security, PriceEOD
from arthasutra.services.live import upsert_ltp


def yahoo_symbol(symbol: str, exchange: str) -> str:
    ex = (exchange or "NSE").upper()
    if ex == "NSE":
        return f"{symbol}.NS"
    if ex == "BSE":
        return f"{symbol}.BO"
    return symbol


def fetch_eod_to_db(session: Session, symbol: str, exchange: str, start: date, end: date) -> int:
    ys = yahoo_symbol(symbol, exchange)
    ticker = yf.Ticker(ys)
    hist = ticker.history(start=start, end=end, auto_adjust=False)
    if hist is None or hist.empty:
        return 0

    sec = session.exec(select(Security).where(Security.symbol == symbol, Security.exchange == exchange)).first()
    if not sec:
        sec = Security(symbol=symbol, exchange=exchange, name=symbol)
        session.add(sec)
        session.flush()

    rows = 0
    for idx, row in hist.iterrows():
        d = idx.date()
        exists = session.exec(select(PriceEOD).where(PriceEOD.security_id == sec.id, PriceEOD.date == d)).first()
        if exists:
            continue
        pe = PriceEOD(
            security_id=sec.id,
            date=d,
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=float(row["Volume"]) if not (row["Volume"] is None) else None,
        )
        session.add(pe)
        rows += 1
    session.commit()
    return rows


def fetch_ltp_batch(session: Session, pairs: Iterable[Tuple[str, str]]) -> Dict[Tuple[str, str], float]:
    # pairs: list of (symbol, exchange)
    mapping = {}
    # Batch via yfinance.download for efficiency
    tickers = []
    rev: Dict[str, Tuple[str, str]] = {}
    for sym, ex in pairs:
        ys = yahoo_symbol(sym, ex)
        tickers.append(ys)
        rev[ys] = (sym, ex)
    if not tickers:
        return mapping
    import yfinance as yf

    try:
        df = yf.download(tickers=tickers, period="1d", interval="1m", progress=False, group_by='ticker', threads=True)
    except Exception:
        return mapping

    # df can be a MultiIndex DataFrame; pick last close for each ticker
    for ys, pair in rev.items():
        try:
            sub = df[ys] if isinstance(df.columns, pd.MultiIndex) else df
            last_row = sub.dropna().tail(1)
            if last_row is not None and not last_row.empty:
                price = float(last_row['Close'].iloc[0])
                mapping[pair] = price
        except Exception:
            continue
    return mapping
