from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers import auth_router, company_router, link_user_to_company_router, role_router, user_company_requests_router, user_router, workday_router
from src.app.controllers.auth_config import AuthCookieSettings
from src.app.controllers.middlewares.auth_middleware import AuthMiddleware
from src.app.dependencies import (
    get_auth_cookie_settings,
    get_companies_repository,
    get_jwt_repository,
    get_refresh_token_expire_days,
    get_roles_repository,
    get_user_company_requests_repository,
    get_token_service,
    get_user_company_roles_repository,
    get_users_repository,
    get_workdays_repository,
)
from src.infra.db import models as _models  # noqa: F401
from src.infra.repositories.companies_repository import CompaniesRepository
from src.infra.repositories.jwt_repository import JWTRepository
from src.infra.repositories.roles_repository import RolesRepository
from src.infra.repositories.user_company_requests_repository import UserCompanyRequestsRepository
from src.infra.repositories.user_company_roles_repository import UserCompanyRolesRepository
from src.infra.repositories.users_repository import UsersRepository
from src.infra.repositories.workdays_repository import WorkdaysRepository
from src.infra.services.jwt_token_service import JWTTokenService
from src.infra.settings.config import get_settings
from src.infra.settings.connection import get_db_session
from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.ijwt_repository import IJWTRepository
from src.interfaces.iroles_repository import IRolesRepository
from src.interfaces.itoken_service import ITokenService
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.iworkdays_repository import IWorkdaysRepository

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

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

token_service = JWTTokenService()
public_paths = ["/auth/login", "/auth/refresh", "/auth/logout", "/users/register", "/docs", "/openapi.json", "/health"]
app.add_middleware(AuthMiddleware, token_service=token_service, access_cookie_name=settings.ACCESS_COOKIE_NAME, public_paths=public_paths)


def provide_users_repository(session: AsyncSession = Depends(get_db_session)) -> IUsersRepository:
    return UsersRepository(session)


def provide_companies_repository(session: AsyncSession = Depends(get_db_session)) -> ICompaniesRepository:
    return CompaniesRepository(session)


def provide_roles_repository(session: AsyncSession = Depends(get_db_session)) -> IRolesRepository:
    return RolesRepository(session)


def provide_user_company_roles_repository(session: AsyncSession = Depends(get_db_session)) -> IUserCompanyRolesRepository:
    return UserCompanyRolesRepository(session)


def provide_user_company_requests_repository(session: AsyncSession = Depends(get_db_session)) -> IUserCompanyRequestsRepository:
    return UserCompanyRequestsRepository(session)


def provide_workdays_repository(session: AsyncSession = Depends(get_db_session)) -> IWorkdaysRepository:
    return WorkdaysRepository(session)


def provide_jwt_repository(session: AsyncSession = Depends(get_db_session)) -> IJWTRepository:
    return JWTRepository(session)


def provide_token_service() -> ITokenService:
    return token_service


auth_cookie_settings = AuthCookieSettings(
    access_cookie_name=settings.ACCESS_COOKIE_NAME,
    refresh_cookie_name=settings.REFRESH_COOKIE_NAME,
    cookie_httponly=settings.COOKIE_HTTPONLY,
    cookie_secure=settings.COOKIE_SECURE,
    cookie_samesite=settings.COOKIE_SAMESITE,
    access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
)


def provide_refresh_token_expire_days() -> int:
    return settings.REFRESH_TOKEN_EXPIRE_DAYS


def provide_auth_cookie_settings() -> AuthCookieSettings:
    return auth_cookie_settings


app.dependency_overrides[get_users_repository] = provide_users_repository
app.dependency_overrides[get_companies_repository] = provide_companies_repository
app.dependency_overrides[get_roles_repository] = provide_roles_repository
app.dependency_overrides[get_user_company_roles_repository] = provide_user_company_roles_repository
app.dependency_overrides[get_user_company_requests_repository] = provide_user_company_requests_repository
app.dependency_overrides[get_workdays_repository] = provide_workdays_repository
app.dependency_overrides[get_jwt_repository] = provide_jwt_repository
app.dependency_overrides[get_token_service] = provide_token_service
app.dependency_overrides[get_refresh_token_expire_days] = provide_refresh_token_expire_days
app.dependency_overrides[get_auth_cookie_settings] = provide_auth_cookie_settings


app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(company_router.router)
app.include_router(role_router.router)
app.include_router(link_user_to_company_router.router)
app.include_router(user_company_requests_router.router)
app.include_router(workday_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
