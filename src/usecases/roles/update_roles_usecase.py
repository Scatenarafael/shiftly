from typing import Awaitable, Optional

from src.domain.entities.role import Role
from src.interfaces.iroles_repository import IRolesRepository


class UpdateRolesUsecase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self, id: str, name: str | None) -> Awaitable[Optional[Role]]:
        return await self.roles_repository.partial_update_by_id(id=id, name=name)
