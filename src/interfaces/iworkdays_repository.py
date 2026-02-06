from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.domain.entities.work_day import WorkDay
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class IWorkdaysRepository(ABC):
    """Interface for Workdays Repository."""

    @abstractmethod
    async def list(self) -> List[WorkDay]:
        pass

    @abstractmethod
    async def batch_create(self, payloads: List[WorkDay]) -> List[WorkDay]:
        pass

    @abstractmethod
    async def create(self, workday: WorkDay) -> WorkDay:
        pass

    @abstractmethod
    async def get_by_id(self, workday_id: int) -> Optional[WorkDay]:
        pass

    @abstractmethod
    async def find_by_date(self, date: datetime) -> Optional[WorkDay]:
        pass

    @abstractmethod
    async def update(self, workday_id: int, payload: PartialWorkdayUpdate) -> Optional[WorkDay]:
        pass

    @abstractmethod
    async def delete(self, workday_id: int) -> None:
        pass

    @abstractmethod
    async def batch_delete(self, workday_ids: List[int]) -> None:
        pass
