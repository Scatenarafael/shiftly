from datetime import datetime
from typing import List

from src.domain.entities.work_day import WorkDay
from src.interfaces.iworkdays_repository import IWorkdaysRepository


class BatchIndividualCreateWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, payloads: List[WorkDay]):
        days_with_errors: List[str] = []

        workdays: List[WorkDay] = []

        for day in payloads:
            inserted_workday = await self.workdays_repository.find_by_date(datetime.fromisoformat(str(day.date)))

            if inserted_workday:
                days_with_errors.append(str(day.date))
                return
            workdays.append(day)

        created_workdays = await self.workdays_repository.batch_create(payloads=workdays)

        if days_with_errors:
            raise ValueError(f"Workdays for dates {', '.join(days_with_errors)} already exist. The others were created successfully.")

        return created_workdays
