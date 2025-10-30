from typing import Awaitable, Optional

from src.domain.entities.role import Role
from src.interfaces.iroles_repository import IRolesRepository


class CreateRoleUseCase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self, name: str) -> Awaitable[Optional[Role]]:
        return await self.roles_repository.create(name=name)
