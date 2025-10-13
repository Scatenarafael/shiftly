from src.account.interfaces.iusers_repository import IUsersRepository


class RetrieveUserUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    def execute(self, user_id: str):
        return self.users_repository.get_by_id(user_id)
