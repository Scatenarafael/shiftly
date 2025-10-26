from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.account.app.controllers.dtos.update_user_dto import UpdateUserDTO
from src.account.app.repositories.users_repository import UsersRepository
from src.account.interfaces.types.user_types import UserUpdateRequestBody
from src.account.usecases.users.create_user_usecase import CreateUserUseCase
from src.account.usecases.users.delete_user_usecase import DeleteUserUseCase
from src.account.usecases.users.list_users_usecase import ListUsersUseCase
from src.account.usecases.users.retrieve_user_usecase import RetrieveUserUseCase
from src.account.usecases.users.update_user_usecase import UpdateUserUseCase
from src.infra.settings.logging_config import app_logger

router = APIRouter(tags=["users"], prefix="/users")


def get_create_user_usecase():
    return CreateUserUseCase(UsersRepository())


def get_list_users_usecase():
    return ListUsersUseCase(UsersRepository())


def get_retrieve_user_usecase():
    return RetrieveUserUseCase(UsersRepository())


def get_update_user_usecase():
    return UpdateUserUseCase(UsersRepository())


def get_delete_user_usecase():
    return DeleteUserUseCase(UsersRepository())


class UserRequestBody(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    active: bool


@router.post("/register")
async def create(payload: UserRequestBody, create_usecase: CreateUserUseCase = Depends(get_create_user_usecase)):
    new_user = await create_usecase.execute(first_name=payload.first_name, last_name=payload.last_name, email=payload.email, password=payload.password, active=payload.active)
    return new_user


@router.get("")
async def list(list_users_usecase: ListUsersUseCase = Depends(get_list_users_usecase)):
    users = await list_users_usecase.execute()
    return users


@router.get("/{user_id}")
async def retrieve(user_id: str, retrieve_user_usecase: RetrieveUserUseCase = Depends(get_retrieve_user_usecase)):
    user = await retrieve_user_usecase.execute(user_id)
    return user


@router.patch("/{user_id}")
async def update(user_id: str, payload: UserUpdateRequestBody, update_usecase: UpdateUserUseCase = Depends(get_update_user_usecase)):
    app_logger.info(f"[USER ROUTER] [UPDATE] Payload ONLY received for update: {payload}")
    updated_user = await update_usecase.execute(user_id, UpdateUserDTO(payload).to_payload_dto())
    return updated_user


@router.delete("/{user_id}")
async def delete(user_id: str, delete_usecase: DeleteUserUseCase = Depends(get_delete_user_usecase)):
    await delete_usecase.execute(user_id)
    return {"message": "User deleted successfully"}
