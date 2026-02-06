from dataclasses import asdict
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.work_day import WorkDay as DomainWorkDay
from src.infra.db.models.work_day import WorkDay
from src.interfaces.iworkdays_repository import IWorkdaysRepository
from src.interfaces.types.workday_types import PartialWorkdayUpdate


class WorkdaysRepository(IWorkdaysRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain_workday(model: WorkDay) -> DomainWorkDay:
        return DomainWorkDay(
            id=model.id,
            role_id=str(model.role_id),
            date=model.date,
            is_holiday=model.is_holiday,
            weekday=model.weekday,
        )

    async def list(self) -> List[DomainWorkDay]:
        result = await self.session.execute(select(WorkDay).order_by(WorkDay.date.asc()))  # type: ignore[arg-type]
        return [self._to_domain_workday(w) for w in result.scalars().all()]

    async def create(self, workday: DomainWorkDay) -> DomainWorkDay:
        model = WorkDay(
            role_id=workday.role_id,
            date=workday.date,
            is_holiday=workday.is_holiday,
            weekday=workday.weekday,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain_workday(model)

    async def batch_create(self, payloads: List[DomainWorkDay]) -> List[DomainWorkDay]:
        if not payloads:
            return []

        rows: List[dict[str, Any]] = [
            {
                "role_id": w.role_id,
                "weekday": w.weekday,
                "date": datetime.fromisoformat(str(w.date)),
                "is_holiday": w.is_holiday,
            }
            for w in payloads
        ]

        stmt = insert(WorkDay).returning(WorkDay)
        result = await self.session.execute(stmt, rows)
        await self.session.commit()
        return [self._to_domain_workday(w) for w in result.scalars().all()]

    async def get_by_id(self, workday_id: int) -> Optional[DomainWorkDay]:
        result = await self.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
        model = result.scalars().first()
        if not model:
            return None
        return self._to_domain_workday(model)

    async def find_by_date(self, date: datetime) -> Optional[DomainWorkDay]:
        result = await self.session.execute(select(WorkDay).where(WorkDay.date == date))
        model = result.scalars().first()
        if not model:
            return None
        return self._to_domain_workday(model)

    async def update(self, workday_id: int, payload: PartialWorkdayUpdate) -> Optional[DomainWorkDay]:
        result = await self.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
        workday = result.scalars().first()
        if not workday:
            return None
        for key, value in asdict(payload).items():
            if value is not None:
                setattr(workday, key, value)
        self.session.add(workday)
        await self.session.commit()
        await self.session.refresh(workday)
        return self._to_domain_workday(workday)

    async def delete(self, workday_id: int) -> None:
        result = await self.session.execute(select(WorkDay).where(WorkDay.id == workday_id))
        workday = result.scalars().first()
        if workday:
            await self.session.delete(workday)
            await self.session.commit()

    async def batch_delete(self, workday_ids: List[int]) -> None:
        stmt = delete(WorkDay).where(WorkDay.id.in_(workday_ids))  # type: ignore[arg-type]
        await self.session.execute(stmt)
        await self.session.commit()
