from src.domain.errors import AlreadyExistsError
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserPublicDTO
from src.usecases.users.mappers import to_user_public


class CreateUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self, first_name: str, last_name: str, email: str, password: str, active: bool) -> UserPublicDTO:
        existing = await self.users_repository.get_by_email(email)
        if existing:
            raise AlreadyExistsError("User already exists")

        user = await self.users_repository.create(first_name=first_name, last_name=last_name, email=email, password=password, active=active)
        return to_user_public(user)
