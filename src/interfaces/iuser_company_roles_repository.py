from abc import ABC, abstractmethod

from src.interfaces.types.user_types import CompaniesRolesFromUser, UsersRolesFromCompany


class IUserCompanyRolesRepository(ABC):
    @abstractmethod
    async def list_users_and_roles_by_company(self, company_id: str) -> list[UsersRolesFromCompany]:
        pass

    @abstractmethod
    async def list_companies_and_roles_by_user(self, user_id: str) -> list[CompaniesRolesFromUser]:
        pass

    @abstractmethod
    async def assign_user_and_role_to_company(self, user_id: str, company_id: str, role_id: str | None) -> None:
        pass

    @abstractmethod
    async def remove_user_company_role_register(self, register_id: str) -> None:
        pass
