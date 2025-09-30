from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.account.domain.entities.refresh_token import RefreshToken


class IJWTRepository(ABC):
    @abstractmethod
    def save_refresh_token(self, jti: str, user_id: str, token_hash: str, expires_at: datetime) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    def revoke_token(self, token: RefreshToken, replaced_by: str | None = None):
        pass

    @abstractmethod
    def delete_token(self, token: RefreshToken):
        pass

    @abstractmethod
    def revoke_all_for_user(self, user_id: str):
        pass
