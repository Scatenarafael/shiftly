from typing import Optional

from pydantic import BaseModel

from src.account.domain.entities.company import Company
from src.account.domain.entities.role import Role


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


class UsersRolesFromCompany:
    user: UserFromCompany
    role: Role


class CompaniesRolesFromUser:
    company: Company
    role: Role
