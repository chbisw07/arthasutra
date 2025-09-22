from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arthasutra.db.session import create_db_and_tables
from arthasutra.api.routers.portfolios import router as portfolios_router
from arthasutra.api.routers.data import router as data_router
from arthasutra.db.session import session_scope
from arthasutra.db.models import Security, Holding
from arthasutra.services.marketdata.yfinance_client import fetch_ltp_batch
from arthasutra.services.live import upsert_ltp


def _get_cors_origins() -> list[str]:
    import os

    origins = os.getenv("CORS_ORIGINS", "").split(",")
    return [o.strip() for o in origins if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    # Start background polling for live quotes using yfinance (optional)
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler(daemon=True)

        def poll_live_quotes():
            with session_scope() as s:
                # unique (symbol, exchange) from current holdings
                rows = s.exec(
                    """
                    SELECT DISTINCT se.symbol, se.exchange, se.id
                    FROM holding h
                    JOIN security se ON se.id = h.security_id
                    """
                ).all()
                pairs = [(r[0], r[1]) for r in rows]
                mapping = fetch_ltp_batch(s, pairs)
                # upsert
                for (sym, ex), ltp in mapping.items():
                    se = s.exec(
                        "SELECT id FROM security WHERE symbol = :sym AND exchange = :ex",
                        {"sym": sym, "ex": ex},
                    ).first()
                    if se:
                        upsert_ltp(s, se[0], ltp, source="yf")

        import os

        interval = int(os.getenv("LIVE_POLL_SECONDS", "60"))
        scheduler.add_job(poll_live_quotes, "interval", seconds=interval, id="yf_live_poll", replace_existing=True)
        scheduler.start()
        app.state._scheduler = scheduler
    except Exception:
        # If APScheduler not available or errors out, continue without live polling
        pass
    yield
    # Shutdown
    sched = getattr(app.state, "_scheduler", None)
    if sched:
        try:
            sched.shutdown(wait=False)
        except Exception:
            pass


app = FastAPI(title="ArthaSutra API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins() or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


app.include_router(portfolios_router, prefix="/portfolios", tags=["portfolios"])
app.include_router(data_router, prefix="/data", tags=["data"])
