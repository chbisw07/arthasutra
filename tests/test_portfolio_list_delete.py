import os
import tempfile

from fastapi.testclient import TestClient


def bootstrap_app_with_temp_db():
    tmpdb = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmpdb.close()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmpdb.name}"
    from arthasutra.api.main import app
    from arthasutra.db.session import create_db_and_tables

    create_db_and_tables()
    return app


def test_portfolio_list_and_delete():
    app = bootstrap_app_with_temp_db()
    client = TestClient(app)

    # Create two portfolios
    r1 = client.post("/portfolios", json={"name": "PF1"})
    r2 = client.post("/portfolios", json={"name": "PF2"})
    assert r1.status_code == 200 and r2.status_code == 200

    # List
    rl = client.get("/portfolios")
    assert rl.status_code == 200
    lst = rl.json()
    assert len(lst) == 2

    # Delete one
    pid = lst[0]["id"]
    rd = client.delete(f"/portfolios/{pid}")
    assert rd.status_code == 200

    # List again
    rl2 = client.get("/portfolios")
    assert rl2.status_code == 200
    assert len(rl2.json()) == 1

