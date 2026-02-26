from src.domain.entities.user_company_requests import UserCompanyRequestStatus
from src.domain.errors import NotFoundError, PermissionDeniedError, ValidationError
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserCompanyRequestDTO
from src.usecases.user_company_requests.mappers import to_user_company_request_dto


class RejectUserCompanyRequestUseCase:
    def __init__(self, user_company_requests_repository: IUserCompanyRequestsRepository, users_repository: IUsersRepository):
        self.user_company_requests_repository = user_company_requests_repository
        self.users_repository = users_repository

    async def execute(self, request_id: str, owner_id: str) -> UserCompanyRequestDTO:
        request = await self.user_company_requests_repository.get_by_id(request_id=request_id)
        if not request:
            raise NotFoundError("Request not found")

        if request.status != UserCompanyRequestStatus.PENDING:
            raise ValidationError("Request already processed")

        owner = await self.users_repository.get_by_id(owner_id)
        if not owner:
            raise NotFoundError("User not found")

        is_owner = any(company_role.company_id == request.company_id and company_role.is_owner for company_role in owner.companies_roles)
        if not is_owner:
            raise PermissionDeniedError("User does not have permission to reject this request")

        updated = await self.user_company_requests_repository.reject(request_id=request_id)
        return to_user_company_request_dto(updated)
