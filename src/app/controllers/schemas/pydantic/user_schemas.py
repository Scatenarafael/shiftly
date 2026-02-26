from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    active: bool


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None


class CompanyResponse(BaseModel):
    id: str
    name: str


class RoleResponse(BaseModel):
    id: str
    name: str
    company_id: Optional[str]
    number_of_cooldown_days: int


class UserCompanyRoleResponse(BaseModel):
    id: str
    company: Optional[CompanyResponse]
    role: Optional[RoleResponse]
    is_owner: bool


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    active: bool
    created_at: Optional[datetime]


class UserDetailResponse(UserResponse):
    companies_roles: List[UserCompanyRoleResponse]


class UserSummaryResponse(BaseModel):
    id: str
    name: str
    email: str
    active: bool


class UsersRolesFromCompanyResponse(BaseModel):
    user: UserSummaryResponse
    is_owner: bool
    role: Optional[RoleResponse]


class CompaniesRolesFromUserResponse(BaseModel):
    company: CompanyResponse
    is_owner: bool
    role: Optional[RoleResponse]


class UserCompanyRequestCreateRequest(BaseModel):
    company_id: str


class UserCompanyRequestResponse(BaseModel):
    id: str
    user_id: str
    company_id: str
    status: str
    accepted: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class UserCompanyRequestWithUserResponse(BaseModel):
    id: str
    user: UserSummaryResponse
    company_id: str
    status: str
    accepted: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
