from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import delete, insert, select

from src.domain.entities.work_day import WorkDay
from src.infra.settings.connection import DbConnectionHandler
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class WorkdaysRepository(IWorkdaysRepository):
    async def list(self) -> Optional[List[WorkDay]]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(
                        select(WorkDay).order_by(WorkDay.date.asc())  # type: ignore
                    )
                    return result.scalars().all()  # type: ignore
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

    async def batch_create(self, payloads: List[WorkDay]) -> Optional[List[WorkDay]]:
        async with DbConnectionHandler() as database:
            if not database.session:
                return None
            if not payloads:
                return []

            rows: List[dict[str, Any]] = [
                {
                    "role_id": w.role_id,
                    "weekday": w.weekday,
                    "date": datetime.fromisoformat(str(w.date)),  # ✅ tem que ser datetime/date, NÃO string
                    "is_holiday": w.is_holiday,
                }
                for w in payloads
            ]

            stmt = insert(WorkDay).returning(WorkDay)  # Postgres ok
            result = await database.session.execute(stmt, rows)
            await database.session.commit()
            return result.scalars().all()  # type: ignore

    async def get_by_id(self, workday_id: int) -> Optional[WorkDay]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
                    return result.scalars().first()
            except Exception as exception:
                raise exception

    async def find_by_date(self, date: datetime) -> Optional[WorkDay]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(WorkDay).where(WorkDay.date == date))
                    return result.scalars().first()
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

    async def batch_delete(self, workday_ids: List[int]) -> None:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    stmt = delete(WorkDay).where(WorkDay.id.in_(workday_ids))  # type: ignore
                    await database.session.execute(stmt)
                    await database.session.commit()

            except Exception as exception:
                raise exception
