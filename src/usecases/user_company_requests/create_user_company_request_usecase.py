from src.domain.errors import AlreadyExistsError, NotFoundError, ValidationError
from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserCompanyRequestDTO
from src.usecases.user_company_requests.mappers import to_user_company_request_dto


class CreateUserCompanyRequestUseCase:
    def __init__(
        self,
        user_company_requests_repository: IUserCompanyRequestsRepository,
        users_repository: IUsersRepository,
        companies_repository: ICompaniesRepository,
        user_company_roles_repository: IUserCompanyRolesRepository,
    ):
        self.user_company_requests_repository = user_company_requests_repository
        self.users_repository = users_repository
        self.companies_repository = companies_repository
        self.user_company_roles_repository = user_company_roles_repository

    async def execute(self, user_id: str, company_id: str) -> UserCompanyRequestDTO:
        user = await self.users_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        company = await self.companies_repository.get_by_id(company_id)
        if not company:
            raise NotFoundError("Company not found")

        companies_roles = await self.user_company_roles_repository.list_companies_and_roles_by_user(user_id=user_id)
        if any(role.company.id == company_id for role in companies_roles):
            raise ValidationError("User already linked to company")

        pending_request = await self.user_company_requests_repository.get_pending_by_user_and_company(user_id=user_id, company_id=company_id)
        if pending_request:
            raise AlreadyExistsError("User already has a pending request for this company")

        request = await self.user_company_requests_repository.create(user_id=user_id, company_id=company_id)
        return to_user_company_request_dto(request)
