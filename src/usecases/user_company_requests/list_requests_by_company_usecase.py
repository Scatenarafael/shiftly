from src.domain.entities.user_company_requests import UserCompanyRequestStatus
from src.domain.errors import NotFoundError, PermissionDeniedError
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserCompanyRequestWithUser


class ListRequestsByCompanyUseCase:
    def __init__(self, user_company_requests_repository: IUserCompanyRequestsRepository, users_repository: IUsersRepository):
        self.user_company_requests_repository = user_company_requests_repository
        self.users_repository = users_repository

    async def execute(self, user_id: str, company_id: str, status: UserCompanyRequestStatus | None = None) -> list[UserCompanyRequestWithUser]:
        user = await self.users_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        is_owner = any(company_role.company_id == company_id and company_role.is_owner for company_role in user.companies_roles)
        if not is_owner:
            raise PermissionDeniedError("User does not have permission to view requests for this company")

        return await self.user_company_requests_repository.list_by_company(company_id=company_id, status=status)
