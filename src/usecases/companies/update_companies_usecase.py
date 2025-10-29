from typing import Awaitable, Optional

from src.domain.entities.company import Company
from src.interfaces.icompanies_repository import ICompaniesRepository


class UpdateCompaniesUsecase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self, id: str, name: str | None) -> Awaitable[Optional[Company]]:
        return await self.companies_repository.partial_update_by_id(id=id, name=name)
