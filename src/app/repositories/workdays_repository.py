from typing import List, Optional

from sqlalchemy import select

from src.domain.entities.work_day import WorkDay
from src.infra.settings.connection import DbConnectionHandler
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class WorkdaysRepository(IWorkdaysRepository):
    async def list(self) -> Optional[List[WorkDay]]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(WorkDay).order_by(WorkDay.date.asc()))  # type: ignore
                    workdays = result.scalars().all()

                    return workdays  # type: ignore
            except Exception as exception:
                raise exception

    async def create(self, workday: WorkDay) -> Optional[WorkDay]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    database.session.add(workday)
                    await database.session.commit()
                    await database.session.refresh(workday)
                    return workday
            except Exception as exception:
                raise exception

    async def get_by_id(self, workday_id: int) -> Optional[WorkDay]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
                    workday = result.scalars().first()
                    return workday
            except Exception as exception:
                raise exception

    async def update(self, workday_id: int, payload: PartialWorkdayUpdate) -> Optional[WorkDay]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
                    workday = result.scalars().first()
                    if workday:
                        for key, value in payload.__dict__.items():
                            if value is not None:
                                setattr(workday, key, value)
                        database.session.add(workday)
                        await database.session.commit()
                    await database.session.refresh(workday)
                    return workday
            except Exception as exception:
                raise exception

    async def delete(self, workday_id: int) -> None:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
                    workday = result.scalars().first()
                    if workday:
                        await database.session.delete(workday)
                        await database.session.commit()
            except Exception as exception:
                raise exception
