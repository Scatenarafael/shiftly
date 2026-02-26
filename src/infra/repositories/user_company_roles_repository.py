from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.infra.db.models.company import Company as CompanyModel
from src.infra.db.models.role import Role as RoleModel
from src.infra.db.models.user_company_role import UserCompanyRole
from src.infra.settings.logging_config import app_logger
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.types.user_types import (
    CompaniesRolesFromUser,
    CompanyDTO,
    RoleDTO,
    UsersRolesFromCompany,
    UserSummaryDTO,
)


class UserCompanyRolesRepository(IUserCompanyRolesRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _role_to_dto(role: RoleModel | None) -> RoleDTO | None:
        if not role:
            return None
        return RoleDTO(
            id=str(role.id),
            name=str(role.name),
            company_id=str(role.company_id) if str(role.company_id) else None,
            number_of_cooldown_days=int(str(role.number_of_cooldown_days)),
        )

    @staticmethod
    def _company_to_dto(company: CompanyModel | None) -> CompanyDTO | None:
        if not company:
            return None
        return CompanyDTO(id=str(company.id), name=str(company.name))

    async def list_users_and_roles_by_company(self, company_id: str) -> list[UsersRolesFromCompany]:
        query = (
            select(UserCompanyRole)
            .options(
                selectinload(UserCompanyRole.user),
                selectinload(UserCompanyRole.role),
            )
            .filter(UserCompanyRole.company_id == company_id)
        )

        result = await self.session.execute(query)
        user_company_roles = result.scalars().all()

        output: list[UsersRolesFromCompany] = []
        for ucr in user_company_roles:
            user = ucr.user
            role = ucr.role
            is_owner = bool(ucr.is_owner)
            output.append(
                UsersRolesFromCompany(
                    user=UserSummaryDTO(
                        id=str(ucr.user_id),
                        name=f"{user.first_name}.{user.last_name}",
                        email=user.email,
                        active=user.active,
                    ),
                    is_owner=is_owner,
                    role=self._role_to_dto(role),
                )
            )
        return output

    async def list_companies_and_roles_by_user(self, user_id: str) -> list[CompaniesRolesFromUser]:
        query = (
            select(UserCompanyRole)
            .options(
                selectinload(UserCompanyRole.company),
                selectinload(UserCompanyRole.role),
            )
            .filter(UserCompanyRole.user_id == user_id)
        )

        result = await self.session.execute(query)
        user_company_roles = result.scalars().all()

        output: list[CompaniesRolesFromUser] = []
        for ucr in user_company_roles:
            company = ucr.company
            role = ucr.role
            is_owner = bool(ucr.is_owner)
            output.append(
                CompaniesRolesFromUser(
                    company=CompanyDTO(id=str(company.id), name=company.name),
                    is_owner=is_owner,
                    role=self._role_to_dto(role),
                )
            )
        return output

    async def assign_user_and_role_to_company(self, user_id: str, company_id: str, role_id: str | None) -> None:
        new_register = UserCompanyRole(user_id=user_id, company_id=company_id, role_id=role_id)

        app_logger.info(f"[USER][CREATE] new_register: (user_id: {user_id}, company_id: {company_id}, role_id: {role_id})")

        self.session.add(new_register)
        await self.session.commit()
        await self.session.refresh(new_register)

    async def remove_user_company_role_register(self, register_id: str) -> None:
        app_logger.info(f"[USER][DELETE] user_id: {register_id}")
        await self.session.execute(delete(UserCompanyRole).where(UserCompanyRole.id == register_id))
        await self.session.commit()
