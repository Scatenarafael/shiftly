from src.interfaces.iusers_repository import IUsersRepository


class ListUsersUseCase:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository

    def execute(self):
        return self.users_repository.list()
