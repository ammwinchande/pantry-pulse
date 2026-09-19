"""
Database engine + session factory (persistence detail).

The datastore is selected entirely by ``DATABASE_URL``:

* ``sqlite:///pantrypulse.db``  — default, zero-config local development
* ``postgresql+psycopg://...``  — production (PostgreSQL)
* ``mysql+pymysql://...``       — production (MySQL)

Because the repositories only depend on the *ports* (``src.ports.driven``),
switching datastores is a one-line environment change — no application code
is touched. This keeps the hexagonal boundary intact: the domain and core
layers never import SQLAlchemy.
"""
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings
from src.adapters.outbound.persistence.orm_models import Base

# SQLite needs check_same_thread=False so FastAPI's threadpool can share it.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,  # recycles stale connections (helpful for long-lived servers)
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables if they do not already exist.

    Idempotent — safe to call on every boot. For schema *evolutions* in
    production, pair this with Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a database session, guaranteeing it is closed on exit."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
