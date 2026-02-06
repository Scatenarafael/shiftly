from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, field_validator

from src.domain.entities.work_day import WorkDay
from src.interfaces.types.workday_types import BatchCreateWorkdays, PartialWorkdayUpdate


class CreateWorkdayPayload(BaseModel):
    role_id: str
    date: datetime
    is_holiday: bool

    @field_validator("date")
    @classmethod
    def normalize_date(cls, v: datetime) -> datetime:
        # boa prática: trabalhar com timezone-aware e salvar em UTC
        if v.tzinfo is None:
            # ou você rejeita (melhor, se seu contrato exigir TZ)
            # raise ValueError("date must include timezone info")
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class UpdateWorkdayPayload(BaseModel):
    role_id: Optional[str] = None
    date: Optional[datetime] = None
    is_holiday: Optional[bool] = None

    @field_validator("date")
    @classmethod
    def normalize_date(cls, v: datetime) -> datetime:
        # boa prática: trabalhar com timezone-aware e salvar em UTC
        if v.tzinfo is None:
            # ou você rejeita (melhor, se seu contrato exigir TZ)
            # raise ValueError("date must include timezone info")
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class UpdateWorkdayDTO:
    @staticmethod
    def from_payload(workday: UpdateWorkdayPayload) -> PartialWorkdayUpdate:
        return PartialWorkdayUpdate(**workday.model_dump(exclude_unset=True))


class BatchCreateWorkdaysPayload(BaseModel):
    start_date: datetime
    end_date: datetime
    role_id: str

    @field_validator("start_date", "end_date")
    @classmethod
    def normalize_date(cls, v: datetime) -> datetime:
        # boa prática: trabalhar com timezone-aware e salvar em UTC
        if v.tzinfo is None:
            # ou você rejeita (melhor, se seu contrato exigir TZ)
            # raise ValueError("date must include timezone info")
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class DateWorkdayPayload(BaseModel):
    date: datetime
    is_holiday: bool = False

    @field_validator("date")
    @classmethod
    def normalize_date(cls, v: datetime) -> datetime:
        # boa prática: trabalhar com timezone-aware e salvar em UTC
        if v.tzinfo is None:
            # ou você rejeita (melhor, se seu contrato exigir TZ)
            # raise ValueError("date must include timezone info")
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class BatchIndividualCreateWorkdaysPayload(BaseModel):
    role_id: str
    dates: List[DateWorkdayPayload]


class BatchIndividualCreateWorkdaysDTO:
    @staticmethod
    def from_payload(payload: BatchIndividualCreateWorkdaysPayload) -> List[WorkDay]:
        workdays: List[WorkDay] = []
        for date_payload in payload.dates:
            workday = {
                "role_id": payload.role_id,
                "date": date_payload.date,
                "is_holiday": date_payload.is_holiday,
                "weekday": date_payload.date.weekday(),
                "id": None,
            }
            workdays.append(WorkDay(**workday))
        return workdays


class BatchCreateWorkdaysDTO:
    @staticmethod
    def from_payload(payload: BatchCreateWorkdaysPayload) -> BatchCreateWorkdays:
        return BatchCreateWorkdays(start_date=payload.start_date, end_date=payload.end_date, role_id=payload.role_id)


class BatchDeleteWorkdaysPayload(BaseModel):
    workday_ids: List[int]


class WorkdayResponse(BaseModel):
    id: Optional[int]
    role_id: str
    date: datetime
    is_holiday: bool
    weekday: Optional[int] = None
