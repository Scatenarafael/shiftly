from typing import Awaitable, List, Optional

from src.domain.entities.role import Role
from src.interfaces.iroles_repository import IRolesRepository


class ListRolesUseCase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self) -> Awaitable[Optional[List[Role]]]:
        return await self.roles_repository.list()
