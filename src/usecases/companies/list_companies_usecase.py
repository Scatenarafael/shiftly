from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.types.user_types import CompanyDTO
from src.usecases.companies.mappers import to_company_dto


class ListCompaniesUseCase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self) -> list[CompanyDTO]:
        companies = await self.companies_repository.list()
        return [to_company_dto(company) for company in companies]
