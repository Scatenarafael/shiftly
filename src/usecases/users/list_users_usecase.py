from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserPublicDTO
from src.usecases.users.mappers import to_user_public


class ListUsersUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self) -> list[UserPublicDTO]:
        users = await self.users_repository.list()
        return [to_user_public(user) for user in users]
