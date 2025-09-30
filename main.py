from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infra.settings.base import Base
from src.infra.settings.connection import DbConnectionHandler

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://192.168.15.7:5173",
    "http://192.168.15.6:5173",
    "http://192.168.1.120:4173",
    "http://192.168.1.120:5173",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


engine = DbConnectionHandler().get_engine()

Base.metadata.create_all(bind=engine)
