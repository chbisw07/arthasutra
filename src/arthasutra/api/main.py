from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arthasutra.db.session import create_db_and_tables
from arthasutra.api.routers.portfolios import router as portfolios_router


def _get_cors_origins() -> list[str]:
    import os

    origins = os.getenv("CORS_ORIGINS", "").split(",")
    return [o.strip() for o in origins if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (no-op for now)


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
