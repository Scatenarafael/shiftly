from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData

from src.account.app.controllers import auth_router, user_router
from src.account.app.controllers.middlewares.auth_middleware import AuthMiddleware

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://192.168.15.7:5173",
    "http://192.168.15.6:5173",
    "http://192.168.1.120:4173",
    "http://192.168.1.120:5173",
]

metadata = MetaData()


# class DbConnectionHandler:
#     def get_engine(self) -> AsyncEngine:
#         DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_db"
#         return create_async_engine(DATABASE_URL)


# async def create_tables():
#     engine = DbConnectionHandler().get_engine()
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# # Lifespan event handler
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup logic
#     await create_tables()
#     yield


# app = FastAPI(lifespan=lifespan)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)


app.include_router(auth_router.router)
app.include_router(user_router.router)
