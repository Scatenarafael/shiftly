from src.domain.entities.user_company_requests import UserCompanyRequests
from src.interfaces.types.user_types import UserCompanyRequestDTO


def to_user_company_request_dto(request: UserCompanyRequests) -> UserCompanyRequestDTO:
    return UserCompanyRequestDTO(
        id=request.id,
        user_id=request.user_id,
        company_id=request.company_id,
        status=request.status,
        accepted=request.accepted,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )
