from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class WorkDay:
    id: Optional[int]
    role_id: str
    date: datetime
    is_holiday: bool
    weekday: Optional[int] = None
