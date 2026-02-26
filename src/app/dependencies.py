from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.ijwt_repository import IJWTRepository
from src.interfaces.iroles_repository import IRolesRepository
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.itoken_service import ITokenService
from src.app.controllers.auth_config import AuthCookieSettings


def _not_configured(name: str) -> RuntimeError:
    return RuntimeError(f"Dependency provider not configured: {name}")


def get_users_repository() -> IUsersRepository:
    raise _not_configured("get_users_repository")


def get_companies_repository() -> ICompaniesRepository:
    raise _not_configured("get_companies_repository")


def get_roles_repository() -> IRolesRepository:
    raise _not_configured("get_roles_repository")


def get_user_company_roles_repository() -> IUserCompanyRolesRepository:
    raise _not_configured("get_user_company_roles_repository")


def get_user_company_requests_repository() -> IUserCompanyRequestsRepository:
    raise _not_configured("get_user_company_requests_repository")


def get_workdays_repository() -> IWorkdaysRepository:
    raise _not_configured("get_workdays_repository")


def get_jwt_repository() -> IJWTRepository:
    raise _not_configured("get_jwt_repository")


def get_token_service() -> ITokenService:
    raise _not_configured("get_token_service")


def get_refresh_token_expire_days() -> int:
    raise _not_configured("get_refresh_token_expire_days")


def get_auth_cookie_settings() -> AuthCookieSettings:
    raise _not_configured("get_auth_cookie_settings")
