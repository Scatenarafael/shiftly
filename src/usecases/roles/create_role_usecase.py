from typing import Awaitable, Optional

from src.domain.entities.role import Role
from src.domain.entities.user import User
from src.interfaces.iroles_repository import IRolesRepository


class CreateRoleUseCase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self, name: str, user: User, company_id: str, number_of_cooldown_days: int) -> Awaitable[Optional[Role]]:
        for company_role in user.companies_roles:
            if company_role.company_id == company_id and not company_role.is_owner:
                raise PermissionError("User does not have permission to create roles for this company")

        return await self.roles_repository.create(name=name, company_id=company_id, number_of_cooldown_days=number_of_cooldown_days)
