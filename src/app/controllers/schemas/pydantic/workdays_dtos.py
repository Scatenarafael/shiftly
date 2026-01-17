from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, field_validator

from src.interfaces.types.workday_types import PartialWorkdayUpdate


class CreateWorkdayPayload(BaseModel):
    role_id: str
    weekday: int
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
    weekday: Optional[int] = None
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
