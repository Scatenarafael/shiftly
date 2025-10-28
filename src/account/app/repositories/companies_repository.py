from typing import List, Optional

from sqlalchemy import delete, select

from src.account.domain.entities.company import Company
from src.account.domain.entities.user_company_role import UserCompanyRole
from src.account.interfaces.icompanies_repository import ICompaniesRepository
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger


class CompaniesRepository(ICompaniesRepository):
    async def list(self) -> Optional[List[Company]]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(Company))  # type: ignore
                    companies = result.scalars().all()
                    return companies  # type: ignore
            except Exception as exception:
                raise exception

    async def create(self, name: str, owner_id: str) -> Optional[Company]:
        async with DbConnectionHandler() as database:
            try:
                new_register = Company(name=name)

                if not new_register:
                    raise ValueError("Could not create company")

                if database.session:
                    database.session.add(new_register)
                    await database.session.commit()
                    await database.session.refresh(new_register)
                    company_role_user = UserCompanyRole(user_id=owner_id, company_id=new_register.id, is_owner=True, role_id=None)
                    database.session.add(company_role_user)
                    await database.session.commit()
                    return new_register
            except Exception as exception:
                app_logger.error(f"[COMPANY][CREATE] Exception: {exception}")
                raise exception

    async def get_by_id(self, id: str) -> Optional[Company]:
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[COMPANY][GETBY][ID] not_none_args: {id}")
                if database.session:
                    result = await database.session.execute(select(Company).filter(Company.id == id))  # type: ignore
                    company = result.scalars().first()
                    app_logger.info(f"[COMPANY][GETBY][ID] company: {company}")
                    if not company:
                        raise LookupError("Company not found!")
                    return company  # type: ignore
            except Exception as exception:
                app_logger.error(f"[COMPANY][GETBY][ID] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    async def partial_update_by_id(self, id: str, name: str | None) -> Optional[Company]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(Company).filter(Company.id == id))  # type: ignore
                    company = result.scalars().first()
                    if not company:
                        raise ValueError("Company not found")

                args = {"name": name}

                not_none_args = {k: v for k, v in args.items() if v is not None}

                app_logger.info(f"[COMPANY][PARTIAL][UPDATE] not_none_args: {not_none_args}")

                for attr, value in not_none_args.items():
                    setattr(company, attr, value)

                if database.session:
                    database.session.add(company)
                    await database.session.commit()
                    await database.session.refresh(company)
                    return company  # type: ignore
            except Exception as exception:
                app_logger.error(f"[COMPANY][PARTIAL][UPDATE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    async def delete(self, id: str) -> None:
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[COMPANY][DELETE] company_id: {id}")
                if database.session:
                    await database.session.execute(delete(Company).where(Company.id == id))
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[COMPANY][DELETE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception
