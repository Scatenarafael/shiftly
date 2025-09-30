from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.infra.settings.config import get_settings

settings = get_settings()

# DATABASE_URL = "sqlite:///./fuel_quali_db.db"
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

print("DATABASE_URL - in connection", DATABASE_URL)


class DbConnectionHandler:
    # constructor to initialize the database connection
    def __init__(self) -> None:
        self.__connection_string = DATABASE_URL
        self.__engine = self.__create_database_engine()
        self.session: Session | None = None

    # method to create the database engine
    def __create_database_engine(self) -> Engine:
        engine = create_engine(self.__connection_string, echo=True, pool_pre_ping=True, pool_size=5, max_overflow=10)
        return engine

    def get_engine(self) -> Engine:
        return self.__engine

    def __enter__(self):
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
