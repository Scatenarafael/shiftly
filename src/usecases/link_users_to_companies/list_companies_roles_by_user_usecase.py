from typing import Awaitable, List, Optional

from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.types.user_types import UsersRolesFromCompany


class ListCompaniesAndRolesByUserUseCase:
    def __init__(self, user_role_company_repository: IUserCompanyRolesRepository):
        self.user_role_company_repository = user_role_company_repository

    async def execute(self, user_id: str) -> Awaitable[Optional[List[UsersRolesFromCompany]]]:
        return await self.user_role_company_repository.list_companies_and_roles_by_user(user_id=user_id)  # type: ignore
