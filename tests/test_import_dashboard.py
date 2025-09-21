import os
import tempfile
from io import BytesIO

from fastapi.testclient import TestClient
from sqlmodel import Session, select


def test_import_and_dashboard_flow():
    # Configure temp DB before importing the app
    tmpdb = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmpdb.close()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmpdb.name}"

    from arthasutra.api.main import app  # import after env var set
    from arthasutra.db.session import engine, create_db_and_tables
    from arthasutra.db.models import Security, PriceEOD

    create_db_and_tables()

    client = TestClient(app)

    # 1) Create portfolio
    resp = client.post("/portfolios", json={"name": "Test PF"})
    assert resp.status_code == 200
    pf = resp.json()
    pid = pf["id"]

    # 2) Import CSV holdings
    csv_content = (
        "symbol,exchange,qty,avg_price,sector\n"
        "BSE,NSE,30,2700,Financial Services\n"
        "HDFCBANK,NSE,120,1520,Banks\n"
    ).encode()
    files = {"file": ("holdings.csv", BytesIO(csv_content), "text/csv")}
    r2 = client.post(f"/portfolios/{pid}/import-csv", files=files)
    assert r2.status_code == 200
    assert r2.json()["rows"] == 2

    # 3) Seed one EOD price for BSE to test PnL
    with Session(engine) as s:
        bse: Security | None = s.exec(select(Security).where(Security.symbol == "BSE", Security.exchange == "NSE")).first()
        assert bse is not None
        s.add(PriceEOD(security_id=bse.id, date=__import__("datetime").date.today(), open=2700, high=2920, low=2680, close=2845))
        s.commit()

    # 4) Dashboard
    r3 = client.get(f"/portfolios/{pid}/dashboard")
    assert r3.status_code == 200
    body = r3.json()
    assert body["portfolio_id"] == pid
    assert isinstance(body["equity_value"], (int, float))
    assert isinstance(body["pnl_inr"], (int, float))
    assert len(body["positions"]) == 2
    assert body["actions"] == []
