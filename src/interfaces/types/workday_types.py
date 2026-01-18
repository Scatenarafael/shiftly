from datetime import datetime
from typing import Optional


class PartialWorkdayUpdate:
    role_id: Optional[str] = None
    date: Optional[datetime] = None
    is_holiday: Optional[bool] = None

    def __init__(self, role_id: Optional[str] = None, date: Optional[datetime] = None, is_holiday: Optional[bool] = None):
        self.role_id = role_id
        self.date = date
        self.is_holiday = is_holiday


class BatchCreateWorkdays:
    start_date: datetime
    end_date: datetime
    role_id: str

    def __init__(self, start_date: datetime, end_date: datetime, role_id: str):
        self.start_date = start_date
        self.end_date = end_date
        self.role_id = role_id
