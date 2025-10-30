from typing import Optional

from pydantic import BaseModel

from src.domain.entities.company import Company
from src.domain.entities.role import Role
from src.domain.entities.user_company_role import UserCompanyRole


class UserUpdateRequestBody(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None


class UserFromCompany:
    id: str
    name: str
    email: str
    active: bool

    def __init__(self, id: str, name: str, email: str, active: bool):
        self.id = id
        self.name = name
        self.email = email
        self.active = active


class UsersRolesFromCompany:
    user: UserFromCompany
    role: Role

    def __init__(self, user_company_role: UserCompanyRole):
        self.user = UserFromCompany(
            id=str(user_company_role.user_id), name=f"{user_company_role.user.first_name}.{user_company_role.user.last_name}", email=user_company_role.user.email, active=user_company_role.user.active
        )

        self.role = user_company_role.role


class CompaniesRolesFromUser:
    company: Company
    role: Role

    def __init__(self, user_company_role: UserCompanyRole):
        self.company = Company(id=str(user_company_role.company_id), name=user_company_role.company.name)

        self.role = user_company_role.role
