from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user_company_requests import UserCompanyRequestStatus, UserCompanyRequests
from src.interfaces.types.user_types import UserCompanyRequestWithUser


class IUserCompanyRequestsRepository(ABC):
    @abstractmethod
    async def create(self, user_id: str, company_id: str) -> UserCompanyRequests:
        pass

    @abstractmethod
    async def get_by_id(self, request_id: str) -> Optional[UserCompanyRequests]:
        pass

    @abstractmethod
    async def get_pending_by_user_and_company(self, user_id: str, company_id: str) -> Optional[UserCompanyRequests]:
        pass

    @abstractmethod
    async def list_by_company(self, company_id: str, status: Optional[UserCompanyRequestStatus] = None) -> list[UserCompanyRequestWithUser]:
        pass

    @abstractmethod
    async def approve(self, request_id: str, role_id: str | None) -> UserCompanyRequests:
        pass

    @abstractmethod
    async def reject(self, request_id: str) -> UserCompanyRequests:
        pass
