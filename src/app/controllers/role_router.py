from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.app.controllers.schemas.dtos.update_role_dto import PayloadUpdateRoleDTO
from src.app.controllers.schemas.pydantic.user_schemas import RoleResponse
from src.app.dependencies import get_roles_repository, get_users_repository
from src.domain.errors import NotFoundError, PermissionDeniedError
from src.interfaces.iroles_repository import IRolesRepository
from src.interfaces.iusers_repository import IUsersRepository
from src.usecases.roles.create_role_usecase import CreateRoleUseCase
from src.usecases.roles.delete_role_usecase import DeleteRoleUseCase
from src.usecases.roles.list_roles_usecase import ListRolesUseCase
from src.usecases.roles.update_roles_usecase import UpdateRolesUsecase

router = APIRouter(tags=["roles"], prefix="/roles")


def get_create_role_usecase(
    roles_repository: IRolesRepository = Depends(get_roles_repository),
    users_repository: IUsersRepository = Depends(get_users_repository),
):
    return CreateRoleUseCase(roles_repository, users_repository)


def get_list_role_usecase(roles_repository: IRolesRepository = Depends(get_roles_repository)):
    return ListRolesUseCase(roles_repository)


def get_update_role_usecase(roles_repository: IRolesRepository = Depends(get_roles_repository)):
    return UpdateRolesUsecase(roles_repository)


def get_delete_role_usecase(roles_repository: IRolesRepository = Depends(get_roles_repository)):
    return DeleteRoleUseCase(roles_repository)


class CreateRoleRequestBody(BaseModel):
    name: str
    company_id: str
    number_of_cooldown_days: int


@router.get("", response_model=list[RoleResponse])
async def list_roles(list_roles_usecase: ListRolesUseCase = Depends(get_list_role_usecase)):
    try:
        roles = await list_roles_usecase.execute()
        return [RoleResponse(**asdict(role)) for role in roles]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not list roles") from exc


@router.post("/create", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(request: Request, body: CreateRoleRequestBody, create_role_usecase: CreateRoleUseCase = Depends(get_create_role_usecase)):
    try:
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

        new_role = await create_role_usecase.execute(
            name=body.name,
            user_id=user_id,
            company_id=body.company_id,
            number_of_cooldown_days=body.number_of_cooldown_days,
        )

        return RoleResponse(**asdict(new_role))

    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, payload: PayloadUpdateRoleDTO, update_roles_usecase: UpdateRolesUsecase = Depends(get_update_role_usecase)):
    try:
        role = await update_roles_usecase.execute(id=role_id, name=payload.name, number_of_cooldown_days=payload.number_of_cooldown_days)
        if not role:
            raise NotFoundError("Role not found")
        return RoleResponse(**asdict(role))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str, delete_role_usecase: DeleteRoleUseCase = Depends(get_delete_role_usecase)):
    try:
        await delete_role_usecase.execute(role_id=role_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
