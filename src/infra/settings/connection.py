from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infra.settings.config import get_settings

settings = get_settings()
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

print("DATABASE_URL - in connection", DATABASE_URL)


class DbConnectionHandler:
    # Constructor to initialize the database connection
    def __init__(self) -> None:
        self.__connection_string = DATABASE_URL
        self.__engine = self.__create_database_engine()
        self.session: AsyncSession | None = None

    # Method to create the database engine
    def __create_database_engine(self) -> AsyncEngine:
        engine = create_async_engine(self.__connection_string)
        return engine

    def get_engine(self) -> AsyncEngine:
        return self.__engine

    async def __aenter__(self):
        # Create an async session factory
        async_session_factory = sessionmaker(self.__engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
        self.session = async_session_factory()  # type: ignore
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
