from typing import Awaitable, List, Optional

from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.domain.entities.user_company_role import UserCompanyRole
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.types.user_types import CompaniesRolesFromUser, UsersRolesFromCompany


class UserCompanyRolesRepository(IUserCompanyRolesRepository):
    async def list_users_and_roles_by_company(self, company_id: str) -> Awaitable[List[Optional[UsersRolesFromCompany]]]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    query = (
                        select(UserCompanyRole)
                        .options(
                            selectinload(UserCompanyRole.user),
                            selectinload(UserCompanyRole.role),
                        )
                        .filter(UserCompanyRole.company_id == company_id)
                    )

                    result = await database.session.execute(query)
                    app_logger.info(f"[USER_COMPANY_ROLE][LIST][BY_COMPANY] result: {result}")
                    user_company_roles = result.scalars().all()

                    for ucr in user_company_roles:
                        app_logger.info(f"[USER_COMPANY_ROLE][LIST][BY_COMPANY] ucr: {ucr}")

                    return [UsersRolesFromCompany(ucr) for ucr in user_company_roles]  # type: ignore
            except Exception as exception:
                raise exception

    async def list_companies_and_roles_by_user(self, user_id: str) -> Awaitable[List[Optional[CompaniesRolesFromUser]]]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    query = (
                        select(UserCompanyRole)
                        .options(
                            selectinload(UserCompanyRole.company),
                            selectinload(UserCompanyRole.role),
                        )
                        .filter(UserCompanyRole.user_id == user_id)
                    )

                    result = await database.session.execute(query)
                    app_logger.info(f"[USER_COMPANY_ROLE][LIST][BY_COMPANY] result: {result}")
                    user_company_roles = result.scalars().all()

                    for ucr in user_company_roles:
                        app_logger.info(f"[USER_COMPANY_ROLE][LIST][BY_COMPANY] ucr: {ucr}")

                    return [CompaniesRolesFromUser(ucr) for ucr in user_company_roles]  # type: ignore
            except Exception as exception:
                raise exception

    # UserCompanyRole
    async def assign_user_and_role_to_company(self, user_id: str, company_id: str, role_id: str):
        async with DbConnectionHandler() as database:
            try:
                new_register = UserCompanyRole(user_id=user_id, company_id=company_id, role_id=role_id)

                app_logger.info(f"[USER][CREATE] new_register: (user_id: {user_id}, company_id: {company_id}, role_id: {role_id})")

                if not new_register:
                    raise ValueError("Could not create user")

                if database.session:
                    database.session.add(new_register)
                    await database.session.commit()
                    await database.session.refresh(new_register)
                    return new_register
            except Exception as exception:
                raise exception

    async def remove_user_company_role_register(self, register_id: str):
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[USER][DELETE] user_id: {register_id}")
                if database.session:
                    await database.session.execute(delete(UserCompanyRole).where(UserCompanyRole.id == register_id))
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[USER][DELETE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception
