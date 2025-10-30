from src.interfaces.iroles_repository import IRolesRepository


class DeleteRoleUseCase:
    def __init__(self, roles_repository: IRolesRepository):
        self.roles_repository = roles_repository

    async def execute(self, role_id: str) -> None:
        await self.roles_repository.delete(id=role_id)
