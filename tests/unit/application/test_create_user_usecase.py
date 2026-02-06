import pytest

from src.domain.entities.user import User
from src.domain.errors import AlreadyExistsError
from src.usecases.users.create_user_usecase import CreateUserUseCase


class FakeUserRepo:
    def __init__(self):
        self.users: dict[str, User] = {}

    async def list(self):
        return list(self.users.values())

    async def create(self, first_name: str, last_name: str, email: str, password: str, active: bool):
        user = User(
            id="1",
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password="hashed",
            active=active,
            created_at=None,
            companies_roles=[],
        )
        self.users[email] = user
        return user

    async def get_by_email(self, email: str):
        return self.users.get(email)

    async def get_by_id(self, id: str):
        return None

    async def partial_update_by_id(self, id: str, first_name, last_name, email, hashed_password, active):
        return None

    async def delete(self, id: str):
        return None

    def verify_password(self, plain: str, hashed: str) -> bool:
        return True


@pytest.mark.asyncio
async def test_create_user_success():
    # Arrange
    repo = FakeUserRepo()
    usecase = CreateUserUseCase(repo)

    # Act
    user = await usecase.execute(first_name="A", last_name="B", email="a@b.com", password="secret", active=True)

    # Assert
    assert user.email == "a@b.com"


@pytest.mark.asyncio
async def test_create_user_conflict():
    # Arrange
    repo = FakeUserRepo()
    usecase = CreateUserUseCase(repo)
    await usecase.execute(first_name="A", last_name="B", email="a@b.com", password="secret", active=True)

    # Act / Assert
    with pytest.raises(AlreadyExistsError):
        await usecase.execute(first_name="A", last_name="B", email="a@b.com", password="secret", active=True)
