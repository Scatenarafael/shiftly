from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.domain.entities.refresh_token import RefreshToken


class IJWTRepository(ABC):
    @abstractmethod
    async def save_refresh_token(self, jti: str, user_id: str, token_hash: str, expires_at: datetime) -> RefreshToken:
        pass

    @abstractmethod
    async def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def revoke_token(self, token: RefreshToken, replaced_by: str | None = None) -> None:
        pass

    @abstractmethod
    async def delete_token(self, token: RefreshToken) -> None:
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: str) -> None:
        pass
