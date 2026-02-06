from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository


class AssignUserRoleToCompanyUseCase:
    def __init__(self, user_role_company_repository: IUserCompanyRolesRepository):
        self.user_role_company_repository = user_role_company_repository

    async def execute(self, user_id: str, company_id: str, role_id: str) -> None:
        await self.user_role_company_repository.assign_user_and_role_to_company(user_id=user_id, company_id=company_id, role_id=role_id)
