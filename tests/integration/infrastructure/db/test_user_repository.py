import pytest

from src.infra.repositories.users_repository import UsersRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_can_persist_user(db_session):
    repo = UsersRepository(db_session)

    created = await repo.create(first_name="A", last_name="B", email="a@b.com", password="secret", active=True)
    fetched = await repo.get_by_email("a@b.com")

    assert created.email == "a@b.com"
    assert fetched is not None
    assert fetched.email == "a@b.com"
