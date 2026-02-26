from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Request, status as http_status

from src.app.controllers.schemas.pydantic.user_schemas import (
    UserCompanyRequestCreateRequest,
    UserCompanyRequestResponse,
    UserCompanyRequestWithUserResponse,
    UserSummaryResponse,
)
from src.app.dependencies import (
    get_companies_repository,
    get_user_company_requests_repository,
    get_user_company_roles_repository,
    get_users_repository,
)
from src.domain.entities.user_company_requests import UserCompanyRequestStatus
from src.domain.errors import AlreadyExistsError, NotFoundError, PermissionDeniedError, ValidationError
from src.interfaces.icompanies_repository import ICompaniesRepository
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserCompanyRequestDTO, UserCompanyRequestWithUser
from src.usecases.user_company_requests.approve_user_company_request_usecase import ApproveUserCompanyRequestUseCase
from src.usecases.user_company_requests.create_user_company_request_usecase import CreateUserCompanyRequestUseCase
from src.usecases.user_company_requests.list_requests_by_company_usecase import ListRequestsByCompanyUseCase
from src.usecases.user_company_requests.reject_user_company_request_usecase import RejectUserCompanyRequestUseCase

router = APIRouter(tags=["company-requests"], prefix="/company-requests")


def get_create_request_usecase(
    user_company_requests_repository: IUserCompanyRequestsRepository = Depends(get_user_company_requests_repository),
    users_repository: IUsersRepository = Depends(get_users_repository),
    companies_repository: ICompaniesRepository = Depends(get_companies_repository),
    user_company_roles_repository: IUserCompanyRolesRepository = Depends(get_user_company_roles_repository),
):
    return CreateUserCompanyRequestUseCase(
        user_company_requests_repository=user_company_requests_repository,
        users_repository=users_repository,
        companies_repository=companies_repository,
        user_company_roles_repository=user_company_roles_repository,
    )


def get_list_requests_usecase(
    user_company_requests_repository: IUserCompanyRequestsRepository = Depends(get_user_company_requests_repository),
    users_repository: IUsersRepository = Depends(get_users_repository),
):
    return ListRequestsByCompanyUseCase(user_company_requests_repository, users_repository)


def get_approve_request_usecase(
    user_company_requests_repository: IUserCompanyRequestsRepository = Depends(get_user_company_requests_repository),
    users_repository: IUsersRepository = Depends(get_users_repository),
    user_company_roles_repository: IUserCompanyRolesRepository = Depends(get_user_company_roles_repository),
):
    return ApproveUserCompanyRequestUseCase(user_company_requests_repository, users_repository, user_company_roles_repository)


def get_reject_request_usecase(
    user_company_requests_repository: IUserCompanyRequestsRepository = Depends(get_user_company_requests_repository),
    users_repository: IUsersRepository = Depends(get_users_repository),
):
    return RejectUserCompanyRequestUseCase(user_company_requests_repository, users_repository)


def _to_request_response(dto: UserCompanyRequestDTO) -> UserCompanyRequestResponse:
    return UserCompanyRequestResponse(
        id=dto.id,
        user_id=dto.user_id,
        company_id=dto.company_id,
        status=dto.status.value,
        accepted=dto.accepted,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


def _to_request_with_user_response(dto: UserCompanyRequestWithUser) -> UserCompanyRequestWithUserResponse:
    return UserCompanyRequestWithUserResponse(
        id=dto.id,
        user=UserSummaryResponse(**asdict(dto.user)),
        company_id=dto.company_id,
        status=dto.status.value,
        accepted=dto.accepted,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post("", response_model=UserCompanyRequestResponse, status_code=http_status.HTTP_201_CREATED)
async def create_company_request(
    request: Request,
    payload: UserCompanyRequestCreateRequest,
    create_request_usecase: CreateUserCompanyRequestUseCase = Depends(get_create_request_usecase),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

    try:
        new_request = await create_request_usecase.execute(user_id=user_id, company_id=payload.company_id)
        return _to_request_response(new_request)
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/by-company/{company_id}", response_model=list[UserCompanyRequestWithUserResponse])
async def list_requests_by_company(
    request: Request,
    company_id: str,
    status: UserCompanyRequestStatus | None = None,
    list_requests_usecase: ListRequestsByCompanyUseCase = Depends(get_list_requests_usecase),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

    try:
        results = await list_requests_usecase.execute(user_id=user_id, company_id=company_id, status=status)
        return [_to_request_with_user_response(item) for item in results]
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{request_id}/approve", response_model=UserCompanyRequestResponse)
async def approve_company_request(
    request: Request,
    request_id: str,
    approve_request_usecase: ApproveUserCompanyRequestUseCase = Depends(get_approve_request_usecase),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

    try:
        updated = await approve_request_usecase.execute(request_id=request_id, owner_id=user_id)
        return _to_request_response(updated)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{request_id}/reject", response_model=UserCompanyRequestResponse)
async def reject_company_request(
    request: Request,
    request_id: str,
    reject_request_usecase: RejectUserCompanyRequestUseCase = Depends(get_reject_request_usecase),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

    try:
        updated = await reject_request_usecase.execute(request_id=request_id, owner_id=user_id)
        return _to_request_response(updated)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
