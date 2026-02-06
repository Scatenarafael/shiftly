from abc import ABC, abstractmethod
from typing import Any, Optional


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, subject: str) -> str:
        pass

    @abstractmethod
    def verify_access_token(self, token: str) -> Optional[dict[str, Any]]:
        pass

    @abstractmethod
    def generate_refresh_token_raw(self) -> str:
        pass

    @abstractmethod
    def hash_refresh_token(self, token: str) -> str:
        pass
