from src.domain.entities.company import Company
from src.interfaces.types.user_types import CompanyDTO


def to_company_dto(company: Company) -> CompanyDTO:
    return CompanyDTO(id=company.id, name=company.name)
