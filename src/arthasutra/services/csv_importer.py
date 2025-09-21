from __future__ import annotations

import csv
from dataclasses import dataclass
from io import TextIOBase, StringIO, BytesIO
from typing import Iterable, List, Optional


@dataclass
class CSVRow:
    symbol: str
    exchange: str
    qty: float
    avg_price: float
    sector: str | None = None
    name: str | None = None
    ltp: float | None = None


def _parse_exchange_symbol(value: str) -> tuple[str, str]:
    # Accept formats: "NSE:INFY" or separate columns
    if ":" in value:
        ex, sym = value.split(":", 1)
        return ex.strip(), sym.strip()
    return "", value.strip()


def _num(value: str | None) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    # Remove commas and percentage signs; handle negatives in parentheses
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    s = s.replace(",", "").replace("%", "")
    try:
        f = float(s)
        return -f if neg else f
    except ValueError:
        return None


def parse_positions_csv(file: BytesIO | TextIOBase) -> List[CSVRow]:
    # Normalize to text reader
    if isinstance(file, BytesIO):
        text = file.getvalue().decode("utf-8")
        stream: TextIOBase = StringIO(text)
    elif hasattr(file, "read"):
        content = file.read()
        if isinstance(content, bytes):
            stream = StringIO(content.decode("utf-8"))
        else:
            stream = StringIO(content)
    else:
        raise ValueError("Unsupported file object")

    reader = csv.DictReader(stream, skipinitialspace=True)
    rows: list[CSVRow] = []
    for row in reader:
        # Header aliases
        symbol_field = (
            row.get("symbol")
            or row.get("Symbol")
            or row.get("Ticker")
            or row.get("Instrument")
            or row.get("instrument")
            or ""
        ).strip()
        name_field = (row.get("name") or row.get("Name") or None)
        exchange_field = (row.get("exchange") or row.get("Exchange") or "").strip()
        qty_field = (
            row.get("qty")
            or row.get("Qty.")
            or row.get("quantity")
            or row.get("Quantity")
            or row.get("Shares")
            or row.get("shares")
            or "0"
        )
        avg_field = (
            row.get("avg_price")
            or row.get("Avg. cost")
            or row.get("Avg Buy Price (Rs.)")
            or row.get("avgPrice")
            or row.get("average_price")
            or "0"
        )
        ltp_field = row.get("LTP") or row.get("Current Price (Rs.)") or row.get("ltp")
        sector_field = (row.get("sector") or row.get("Sector") or None)

        if not symbol_field:
            continue
        if not exchange_field:
            exchange_field, symbol_field = _parse_exchange_symbol(symbol_field)

        qty_val = _num(qty_field) or 0.0
        avg_val = _num(avg_field) or 0.0
        ltp_val = _num(ltp_field)

        rows.append(
            CSVRow(
                symbol=symbol_field,
                exchange=exchange_field or "NSE",
                qty=qty_val,
                avg_price=avg_val,
                sector=sector_field.strip() if isinstance(sector_field, str) else None,
                name=name_field.strip() if isinstance(name_field, str) else None,
                ltp=ltp_val,
            )
        )
    return rows
