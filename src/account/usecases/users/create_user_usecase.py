from typing import Awaitable, Optional

from src.account.domain.entities.user import User
from src.account.interfaces.iusers_repository import IUsersRepository


class CreateUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self, first_name: str, last_name: str, email: str, password: str, active: bool) -> Awaitable[Optional[User]]:
        return await self.users_repository.create(first_name=first_name, last_name=last_name, email=email, password=password, active=active)
