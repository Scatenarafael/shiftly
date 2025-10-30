from typing import Awaitable, List, Optional

from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.types.user_types import UsersRolesFromCompany


class ListUserAndRolesByCompanyUseCase:
    def __init__(self, user_role_company_repository: IUserCompanyRolesRepository):
        self.user_role_company_repository = user_role_company_repository

    async def execute(self, company_id: str) -> Awaitable[Optional[List[UsersRolesFromCompany]]]:
        return await self.user_role_company_repository.list_users_and_roles_by_company(company_id=company_id)  # type: ignore
