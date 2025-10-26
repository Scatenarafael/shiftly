from abc import ABC, abstractmethod
from typing import Awaitable

from src.account.interfaces.types.user_types import CompaniesRolesFromUser, UsersRolesFromCompany


class IUserCompanyRolesRepository(ABC):
    @abstractmethod
    async def list_users_and_roles_by_company(self, company_id: str) -> Awaitable[list[UsersRolesFromCompany] | None]:
        pass

    @abstractmethod
    async def list_companies_and_roles_by_user(self, user_id: str) -> Awaitable[list[CompaniesRolesFromUser] | None]:
        pass

    @abstractmethod
    async def assign_user_and_role_to_company(self, user_id: str, company_id: str, role_id: str) -> Awaitable[None]:
        pass

    @abstractmethod
    async def remove_user_company_role_register(self, register_id: str) -> Awaitable[None]:
        pass
