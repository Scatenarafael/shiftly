from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class UserCompanyRequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(slots=True)
class UserCompanyRequests:
    id: str
    user_id: str
    company_id: str
    status: UserCompanyRequestStatus
    accepted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
