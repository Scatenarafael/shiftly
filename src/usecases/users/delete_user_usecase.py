from src.interfaces.iusers_repository import IUsersRepository


class DeleteUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    def execute(self, user_id: str):
        return self.users_repository.delete(user_id)
