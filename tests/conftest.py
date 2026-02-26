import os
from pathlib import Path

import httpx
import pytest_asyncio
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from asgi_lifespan import LifespanManager
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command

# Ensure the test DB URL is used before any project imports.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_db",
)
os.environ["SQLALCHEMY_DATABASE_URI"] = TEST_DATABASE_URL

from src.infra.settings import config as settings_config
from src.infra.settings.connection import get_db_session

settings_config.get_settings.cache_clear()

from main import app as fastapi_app

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI_PATH = PROJECT_ROOT / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = PROJECT_ROOT / "alembic"


def _to_sync_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername == "postgresql+asyncpg":
        url = url.set(drivername="postgresql+psycopg2")
    return url.render_as_string(hide_password=False)


def _build_alembic_config(sync_database_url: str) -> Config:
    alembic_config = Config(str(ALEMBIC_INI_PATH))
    alembic_config.set_main_option("script_location", str(ALEMBIC_SCRIPT_LOCATION))
    alembic_config.set_main_option("sqlalchemy.url", sync_database_url)
    return alembic_config


def _has_existing_schema(sync_database_url: str) -> bool:
    engine = create_engine(sync_database_url, poolclass=NullPool, future=True)
    try:
        with engine.connect() as conn:
            table_names = inspect(conn).get_table_names()
            return any(table_name != "alembic_version" for table_name in table_names)
    finally:
        engine.dispose()


def _reset_public_schema(sync_database_url: str) -> None:
    engine = create_engine(sync_database_url, poolclass=NullPool, future=True)
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE")
            conn.exec_driver_sql("CREATE SCHEMA public")
    finally:
        engine.dispose()


def _ensure_test_db_migrations() -> None:
    sync_database_url = _to_sync_database_url(TEST_DATABASE_URL)
    alembic_config = _build_alembic_config(sync_database_url)
    script = ScriptDirectory.from_config(alembic_config)
    head_revisions = set(script.get_heads())

    engine = create_engine(sync_database_url, poolclass=NullPool, future=True)
    try:
        with engine.connect() as conn:
            migration_context = MigrationContext.configure(conn)
            current_revisions = set(migration_context.get_current_heads())
    finally:
        engine.dispose()

    if current_revisions == head_revisions and current_revisions:
        return

    # If there is pre-existing non-versioned schema, reset test schema first.
    if not current_revisions and _has_existing_schema(sync_database_url):
        _reset_public_schema(sync_database_url)

    command.upgrade(alembic_config, "head")


# ---- engine (session scope) ----
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    _ensure_test_db_migrations()

    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,  # isolates connections (good for tests)
        future=True,
    )

    yield engine

    await engine.dispose()


# ---- connection + outer transaction (per test) ----
@pytest_asyncio.fixture
async def db_connection(async_engine):
    async with async_engine.connect() as conn:
        tx = await conn.begin()
        try:
            yield conn
        finally:
            await tx.rollback()  # ✅ rolls back everything the test did


# ---- session + SAVEPOINT (per test) ----
@pytest_asyncio.fixture
async def db_session(db_connection):
    session = AsyncSession(bind=db_connection, expire_on_commit=False)

    # Start a SAVEPOINT so code that calls commit() inside the app doesn't break isolation
    await session.begin_nested()

    # When the nested transaction ends, reopen it (common SQLAlchemy test pattern)
    @event.listens_for(session.sync_session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        # If the SAVEPOINT ended, reopen it
        if trans.nested and not trans._parent.nested:  # SQLAlchemy internals, but widely used
            sess.begin_nested()

    try:
        yield session
    finally:
        await session.close()


# ---- FastAPI app (per test) ----
@pytest_asyncio.fixture
async def app(db_session):
    async def _override_get_db_session():
        yield db_session

    fastapi_app.dependency_overrides[get_db_session] = _override_get_db_session
    try:
        yield fastapi_app
    finally:
        fastapi_app.dependency_overrides.pop(get_db_session, None)


# ---- HTTP client (per test) ----
@pytest_asyncio.fixture
async def client(app):
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
