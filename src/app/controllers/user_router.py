from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from src.app.controllers.schemas.dtos.update_user_dto import UpdateUserDTO
from src.app.controllers.schemas.pydantic.user_schemas import UserCreateRequest, UserDetailResponse, UserResponse, UserUpdateRequest
from src.app.dependencies import get_users_repository
from src.domain.errors import AlreadyExistsError, NotFoundError
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserUpdatePayload
from src.usecases.users.create_user_usecase import CreateUserUseCase
from src.usecases.users.delete_user_usecase import DeleteUserUseCase
from src.usecases.users.list_users_usecase import ListUsersUseCase
from src.usecases.users.retrieve_user_usecase import RetrieveUserUseCase
from src.usecases.users.update_user_usecase import UpdateUserUseCase

router = APIRouter(tags=["users"], prefix="/users")


def get_create_user_usecase(users_repository: IUsersRepository = Depends(get_users_repository)):
    return CreateUserUseCase(users_repository)


def get_list_users_usecase(users_repository: IUsersRepository = Depends(get_users_repository)):
    return ListUsersUseCase(users_repository)


def get_retrieve_user_usecase(users_repository: IUsersRepository = Depends(get_users_repository)):
    return RetrieveUserUseCase(users_repository)


def get_update_user_usecase(users_repository: IUsersRepository = Depends(get_users_repository)):
    return UpdateUserUseCase(users_repository)


def get_delete_user_usecase(users_repository: IUsersRepository = Depends(get_users_repository)):
    return DeleteUserUseCase(users_repository)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create(payload: UserCreateRequest, create_usecase: CreateUserUseCase = Depends(get_create_user_usecase)):
    try:
        new_user = await create_usecase.execute(first_name=payload.first_name, last_name=payload.last_name, email=payload.email, password=payload.password, active=payload.active)
        return UserResponse(**asdict(new_user))
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("", response_model=list[UserResponse])
async def list(list_users_usecase: ListUsersUseCase = Depends(get_list_users_usecase)):
    users = await list_users_usecase.execute()
    return [UserResponse(**asdict(user)) for user in users]


@router.get("/{user_id}", response_model=UserDetailResponse)
async def retrieve(user_id: str, retrieve_user_usecase: RetrieveUserUseCase = Depends(get_retrieve_user_usecase)):
    try:
        user = await retrieve_user_usecase.execute(user_id)
        return UserDetailResponse(**asdict(user))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}", response_model=UserResponse)
async def update(user_id: str, payload: UserUpdateRequest, update_usecase: UpdateUserUseCase = Depends(get_update_user_usecase)):
    try:
        dto_payload: UserUpdatePayload = UpdateUserDTO.from_payload(payload.model_dump(exclude_unset=True))
        updated_user = await update_usecase.execute(user_id, dto_payload)
        return UserResponse(**asdict(updated_user))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(user_id: str, delete_usecase: DeleteUserUseCase = Depends(get_delete_user_usecase)):
    await delete_usecase.execute(user_id)
    return None
