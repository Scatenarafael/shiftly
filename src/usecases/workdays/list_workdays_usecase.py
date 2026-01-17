from typing import List, Optional

from src.domain.entities.work_day import WorkDay
from src.interfaces.iworkdays_repository import IWorkdaysRepository


class ListWorkdaysUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self) -> Optional[List[WorkDay]]:
        workdays = await self.workdays_repository.list()
        return workdays
