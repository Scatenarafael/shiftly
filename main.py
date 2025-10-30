from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData

from src.app.controllers import auth_router, company_router, link_user_to_company_router, role_router, user_router
from src.app.controllers.middlewares.auth_middleware import AuthMiddleware

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://192.168.15.7:5173",
    "http://192.168.15.6:5173",
    "http://192.168.1.120:4173",
    "http://192.168.1.120:5173",
]

metadata = MetaData()

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
app.include_router(company_router.router)
app.include_router(role_router.router)
app.include_router(link_user_to_company_router.router)
