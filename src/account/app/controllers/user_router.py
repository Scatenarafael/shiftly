from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.account.app.repositories.users_repository import UsersRepository
from src.account.usecases.users.create_user_usecase import CreateUserUseCase

router = APIRouter(tags=["users"])


def get_create_user_usecase():
    return CreateUserUseCase(UsersRepository())


class UserRequestBody(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    active: bool


@router.post("/users")
async def create(payload: UserRequestBody, create_usecase: CreateUserUseCase = Depends(get_create_user_usecase)):
    new_user = await create_usecase.execute(first_name=payload.first_name, last_name=payload.last_name, email=payload.email, password=payload.password, active=payload.active)
    return new_user
