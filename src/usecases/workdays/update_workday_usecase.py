from src.domain.entities.work_day import WorkDay
from src.domain.errors import NotFoundError
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class UpdateWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, workday_id: int, payload: PartialWorkdayUpdate) -> WorkDay:
        updated_workday = await self.workdays_repository.update(workday_id, payload)
        if not updated_workday:
            raise NotFoundError("Workday not found")
        return updated_workday
