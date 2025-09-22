from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text


load_dotenv()


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///arthasutra.db")


def _engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(get_database_url(), **_engine_kwargs(get_database_url()))


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _run_light_migrations()


def _run_light_migrations() -> None:
    # Lightweight migrations for SQLite during dev: add columns if missing
    url = get_database_url()
    if not url.startswith("sqlite"):
        return
    with engine.connect() as conn:
        # security.kite_token
        info = conn.execute(text("PRAGMA table_info('security')")).fetchall()
        col_names = {row[1] for row in info}
        if "kite_token" not in col_names:
            conn.execute(text("ALTER TABLE security ADD COLUMN kite_token INTEGER"))
            conn.commit()


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


@contextmanager
def session_scope() -> Iterator[Session]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
