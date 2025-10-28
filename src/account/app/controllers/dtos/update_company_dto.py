from typing import Optional

from pydantic import BaseModel


class PayloadUpdateCompanyDTO(BaseModel):
    name: Optional[str] = None
