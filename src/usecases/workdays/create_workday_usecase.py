from datetime import datetime

from src.domain.entities.work_day import WorkDay
from src.domain.errors import AlreadyExistsError
from src.interfaces.iworkdays_repository import IWorkdaysRepository


class CreateWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, workday: WorkDay) -> WorkDay:
        inserted_workday = await self.workdays_repository.find_by_date(datetime.fromisoformat(str(workday.date)))

        if inserted_workday:
            raise AlreadyExistsError(f"Workday for date {workday.date} already exists.")

        created_workday = await self.workdays_repository.create(workday)
        return created_workday
