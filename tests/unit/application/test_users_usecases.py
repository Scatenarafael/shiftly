from datetime import datetime, timezone

import pytest

from src.domain.entities.user import User
from src.domain.errors import NotFoundError
from src.interfaces.types.user_types import UserUpdatePayload
from src.usecases.users.delete_user_usecase import DeleteUserUseCase
from src.usecases.users.list_users_usecase import ListUsersUseCase
from src.usecases.users.retrieve_user_usecase import RetrieveUserUseCase
from src.usecases.users.update_user_usecase import UpdateUserUseCase


class FakeUserRepo:
    def __init__(self):
        self.users: dict[str, User] = {}
        self.deleted_ids: list[str] = []

    async def list(self):
        return list(self.users.values())

    async def create(self, first_name: str, last_name: str, email: str, password: str, active: bool):
        user_id = str(len(self.users) + 1)
        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password="hashed",
            active=active,
            created_at=datetime.now(timezone.utc),
            companies_roles=[],
        )
        self.users[user_id] = user
        return user

    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def get_by_id(self, id: str):
        return self.users.get(id)

    async def partial_update_by_id(self, id: str, first_name, last_name, email, hashed_password, active):
        user = self.users.get(id)
        if not user:
            return None

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if hashed_password is not None:
            user.hashed_password = hashed_password
        if active is not None:
            user.active = active
        return user

    async def delete(self, id: str):
        self.deleted_ids.append(id)
        self.users.pop(id, None)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return plain == "secret"


@pytest.mark.asyncio
async def test_list_users_usecase_returns_public_dtos():
    repo = FakeUserRepo()
    await repo.create("A", "B", "first@b.com", "secret", True)
    await repo.create("C", "D", "second@b.com", "secret", False)

    usecase = ListUsersUseCase(repo)
    users = await usecase.execute()

    assert len(users) == 2
    assert users[0].email == "first@b.com"
    assert users[1].email == "second@b.com"


@pytest.mark.asyncio
async def test_retrieve_user_usecase_returns_detail():
    repo = FakeUserRepo()
    created = await repo.create("A", "B", "detail@b.com", "secret", True)

    usecase = RetrieveUserUseCase(repo)
    user = await usecase.execute(created.id)

    assert user.id == created.id
    assert user.email == "detail@b.com"
    assert user.companies_roles == []


@pytest.mark.asyncio
async def test_retrieve_user_usecase_not_found():
    repo = FakeUserRepo()
    usecase = RetrieveUserUseCase(repo)

    with pytest.raises(NotFoundError):
        await usecase.execute("missing-id")


@pytest.mark.asyncio
async def test_update_user_usecase_updates_fields():
    repo = FakeUserRepo()
    created = await repo.create("A", "B", "update@b.com", "secret", True)

    usecase = UpdateUserUseCase(repo)
    updated = await usecase.execute(created.id, UserUpdatePayload(first_name="Updated", active=False))

    assert updated.first_name == "Updated"
    assert updated.active is False


@pytest.mark.asyncio
async def test_update_user_usecase_not_found():
    repo = FakeUserRepo()
    usecase = UpdateUserUseCase(repo)

    with pytest.raises(NotFoundError):
        await usecase.execute("missing-id", UserUpdatePayload(first_name="Updated"))


@pytest.mark.asyncio
async def test_delete_user_usecase_calls_repository_delete():
    repo = FakeUserRepo()
    created = await repo.create("A", "B", "delete@b.com", "secret", True)

    usecase = DeleteUserUseCase(repo)
    await usecase.execute(created.id)

    assert created.id in repo.deleted_ids
    assert await repo.get_by_id(created.id) is None
