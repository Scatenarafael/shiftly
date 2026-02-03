import asyncio
import os

import httpx
import pytest
from asgi_lifespan import LifespanManager
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

# Ensure the test DB URL is used before any project imports.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_test",
)
os.environ["SQLALCHEMY_DATABASE_URI"] = TEST_DATABASE_URL

from src.infra.settings import config as settings_config

settings_config.get_settings.cache_clear()

from main import app as fastapi_app

# Import entities so metadata is fully populated for create_all.
from src.domain.entities import (  # noqa: F401
    company,
    refresh_token,
    role,
    user,
    user_company_role,
    work_day,
    work_shift,
)
from src.infra.settings.base import Base


# ---- event loop (pytest-asyncio) ----
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ---- engine (session scope) ----
@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,  # isolates connections (good for tests)
        future=True,
    )

    # Create schema once per test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop schema after all tests (optional but tidy)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ---- connection + outer transaction (per test) ----
@pytest.fixture
async def db_connection(async_engine):
    async with async_engine.connect() as conn:
        tx = await conn.begin()
        try:
            yield conn
        finally:
            await tx.rollback()  # ✅ rolls back everything the test did


# ---- session + SAVEPOINT (per test) ----
@pytest.fixture
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
@pytest.fixture
async def app():
    return fastapi_app


# ---- HTTP client (per test) ----
@pytest.fixture
async def client(app):
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
