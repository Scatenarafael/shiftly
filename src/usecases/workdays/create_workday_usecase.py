from src.domain.entities.work_day import WorkDay
from src.interfaces.iworkdays_repository import IWorkdaysRepository


class CreateWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, workday: WorkDay):
        created_workday = await self.workdays_repository.create(workday)
        return created_workday
