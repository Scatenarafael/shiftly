from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.entities.user_company_role import UserCompanyRole


@dataclass(slots=True)
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    hashed_password: Optional[str]
    active: bool
    created_at: Optional[datetime] = None
    companies_roles: List[UserCompanyRole] = field(default_factory=list)
