from src.domain.entities.role import Role
from src.interfaces.types.user_types import RoleDTO


def to_role_dto(role: Role) -> RoleDTO:
    return RoleDTO(id=role.id, name=role.name, company_id=role.company_id, number_of_cooldown_days=role.number_of_cooldown_days)
