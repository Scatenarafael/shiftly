from __future__ import annotations

from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.company import Company as DomainCompany
from src.domain.entities.role import Role as DomainRole
from src.domain.entities.user import User as DomainUser
from src.domain.entities.user_company_role import UserCompanyRole as DomainUserCompanyRole
from src.infra.db.models.company import Company
from src.infra.db.models.role import Role
from src.infra.db.models.user import User
from src.infra.db.models.user_company_role import UserCompanyRole
from src.infra.settings.logging_config import app_logger
from src.interfaces.iusers_repository import IUsersRepository

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersRepository(IUsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain_company(model: Company | None) -> Optional[DomainCompany]:
        if not model:
            return None
        return DomainCompany(id=str(model.id), name=model.name)

    @staticmethod
    def _to_domain_role(model: Role | None) -> Optional[DomainRole]:
        if not model:
            return None
        return DomainRole(
            id=str(model.id),
            name=model.name,
            company_id=str(model.company_id) if model.company_id else None,
            number_of_cooldown_days=model.number_of_cooldown_days,
        )

    @classmethod
    def _to_domain_user_company_role(cls, model: UserCompanyRole) -> DomainUserCompanyRole:
        return DomainUserCompanyRole(
            id=str(model.id),
            user_id=str(model.user_id),
            company_id=str(model.company_id),
            role_id=str(model.role_id) if model.role_id else None,
            is_owner=model.is_owner,
            company=cls._to_domain_company(model.company),
            role=cls._to_domain_role(model.role),
        )

    @classmethod
    def _to_domain_user(cls, model: User, include_roles: bool = False) -> DomainUser:
        companies_roles = []
        if include_roles and model.companies_roles:
            companies_roles = [cls._to_domain_user_company_role(ucr) for ucr in model.companies_roles]
        return DomainUser(
            id=str(model.id),
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            hashed_password=model.hashed_password,
            active=model.active,
            created_at=model.created_at,
            companies_roles=companies_roles,
        )

    async def list(self) -> list[DomainUser]:
        result = await self.session.execute(select(User).order_by(User.created_at.desc()))  # type: ignore[arg-type]
        users = result.scalars().all()
        return [self._to_domain_user(user, include_roles=False) for user in users]

    async def create(self, first_name: str, last_name: str, email: str, password: str, active: bool) -> DomainUser:
        new_register = User(first_name=first_name, last_name=last_name, email=email, hashed_password=pwd_ctx.hash(password), active=active)

        app_logger.info(
            f"[USER][CREATE] new_register: (first_name: {new_register.first_name}, last_name: {new_register.last_name}, email: {new_register.email}, active: {new_register.active})"
        )

        self.session.add(new_register)
        await self.session.commit()
        await self.session.refresh(new_register)
        return self._to_domain_user(new_register, include_roles=False)

    async def get_by_id(self, id: str) -> Optional[DomainUser]:
        app_logger.info(f"[USER][GETBY][ID] not_none_args: {id}")

        stmt = (
            select(User)
            .where(User.id == id)
            .options(
                selectinload(User.companies_roles).selectinload(UserCompanyRole.company),
                selectinload(User.companies_roles).selectinload(UserCompanyRole.role),
            )
        )

        result = await self.session.execute(stmt)
        user = result.scalars().unique().first()
        if not user:
            return None
        return self._to_domain_user(user, include_roles=True)

    async def get_by_email(self, email: str) -> Optional[DomainUser]:
        app_logger.info(f"[USER][GETBY][EMAIL] not_none_args: {email}")
        result = await self.session.execute(select(User).where(User.email == email))  # type: ignore[arg-type]
        user = result.scalars().first()
        if not user:
            return None
        return self._to_domain_user(user, include_roles=False)

    async def partial_update_by_id(
        self,
        id: str,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        hashed_password: str | None,
        active: bool | None,
    ) -> Optional[DomainUser]:
        result = await self.session.execute(select(User).filter(User.id == id))  # type: ignore[arg-type]
        user = result.scalars().first()
        if not user:
            return None

        args = {"first_name": first_name, "last_name": last_name, "email": email, "hashed_password": hashed_password, "active": active}
        not_none_args = {k: v for k, v in args.items() if v is not None}

        app_logger.info(f"[USER][PARTIAL][UPDATE] not_none_args: {not_none_args}")

        for attr, value in not_none_args.items():
            setattr(user, attr, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return self._to_domain_user(user, include_roles=False)

    async def delete(self, id: str) -> None:
        app_logger.info(f"[USER][DELETE] user_id: {id}")
        await self.session.execute(delete(User).where(User.id == id))
        await self.session.commit()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_ctx.verify(plain, hashed)
