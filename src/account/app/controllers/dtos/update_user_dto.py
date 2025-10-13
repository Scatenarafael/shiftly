from typing import Optional

from pydantic import BaseModel

from src.account.usecases.users.update_user_usecase import PayloadUpdateUserDTO


class UserUpdateRequestBody(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None


class UpdateUserDTO:
    payload: UserUpdateRequestBody

    def __init__(self, payload: UserUpdateRequestBody):
        self.payload = payload

    def to_payload_dto(self) -> PayloadUpdateUserDTO:
        dto = PayloadUpdateUserDTO()
        dto.first_name = self.payload.first_name
        dto.last_name = self.payload.last_name
        dto.email = self.payload.email
        dto.password = self.payload.password
        dto.active = self.payload.active
        return dto
