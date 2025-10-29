from src.interfaces.icompanies_repository import ICompaniesRepository


class DeleteCompanyUseCase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self, company_id: str) -> None:
        await self.companies_repository.delete(id=company_id)
