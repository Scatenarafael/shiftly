from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.company import Company


class ICompaniesRepository(ABC):
    @abstractmethod
    async def list(self) -> list[Company]:
        pass

    @abstractmethod
    async def create(self, name: str, owner_id: str) -> Company:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Company]:
        pass

    @abstractmethod
    async def partial_update_by_id(self, id: str, name: Optional[str]) -> Optional[Company]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        pass
