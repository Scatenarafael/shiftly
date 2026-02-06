from src.domain.errors import NotFoundError, PermissionDeniedError
from src.interfaces.iroles_repository import IRolesRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import RoleDTO
from src.usecases.roles.mappers import to_role_dto


class CreateRoleUseCase:
    def __init__(self, roles_repository: IRolesRepository, users_repository: IUsersRepository):
        self.roles_repository = roles_repository
        self.users_repository = users_repository

    async def execute(self, name: str, user_id: str, company_id: str, number_of_cooldown_days: int) -> RoleDTO:
        user = await self.users_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        is_owner = any(company_role.company_id == company_id and company_role.is_owner for company_role in user.companies_roles)
        if not is_owner:
            raise PermissionDeniedError("User does not have permission to create roles for this company")

        role = await self.roles_repository.create(name=name, company_id=company_id, number_of_cooldown_days=number_of_cooldown_days)
        return to_role_dto(role)
