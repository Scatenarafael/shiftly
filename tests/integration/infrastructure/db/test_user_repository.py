import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_can_persist_user(db_session):
    # Here you instantiate your real repo that uses SQLAlchemy session.
    # repo = SqlAlchemyUserRepository(db_session)

    # Example pseudo-assert:
    # await repo.add(User(email="a@b.com"))
    # user = await repo.get_by_email("a@b.com")
    # assert user is not None
    assert db_session is not None
