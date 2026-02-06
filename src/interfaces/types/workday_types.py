from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class PartialWorkdayUpdate:
    role_id: Optional[str] = None
    date: Optional[datetime] = None
    is_holiday: Optional[bool] = None


@dataclass(slots=True)
class BatchCreateWorkdays:
    start_date: datetime
    end_date: datetime
    role_id: str
