from typing import Optional

from src.account.interfaces.iusers_repository import IUsersRepository
from src.infra.settings.logging_config import app_logger


class PayloadUpdateUserDTO:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None


class UpdateUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self, user_id: str, payload: PayloadUpdateUserDTO):
        app_logger.info(f"[USER USE CASE] [UPDATE] user_id: {user_id}, payload: {payload}")

        user = await self.users_repository.partial_update_by_id(user_id, first_name=payload.first_name, last_name=payload.last_name, email=payload.email, active=payload.active, hashed_password=None)

        app_logger.info(f"[USER USE CASE] [UPDATE] user_id: {user_id}, user: {user}")

        return user
