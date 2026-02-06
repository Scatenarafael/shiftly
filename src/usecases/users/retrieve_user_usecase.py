from src.domain.errors import NotFoundError
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserDetailDTO
from src.usecases.users.mappers import to_user_detail


class RetrieveUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self, user_id: str) -> UserDetailDTO:
        user = await self.users_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return to_user_detail(user)
