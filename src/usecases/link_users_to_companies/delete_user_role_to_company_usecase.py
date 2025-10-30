from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository


class DeleteUserRoleToCompanyUseCase:
    def __init__(self, user_role_company_repository: IUserCompanyRolesRepository):
        self.user_role_company_repository = user_role_company_repository

    async def execute(self, register_id: str) -> None:
        await self.user_role_company_repository.remove_user_company_role_register(register_id=register_id)
