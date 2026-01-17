from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class UpdateWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, workday_id: int, payload: PartialWorkdayUpdate):
        updated_workday = await self.workdays_repository.update(workday_id, payload)
        return updated_workday
