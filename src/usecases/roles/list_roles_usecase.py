from src.interfaces.iroles_repository import IRolesRepository
from src.interfaces.types.user_types import RoleDTO
from src.usecases.roles.mappers import to_role_dto


class ListRolesUseCase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self) -> list[RoleDTO]:
        roles = await self.roles_repository.list()
        return [to_role_dto(role) for role in roles]
