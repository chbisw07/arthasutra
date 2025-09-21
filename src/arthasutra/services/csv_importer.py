from __future__ import annotations

import csv
from dataclasses import dataclass
from io import TextIOBase, StringIO, BytesIO
from typing import Iterable, List


@dataclass
class CSVRow:
    symbol: str
    exchange: str
    qty: float
    avg_price: float
    sector: str | None = None


def _parse_exchange_symbol(value: str) -> tuple[str, str]:
    # Accept formats: "NSE:INFY" or separate columns
    if ":" in value:
        ex, sym = value.split(":", 1)
        return ex.strip(), sym.strip()
    return "", value.strip()


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

    reader = csv.DictReader(stream)
    rows: list[CSVRow] = []
    for row in reader:
        symbol_field = (row.get("symbol") or row.get("Symbol") or "").strip()
        exchange_field = (row.get("exchange") or row.get("Exchange") or "").strip()
        qty_field = (row.get("qty") or row.get("quantity") or row.get("Quantity") or "0").strip()
        avg_field = (row.get("avg_price") or row.get("avgPrice") or row.get("average_price") or "0").strip()
        sector_field = (row.get("sector") or row.get("Sector") or None)

        if not symbol_field:
            continue
        if not exchange_field:
            exchange_field, symbol_field = _parse_exchange_symbol(symbol_field)

        rows.append(
            CSVRow(
                symbol=symbol_field,
                exchange=exchange_field or "NSE",
                qty=float(qty_field or 0),
                avg_price=float(avg_field or 0),
                sector=sector_field.strip() if isinstance(sector_field, str) else None,
            )
        )
    return rows

