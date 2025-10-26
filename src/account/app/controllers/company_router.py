from typing import Awaitable, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.account.app.repositories.companies_repository import CompaniesRepository
from src.account.app.repositories.jwt_repository import JWTRepository
from src.account.app.repositories.users_repository import UsersRepository
from src.account.domain.entities.user import User
from src.account.usecases.auth_service import AuthService
from src.account.usecases.companies.create_company_usecase import CreateCompanyUseCase
from src.account.usecases.companies.list_companies_usecase import ListCompaniesUseCase
from src.infra.settings.config import get_settings
from src.infra.settings.logging_config import app_logger

router = APIRouter(tags=["companies"], prefix="/companies")

settings = get_settings()


def get_create_company_usecase():
    return CreateCompanyUseCase(CompaniesRepository())


def get_list_company_usecase():
    return ListCompaniesUseCase(CompaniesRepository())


def get_auth_service() -> AuthService:
    return AuthService(UsersRepository(), JWTRepository())


class CreateCompanyRequestBody(BaseModel):
    name: str


@router.get("")
async def list_companies(list_companies_usecase: ListCompaniesUseCase = Depends(get_list_company_usecase)):
    try:
        companies = await list_companies_usecase.execute()
        return companies
    except Exception as e:
        app_logger.error(f"[COMPANY ROUTES] [LIST COMPANIES] [EXCEPTION] e: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not list companies") from e


@router.post("/create")
async def create_company(request: Request, body: CreateCompanyRequestBody, auth_service: AuthService = Depends(get_auth_service), create_company_usecase: CreateCompanyUseCase = Depends(get_create_company_usecase)):
    access = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    try:
        if not access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

        user: Awaitable[Optional[User]] = await auth_service.return_user_by_access_token(access)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find user")
        else:
            ensured_user: User = user  # type: ignore

        user_json = ensured_user.to_dict()

        app_logger.info(f"[COMPANY ROUTES] [CREATE COMPANY] user_id: {user_json.get('id')}")

        new_company = await create_company_usecase.execute(name=body.name, owner_id=user_json.get("id", ""))

        return new_company

    except Exception as e:
        app_logger.error(f"[AUTH ROUTES] [ME] [EXCEPTION] e: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is not valid") from e
