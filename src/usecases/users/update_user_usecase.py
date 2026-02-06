from src.domain.errors import NotFoundError
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserPublicDTO, UserUpdatePayload
from src.usecases.users.mappers import to_user_public


class UpdateUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self, user_id: str, payload: UserUpdatePayload) -> UserPublicDTO:
        user = await self.users_repository.partial_update_by_id(
            user_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            active=payload.active,
            hashed_password=None,
        )

        if not user:
            raise NotFoundError("User not found")

        return to_user_public(user)
