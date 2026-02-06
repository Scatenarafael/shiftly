from typing import List

from src.interfaces.iworkdays_repository import IWorkdaysRepository


class BatchDeleteWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, workday_ids: List[int]) -> None:
        await self.workdays_repository.batch_delete(workday_ids)
