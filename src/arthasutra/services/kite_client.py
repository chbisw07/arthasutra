from __future__ import annotations

import os
import threading
from typing import Iterable, Optional, Dict, Tuple

from sqlmodel import Session, select
from arthasutra.db.session import session_scope

try:
    from kiteconnect import KiteTicker, KiteConnect
except Exception:  # pragma: no cover - optional dependency
    KiteTicker = None  # type: ignore
    KiteConnect = None  # type: ignore

from arthasutra.db.models import Security
from arthasutra.services.live import upsert_ltp


class KiteWSManager:
    def __init__(self, api_key: str, access_token: str, session: Session) -> None:
        if KiteTicker is None:
            raise RuntimeError("kiteconnect not installed")
        self.api_key = api_key
        self.access_token = access_token
        # Support both legacy (api_key, access_token) and enctoken-based constructors
        user_id = os.getenv("KITE_USER_ID")
        try:
            # Older signature: (api_key, access_token)
            self._kt = KiteTicker(self.api_key, self.access_token)
        except TypeError:
            # Newer signature may accept enctoken + optional user_id
            try:
                if user_id:
                    self._kt = KiteTicker(enctoken=self.access_token, user_id=user_id)
                else:
                    self._kt = KiteTicker(enctoken=self.access_token)
            except Exception:
                # Fallback to raising a clear error
                raise RuntimeError("Failed to initialize KiteTicker. Check token type (PUBLIC/ACCESS) and library version.")
        self._thread: Optional[threading.Thread] = None
        self._session = session

        self._kt.on_ticks = self._on_ticks
        self._kt.on_connect = self._on_connect
        self._kt.on_error = self._on_error
        self._sub_tokens: list[int] = []

    def _on_connect(self, ws, response):  # noqa: ANN001
        self._connected = True
        if self._sub_tokens:
            ws.subscribe(self._sub_tokens)
            ws.set_mode(ws.MODE_LTP, self._sub_tokens)

    def _on_error(self, ws, code, reason):  # noqa: ANN001
        # For now, let errors be logged by kiteconnect; we could add loguru if needed
        self._connected = False

    def _on_ticks(self, ws, ticks):  # noqa: ANN001
        # ticks: list of dicts with instrument_token and last_price
        with session_scope() as s:
            tok_to_sec = {srow.kite_token: srow.id for srow in s.exec(select(Security).where(Security.kite_token.is_not(None))).all()}
            for t in ticks:
                token = t.get("instrument_token")
                ltp = t.get("last_price") or t.get("last_traded_price")
                sid = tok_to_sec.get(token)
                if sid and ltp:
                    upsert_ltp(s, sid, float(ltp), source="kite")

    def subscribe_portfolio_tokens(self) -> None:
        with session_scope() as s:
            tokens = [row.kite_token for row in s.exec(select(Security).where(Security.kite_token.is_not(None))).all() if row.kite_token]
        self._sub_tokens = list({int(t) for t in tokens})
        if self._kt and self._sub_tokens:
            self._kt.subscribe(self._sub_tokens)
            self._kt.set_mode(self._kt.MODE_LTP, self._sub_tokens)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._connected = False
        self._thread = threading.Thread(target=self._kt.connect, kwargs={"threaded": True}, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        try:
            self._kt.close()
        except Exception:
            pass

    def status(self) -> Dict[str, object]:
        return {
            "connected": getattr(self, "_connected", False),
            "subscribed_count": len(self._sub_tokens or []),
            "provider": "kite",
        }


def maybe_start_kite_ws(session: Session):
    api_key = os.getenv("KITE_API_KEY")
    # Prefer PUBLIC_TOKEN if provided; else ACCESS_TOKEN
    access_token = os.getenv("KITE_PUBLIC_TOKEN") or os.getenv("KITE_ACCESS_TOKEN")
    if not api_key or not access_token or KiteTicker is None:
        return None
    mgr = KiteWSManager(api_key, access_token, session)
    mgr.subscribe_portfolio_tokens()
    mgr.start()
    return mgr


def get_kite_client() -> Optional[KiteConnect]:
    if KiteConnect is None:
        return None
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")
    if not api_key or not access_token:
        return None
    kc = KiteConnect(api_key=api_key)
    kc.set_access_token(access_token)
    return kc


def bulk_map_tokens(session: Session, exchanges: Iterable[str]) -> Dict[str, int]:
    """Fetch instruments for given exchanges and map Security.kite_token by tradingsymbol.

    Returns summary dict with counts: {updated, skipped, unmatched}
    """
    kc = get_kite_client()
    if kc is None:
        return {"updated": 0, "skipped": 0, "unmatched": 0}
    updated = 0
    skipped = 0
    unmatched = 0
    # Build lookup of our securities by (exchange, symbol)
    secs = {(s.exchange.upper(), s.symbol.upper()): s for s in session.exec(select(Security)).all()}
    for ex in exchanges:
        try:
            instruments = kc.instruments(ex.upper())
        except Exception:
            continue
        for inst in instruments:
            exu = inst.get("exchange", "").upper()
            tsym = str(inst.get("tradingsymbol", "")).upper()
            token = inst.get("instrument_token")
            lot = inst.get("lot_size")
            tick = inst.get("tick_size")
            key = (exu, tsym)
            sec = secs.get(key)
            if not sec:
                unmatched += 1
                continue
            if sec.kite_token == token:
                skipped += 1
                continue
            sec.kite_token = token
            if lot is not None:
                sec.lot_size = lot
            if tick is not None:
                try:
                    sec.tick_size = float(tick)
                except Exception:
                    pass
            updated += 1
    session.commit()
    return {"updated": updated, "skipped": skipped, "unmatched": unmatched}


def fetch_snapshot_ltp(session: Session, symbols: Iterable[Tuple[str, str]]) -> Dict[Tuple[str, str], float]:
    """Fetch one-shot LTP snapshot from Kite for symbols [(symbol, exchange)]."""
    kc = get_kite_client()
    if kc is None:
        return {}
    ins = [f"{ex}:{sym}" for sym, ex in symbols]
    if not ins:
        return {}
    mapping: Dict[Tuple[str, str], float] = {}
    try:
        data = kc.ltp(ins)
    except Exception:
        return mapping
    for key, val in data.items():
        try:
            ex, sym = key.split(":", 1)
            ltp = float(val.get("last_price") or val.get("last_traded_price") or 0)
            if ltp:
                mapping[(sym, ex)] = ltp
        except Exception:
            continue
    # Upsert to quotes_live
    for (sym, ex), price in mapping.items():
        sec = session.exec(select(Security).where(Security.symbol == sym, Security.exchange == ex)).first()
        if sec:
            upsert_ltp(session, sec.id, price, source="kite")
    session.commit()
    return mapping
