from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.role import Role


class IRolesRepository(ABC):
    @abstractmethod
    async def list(self) -> list[Role]:
        pass

    @abstractmethod
    async def create(self, company_id: str, name: str, number_of_cooldown_days: int) -> Role:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Role]:
        pass

    @abstractmethod
    async def partial_update_by_id(self, id: str, name: Optional[str]) -> Optional[Role]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        pass
