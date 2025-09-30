from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.account.domain.entities.user import User


class IUsersRepository(ABC):
    @abstractmethod
    def list(self) -> list[User] | None:
        pass

    @abstractmethod
    def create(self, first_name: str, last_name: str, email: str, hashed_password: str, active: bool) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Dict[str, Any] | None:
        pass

    @abstractmethod
    def partial_update_by_id(self, id: str, first_name: Optional[str], last_name: Optional[str], email: Optional[str], hashed_password: Optional[str], active: Optional[bool]) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, id: str):
        pass

    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool:
        pass
