from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class RefreshToken:
    id: str
    user_id: str
    token_hash: str
    created_at: Optional[datetime]
    expires_at: datetime
    revoked: bool
    replaced_by: Optional[str]
