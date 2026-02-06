from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.company import Company as DomainCompany
from src.infra.db.models.company import Company
from src.infra.db.models.user_company_role import UserCompanyRole
from src.infra.settings.logging_config import app_logger
from src.interfaces.icompanies_repository import ICompaniesRepository


class CompaniesRepository(ICompaniesRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain_company(model: Company) -> DomainCompany:
        return DomainCompany(id=str(model.id), name=model.name)

    async def list(self) -> list[DomainCompany]:
        result = await self.session.execute(select(Company))  # type: ignore[arg-type]
        companies = result.scalars().all()
        return [self._to_domain_company(company) for company in companies]

    async def create(self, name: str, owner_id: str) -> DomainCompany:
        new_register = Company(name=name)

        if not new_register:
            raise ValueError("Could not create company")

        self.session.add(new_register)
        await self.session.commit()
        await self.session.refresh(new_register)

        company_role_user = UserCompanyRole(user_id=owner_id, company_id=new_register.id, is_owner=True, role_id=None)
        self.session.add(company_role_user)
        await self.session.commit()

        return self._to_domain_company(new_register)

    async def get_by_id(self, id: str):
        app_logger.info(f"[COMPANY][GETBY][ID] not_none_args: {id}")
        result = await self.session.execute(select(Company).filter(Company.id == id))  # type: ignore[arg-type]
        company = result.scalars().first()
        if not company:
            return None
        return self._to_domain_company(company)

    async def partial_update_by_id(self, id: str, name: str | None):
        result = await self.session.execute(select(Company).filter(Company.id == id))  # type: ignore[arg-type]
        company = result.scalars().first()
        if not company:
            return None

        args = {"name": name}
        not_none_args = {k: v for k, v in args.items() if v is not None}

        app_logger.info(f"[COMPANY][PARTIAL][UPDATE] not_none_args: {not_none_args}")

        for attr, value in not_none_args.items():
            setattr(company, attr, value)

        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return self._to_domain_company(company)

    async def delete(self, id: str) -> None:
        app_logger.info(f"[COMPANY][DELETE] company_id: {id}")
        await self.session.execute(delete(Company).where(Company.id == id))
        await self.session.commit()
