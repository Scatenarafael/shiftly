from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class WorkShift:
    id: int
    work_day_id: str
    start_time: datetime
    end_time: datetime
