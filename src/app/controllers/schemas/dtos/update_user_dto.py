from src.interfaces.types.user_types import UserUpdatePayload


class UpdateUserDTO:
    @staticmethod
    def from_payload(payload: dict) -> UserUpdatePayload:
        return UserUpdatePayload(**payload)
