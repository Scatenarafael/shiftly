from abc import ABC, abstractmethod
from typing import Awaitable, Optional

from src.account.domain.entities.company import Company


class ICompaniesRepository(ABC):
    @abstractmethod
    async def list(self) -> Awaitable[list[Company] | None]:
        pass

    @abstractmethod
    async def create(self, name: str, owner_id: str) -> Awaitable[Optional[Company]]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Awaitable[Optional[Company]]:
        pass

    @abstractmethod
    async def partial_update_by_id(self, id: str, name: Optional[str]) -> Awaitable[Optional[Company]]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> Awaitable[None]:
        pass
