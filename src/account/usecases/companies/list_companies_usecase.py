from typing import Awaitable, List, Optional

from src.account.domain.entities.company import Company
from src.account.interfaces.icompanies_repository import ICompaniesRepository


class ListCompaniesUseCase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self) -> Awaitable[Optional[List[Company]]]:
        return await self.companies_repository.list()
