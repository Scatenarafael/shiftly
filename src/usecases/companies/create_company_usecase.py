from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.types.user_types import CompanyDTO
from src.usecases.companies.mappers import to_company_dto


class CreateCompanyUseCase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self, name: str, owner_id: str) -> CompanyDTO:
        company = await self.companies_repository.create(name=name, owner_id=owner_id)
        return to_company_dto(company)
