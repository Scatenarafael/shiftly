from datetime import datetime
from typing import Optional


class PartialWorkdayUpdate:
    role_id: Optional[str] = None
    weekday: Optional[int] = None
    date: Optional[datetime] = None
    is_holiday: Optional[bool] = None

    def __init__(self, role_id: Optional[str] = None, weekday: Optional[int] = None, date: Optional[datetime] = None, is_holiday: Optional[bool] = None):
        self.role_id = role_id
        self.weekday = weekday
        self.date = date
        self.is_holiday = is_holiday
