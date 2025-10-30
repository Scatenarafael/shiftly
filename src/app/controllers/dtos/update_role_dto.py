from typing import Optional

from pydantic import BaseModel


class PayloadUpdateRoleDTO(BaseModel):
    name: Optional[str] = None
