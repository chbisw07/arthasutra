from __future__ import annotations

import os
import threading
from typing import Iterable, Optional

from sqlmodel import Session, select
from arthasutra.db.session import session_scope

try:
    from kiteconnect import KiteTicker
except Exception:  # pragma: no cover - optional dependency
    KiteTicker = None  # type: ignore

from arthasutra.db.models import Security
from arthasutra.services.live import upsert_ltp


class KiteWSManager:
    def __init__(self, api_key: str, access_token: str, session: Session) -> None:
        if KiteTicker is None:
            raise RuntimeError("kiteconnect not installed")
        self.api_key = api_key
        self.access_token = access_token
        self._kt = KiteTicker(self.api_key, self.access_token)
        self._thread: Optional[threading.Thread] = None
        self._session = session

        self._kt.on_ticks = self._on_ticks
        self._kt.on_connect = self._on_connect
        self._kt.on_error = self._on_error
        self._sub_tokens: list[int] = []

    def _on_connect(self, ws, response):  # noqa: ANN001
        if self._sub_tokens:
            ws.subscribe(self._sub_tokens)
            ws.set_mode(ws.MODE_LTP, self._sub_tokens)

    def _on_error(self, ws, code, reason):  # noqa: ANN001
        # For now, let errors be logged by kiteconnect; we could add loguru if needed
        pass

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
        self._thread = threading.Thread(target=self._kt.connect, kwargs={"threaded": True}, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        try:
            self._kt.close()
        except Exception:
            pass


def maybe_start_kite_ws(session: Session):
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")
    if not api_key or not access_token or KiteTicker is None:
        return None
    mgr = KiteWSManager(api_key, access_token, session)
    mgr.subscribe_portfolio_tokens()
    mgr.start()
    return mgr
