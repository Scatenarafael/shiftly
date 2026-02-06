from src.interfaces.iusers_repository import IUsersRepository


class DeleteUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    async def execute(self, user_id: str) -> None:
        await self.users_repository.delete(user_id)
