from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(slots=True)
class UserUpdatePayload:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None


@dataclass(slots=True)
class CompanyDTO:
    id: str
    name: str


@dataclass(slots=True)
class RoleDTO:
    id: str
    name: str
    company_id: Optional[str]
    number_of_cooldown_days: int


@dataclass(slots=True)
class UserCompanyRoleDTO:
    id: str
    company: Optional[CompanyDTO]
    role: Optional[RoleDTO]
    is_owner: bool


@dataclass(slots=True)
class UserPublicDTO:
    id: str
    first_name: str
    last_name: str
    email: str
    active: bool
    created_at: Optional[datetime]


@dataclass(slots=True)
class UserDetailDTO(UserPublicDTO):
    companies_roles: List[UserCompanyRoleDTO]


@dataclass(slots=True)
class UserSummaryDTO:
    id: str
    name: str
    email: str
    active: bool


@dataclass(slots=True)
class UsersRolesFromCompany:
    user: UserSummaryDTO
    role: Optional[RoleDTO]


@dataclass(slots=True)
class CompaniesRolesFromUser:
    company: CompanyDTO
    role: Optional[RoleDTO]
