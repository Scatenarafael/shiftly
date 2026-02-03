import pytest


class FakeUserRepo:
    def __init__(self):
        self.emails = set()

    async def exists_by_email(self, email: str) -> bool:
        return email in self.emails

    async def save(self, email: str) -> int:
        self.emails.add(email)
        return 1


@pytest.mark.asyncio
async def test_create_user_success():
    # Arrange
    repo = FakeUserRepo()

    # Act
    user_id = await repo.save("a@b.com")

    # Assert
    assert user_id == 1
    assert await repo.exists_by_email("a@b.com") is True
