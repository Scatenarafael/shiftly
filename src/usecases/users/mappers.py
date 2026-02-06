from typing import List, Optional

from src.domain.entities.user import User
from src.domain.entities.user_company_role import UserCompanyRole
from src.interfaces.types.user_types import CompanyDTO, RoleDTO, UserCompanyRoleDTO, UserDetailDTO, UserPublicDTO


def _to_company_dto(company) -> Optional[CompanyDTO]:
    if not company:
        return None
    return CompanyDTO(id=company.id, name=company.name)


def _to_role_dto(role) -> Optional[RoleDTO]:
    if not role:
        return None
    return RoleDTO(id=role.id, name=role.name, company_id=role.company_id, number_of_cooldown_days=role.number_of_cooldown_days)


def _to_user_company_role_dto(ucr: UserCompanyRole) -> UserCompanyRoleDTO:
    return UserCompanyRoleDTO(
        id=ucr.id,
        company=_to_company_dto(ucr.company),
        role=_to_role_dto(ucr.role),
        is_owner=ucr.is_owner,
    )


def to_user_public(user: User) -> UserPublicDTO:
    return UserPublicDTO(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        active=user.active,
        created_at=user.created_at,
    )


def to_user_detail(user: User) -> UserDetailDTO:
    companies_roles: List[UserCompanyRoleDTO] = [_to_user_company_role_dto(ucr) for ucr in user.companies_roles]
    return UserDetailDTO(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        active=user.active,
        created_at=user.created_at,
        companies_roles=companies_roles,
    )
