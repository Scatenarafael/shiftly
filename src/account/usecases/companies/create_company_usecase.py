from typing import Awaitable, Optional

from src.account.domain.entities.company import Company
from src.account.interfaces.icompanies_repository import ICompaniesRepository


class CreateCompanyUseCase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self, name: str, owner_id: str) -> Awaitable[Optional[Company]]:
        return await self.companies_repository.create(name=name, owner_id=owner_id)
