from abc import ABC, abstractmethod
from typing import Awaitable, Optional

from src.account.domain.entities.user import User


class IUsersRepository(ABC):
    @abstractmethod
    async def list(self) -> Awaitable[list[User] | None]:
        pass

    @abstractmethod
    async def create(self, first_name: str, last_name: str, email: str, password: str, active: bool) -> Awaitable[Optional[User]]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Awaitable[Optional[User]]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Awaitable[Optional[User]]:
        pass

    @abstractmethod
    async def partial_update_by_id(self, id: str, first_name: Optional[str], last_name: Optional[str], email: Optional[str], hashed_password: Optional[str], active: Optional[bool]) -> Awaitable[Optional[User]]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> Awaitable[None]:
        pass

    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool:
        pass
