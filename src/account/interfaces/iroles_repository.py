from abc import ABC, abstractmethod
from typing import Awaitable, Optional

from src.account.domain.entities.role import Role


class IRolesRepository(ABC):
    @abstractmethod
    async def list(self) -> Awaitable[list[Role] | None]:
        pass

    @abstractmethod
    async def create(self, name: str) -> Awaitable[Optional[Role]]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Awaitable[Optional[Role]]:
        pass

    @abstractmethod
    async def partial_update_by_id(self, id: str, name: Optional[str]) -> Awaitable[Optional[Role]]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> Awaitable[None]:
        pass
