from src.interfaces.iroles_repository import IRolesRepository
from src.interfaces.types.user_types import RoleDTO
from src.usecases.roles.mappers import to_role_dto


class UpdateRolesUsecase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self, id: str, name: str | None, number_of_cooldown_days: int | None) -> RoleDTO | None:
        role = await self.roles_repository.partial_update_by_id(id=id, name=name, number_of_cooldown_days=number_of_cooldown_days)
        if not role:
            return None
        return to_role_dto(role)
