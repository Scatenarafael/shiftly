from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infra.settings.config import get_settings

settings = get_settings()
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI


engine: AsyncEngine = create_async_engine(DATABASE_URL)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


class DbConnectionHandler:
    """Deprecated: use get_db_session() dependency instead."""

    def __init__(self) -> None:
        self.__engine = engine
        self.session: AsyncSession | None = None

    def get_engine(self) -> AsyncEngine:
        return self.__engine

    async def __aenter__(self):
        self.session = async_session_factory()  # type: ignore
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
