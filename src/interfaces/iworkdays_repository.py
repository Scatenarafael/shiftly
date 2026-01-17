from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.work_day import WorkDay
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class IWorkdaysRepository(ABC):
    """Interface for Workdays Repository."""

    @abstractmethod
    async def list(self) -> Optional[List[WorkDay]]:
        pass

    @abstractmethod
    async def create(self, workday: WorkDay) -> Optional[WorkDay]:
        pass

    @abstractmethod
    async def get_by_id(self, workday_id: int) -> Optional[WorkDay]:
        pass

    @abstractmethod
    async def update(self, workday_id: int, payload: PartialWorkdayUpdate) -> Optional[WorkDay]:
        pass

    @abstractmethod
    async def delete(self, workday_id: int) -> None:
        pass
