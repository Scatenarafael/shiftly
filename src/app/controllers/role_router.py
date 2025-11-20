from typing import Awaitable, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.app.controllers.dtos.update_role_dto import PayloadUpdateRoleDTO
from src.app.repositories.jwt_repository import JWTRepository
from src.app.repositories.roles_repository import RolesRepository
from src.app.repositories.users_repository import UsersRepository
from src.domain.entities.user import User
from src.infra.settings.config import get_settings
from src.infra.settings.logging_config import app_logger
from src.usecases.auth_service import AuthService
from src.usecases.roles.create_role_usecase import CreateRoleUseCase
from src.usecases.roles.delete_role_usecase import DeleteRoleUseCase
from src.usecases.roles.list_roles_usecase import ListRolesUseCase
from src.usecases.roles.update_roles_usecase import UpdateRolesUsecase

router = APIRouter(tags=["roles"], prefix="/roles")

settings = get_settings()


def get_create_role_usecase():
    return CreateRoleUseCase(RolesRepository())


def get_list_role_usecase():
    return ListRolesUseCase(RolesRepository())


def get_update_role_usecase():
    return UpdateRolesUsecase(RolesRepository())


def get_delete_role_usecase():
    return DeleteRoleUseCase(RolesRepository())


def get_auth_service() -> AuthService:
    return AuthService(UsersRepository(), JWTRepository())


class CreateRoleRequestBody(BaseModel):
    name: str
    number_of_cooldown_days: int


@router.get("")
async def list_roles(list_roles_usecase: ListRolesUseCase = Depends(get_list_role_usecase)):
    try:
        roles = await list_roles_usecase.execute()
        return roles
    except Exception as e:
        app_logger.error(f"[ROLE ROUTES] [LIST roles] [EXCEPTION] e: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not list roles") from e


@router.post("/create")
async def create_role(request: Request, body: CreateRoleRequestBody, auth_service: AuthService = Depends(get_auth_service), create_role_usecase: CreateRoleUseCase = Depends(get_create_role_usecase)):
    access = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    try:
        if not access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

        user: Awaitable[Optional[User]] = await auth_service.return_user_by_access_token(access)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find user")
        else:
            ensured_user: User = user  # type: ignore

        user_json = ensured_user.to_dict()

        app_logger.info(f"[ROLE ROUTES] [CREATE role] user_id: {user_json.get('id')}")

        new_role = await create_role_usecase.execute(name=body.name, number_of_cooldown_days=body.number_of_cooldown_days)

        return new_role

    except Exception as e:
        app_logger.error(f"[AUTH ROUTES] [ME] [EXCEPTION] e: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is not valid") from e


@router.patch("/{role_id}")
async def update_role(role_id: str, payload: PayloadUpdateRoleDTO, update_roles_usecase: UpdateRolesUsecase = Depends(get_update_role_usecase)):
    try:
        role = await update_roles_usecase.execute(id=role_id, name=payload.name)
        return role
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str):
    try:
        await get_delete_role_usecase().execute(role_id=role_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return Response(status_code=status.HTTP_204_NO_CONTENT)
