from typing import Optional

from pydantic import BaseModel


class PayloadUpdateRoleDTO(BaseModel):
    name: Optional[str] = None
    number_of_cooldown_days: Optional[int] = None
