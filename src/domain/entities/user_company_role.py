from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities.company import Company
    from src.domain.entities.role import Role


@dataclass(slots=True)
class UserCompanyRole:
    id: str
    user_id: str
    company_id: str
    role_id: Optional[str]
    is_owner: bool
    company: Optional["Company"] = None
    role: Optional["Role"] = None
