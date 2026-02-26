from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.domain.entities.user_company_requests import UserCompanyRequestStatus, UserCompanyRequests
from src.infra.db.models.user_company_requests import UserCompanyRequest
from src.infra.db.models.user_company_role import UserCompanyRole
from src.infra.settings.logging_config import app_logger
from src.interfaces.iuser_company_requests_repository import IUserCompanyRequestsRepository
from src.interfaces.types.user_types import UserCompanyRequestWithUser, UserSummaryDTO


class UserCompanyRequestsRepository(IUserCompanyRequestsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(model: UserCompanyRequest) -> UserCompanyRequests:
        return UserCompanyRequests(
            id=str(model.id),
            user_id=str(model.user_id),
            company_id=str(model.company_id),
            status=model.status,
            accepted=model.accepted,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_user_summary(user) -> UserSummaryDTO:
        return UserSummaryDTO(
            id=str(user.id),
            name=f"{user.first_name}.{user.last_name}",
            email=user.email,
            active=user.active,
        )

    async def _get_model_by_id(self, request_id: str) -> UserCompanyRequest | None:
        result = await self.session.execute(select(UserCompanyRequest).where(UserCompanyRequest.id == request_id))
        return result.scalars().first()

    async def create(self, user_id: str, company_id: str) -> UserCompanyRequests:
        new_register = UserCompanyRequest(user_id=user_id, company_id=company_id)
        app_logger.info(f"[USER_COMPANY_REQUEST][CREATE] user_id: {user_id}, company_id: {company_id}")
        self.session.add(new_register)
        await self.session.commit()
        await self.session.refresh(new_register)
        return self._to_domain(new_register)

    async def get_by_id(self, request_id: str) -> UserCompanyRequests | None:
        model = await self._get_model_by_id(request_id)
        if not model:
            return None
        return self._to_domain(model)

    async def get_pending_by_user_and_company(self, user_id: str, company_id: str) -> UserCompanyRequests | None:
        query = select(UserCompanyRequest).where(
            UserCompanyRequest.user_id == user_id,
            UserCompanyRequest.company_id == company_id,
            UserCompanyRequest.status == UserCompanyRequestStatus.PENDING,
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_domain(model)

    async def list_by_company(self, company_id: str, status: UserCompanyRequestStatus | None = None) -> list[UserCompanyRequestWithUser]:
        query = (
            select(UserCompanyRequest)
            .options(selectinload(UserCompanyRequest.user))
            .where(UserCompanyRequest.company_id == company_id)
            .order_by(UserCompanyRequest.created_at.desc())
        )
        if status is not None:
            query = query.where(UserCompanyRequest.status == status)

        result = await self.session.execute(query)
        requests = result.scalars().all()

        output: list[UserCompanyRequestWithUser] = []
        for request in requests:
            user = request.user
            output.append(
                UserCompanyRequestWithUser(
                    id=str(request.id),
                    user=self._to_user_summary(user),
                    company_id=str(request.company_id),
                    status=request.status,
                    accepted=request.accepted,
                    created_at=request.created_at,
                    updated_at=request.updated_at,
                )
            )
        return output

    async def approve(self, request_id: str, role_id: str | None) -> UserCompanyRequests:
        request = await self._get_model_by_id(request_id)
        if not request:
            raise ValueError("Request not found")

        request.status = UserCompanyRequestStatus.APPROVED
        request.accepted = True

        new_link = UserCompanyRole(
            user_id=request.user_id,
            company_id=request.company_id,
            role_id=role_id,
            is_owner=False,
        )

        app_logger.info(f"[USER_COMPANY_REQUEST][APPROVE] request_id: {request_id}")

        self.session.add(request)
        self.session.add(new_link)
        await self.session.commit()
        await self.session.refresh(request)
        return self._to_domain(request)

    async def reject(self, request_id: str) -> UserCompanyRequests:
        request = await self._get_model_by_id(request_id)
        if not request:
            raise ValueError("Request not found")

        request.status = UserCompanyRequestStatus.REJECTED
        request.accepted = False
        app_logger.info(f"[USER_COMPANY_REQUEST][REJECT] request_id: {request_id}")

        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return self._to_domain(request)
