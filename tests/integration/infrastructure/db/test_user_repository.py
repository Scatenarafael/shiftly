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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_partial_update_updates_user(db_session):
    repo = UsersRepository(db_session)
    created = await repo.create(first_name="Old", last_name="Name", email="old@b.com", password="secret", active=True)

    updated = await repo.partial_update_by_id(
        created.id,
        first_name="New",
        last_name=None,
        email=None,
        hashed_password=None,
        active=False,
    )

    assert updated is not None
    assert updated.first_name == "New"
    assert updated.active is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_delete_removes_user(db_session):
    repo = UsersRepository(db_session)
    created = await repo.create(first_name="Delete", last_name="Me", email="delete@b.com", password="secret", active=True)

    await repo.delete(created.id)
    fetched = await repo.get_by_id(created.id)

    assert fetched is None
