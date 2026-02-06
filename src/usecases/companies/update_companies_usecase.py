from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.types.user_types import CompanyDTO
from src.usecases.companies.mappers import to_company_dto


class UpdateCompaniesUsecase:
    def __init__(self, companies_repository: ICompaniesRepository):
        self.companies_repository = companies_repository

    async def execute(self, id: str, name: str | None) -> CompanyDTO | None:
        company = await self.companies_repository.partial_update_by_id(id=id, name=name)
        if not company:
            return None
        return to_company_dto(company)
