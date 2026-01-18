from datetime import datetime
from typing import List

from src.domain.entities.work_day import WorkDay
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.types.workday_types import BatchCreateWorkdays
from src.usecases.workdays.utils import days_between_iso_utc


class BatchIntervalCreateWorkdayUseCase:
    def __init__(self, workdays_repository: IWorkdaysRepository):
        self.workdays_repository = workdays_repository

    async def execute(self, payload: BatchCreateWorkdays):
        start_date = payload.start_date

        end_date = payload.end_date

        role_id = payload.role_id

        list_of_days = days_between_iso_utc(start_date, end_date)

        print("List of days to create workdays for:", list_of_days)

        workdays_list: List[WorkDay] = []

        days_with_errors: List[str] = []

        for day in list_of_days:
            inserted_workday = await self.workdays_repository.find_by_date(datetime.fromisoformat(str(day)))

            if inserted_workday:
                days_with_errors.append(day)
                return

            workdays_list.append(WorkDay(role_id=role_id, date=day, weekday=datetime.fromisoformat(day).weekday()))

        print("workdays_list: ", workdays_list)
        created_workdays = await self.workdays_repository.batch_create(payloads=workdays_list)

        if days_with_errors:
            raise ValueError(f"Workdays for dates {', '.join(days_with_errors)} already exist. The others were created successfully.")

        return created_workdays
