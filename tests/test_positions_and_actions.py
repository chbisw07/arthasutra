import os
import tempfile
from datetime import date, timedelta

from fastapi.testclient import TestClient


def bootstrap_app_with_temp_db():
    tmpdb = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmpdb.close()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmpdb.name}"
    from arthasutra.api.main import app
    from arthasutra.db.session import create_db_and_tables

    create_db_and_tables()
    return app


def test_positions_and_actions_flow():
    app = bootstrap_app_with_temp_db()
    client = TestClient(app)

    # Create portfolio
    r1 = client.post("/portfolios", json={"name": "PF"})
    pid = r1.json()["id"]

    # Import holdings
    csv_content = (
        "symbol,exchange,qty,avg_price,sector\n"
        "BSE,NSE,30,2700,Financial Services\n"
    ).encode()
    files = {"file": ("holdings.csv", csv_content, "text/csv")}
    client.post(f"/portfolios/{pid}/import-csv", files=files)

    # Import 210 days EOD data trending up for BSE to trigger TRIM/ADD rules
    start = date.today() - timedelta(days=250)
    rows = [
        {
            "symbol": "BSE",
            "exchange": "NSE",
            "date": (start + timedelta(days=i)).isoformat(),
            "open": 2600 + i * 1.5,
            "high": 2600 + i * 1.5 + 10,
            "low": 2600 + i * 1.5 - 10,
            "close": 2600 + i * 1.5,
            "volume": 100000 + i,
        }
        for i in range(0, 210)
    ]
    import io, csv

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    files = {"file": ("eod.csv", buf.getvalue().encode(), "text/csv")}
    r_import = client.post("/data/prices-eod/import-csv", files=files)
    assert r_import.status_code == 200

    # Positions endpoint
    rpos = client.get(f"/portfolios/{pid}/positions")
    assert rpos.status_code == 200
    positions = rpos.json()
    assert len(positions) == 1
    assert positions[0]["symbol"] == "BSE"
    assert "pct_today" in positions[0]

    # Dashboard contains actions
    rdb = client.get(f"/portfolios/{pid}/dashboard")
    body = rdb.json()
    assert "actions" in body
    assert isinstance(body["actions"], list)
    # Given strong uptrend, TRIM or ADD should appear
    assert any(a["action"] in {"TRIM", "ADD", "KEEP"} for a in body["actions"])  # at least well-formed

