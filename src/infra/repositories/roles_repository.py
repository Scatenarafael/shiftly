from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.entities.role import Role as DomainRole
from src.infra.db.models.role import Role
from src.infra.settings.logging_config import app_logger
from src.interfaces.iroles_repository import IRolesRepository


class RolesRepository(IRolesRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain_role(model: Role) -> DomainRole:
        return DomainRole(
            id=str(model.id),
            name=str(model.name),
            company_id=str(model.company_id) if str(model.company_id) else None,
            number_of_cooldown_days=int(model.number_of_cooldown_days),  # type: ignore
        )

    async def list(self) -> list[DomainRole]:
        result = await self.session.execute(select(Role))  # type: ignore[arg-type]
        roles = result.scalars().all()
        return [self._to_domain_role(role) for role in roles]

    async def create(self, company_id: str, name: str, number_of_cooldown_days: int) -> DomainRole:
        new_register = Role(company_id=company_id, name=name, number_of_cooldown_days=number_of_cooldown_days)

        if not new_register:
            raise ValueError("Could not create role")

        self.session.add(new_register)
        await self.session.commit()
        await self.session.refresh(new_register)
        return self._to_domain_role(new_register)

    async def get_by_id(self, id: str):
        app_logger.info(f"[ROLE][GETBY][ID] not_none_args: {id}")
        result = await self.session.execute(select(Role).filter(Role.id == id))  # type: ignore[arg-type]
        role = result.scalars().first()
        if not role:
            return None
        return self._to_domain_role(role)

    async def partial_update_by_id(self, id: str, name: str | None, number_of_cooldown_days: int | None) -> DomainRole | None:
        result = await self.session.execute(select(Role).filter(Role.id == id))  # type: ignore[arg-type]
        role = result.scalars().first()
        if not role:
            return None

        args = {"name": name, "number_of_cooldown_days": number_of_cooldown_days}
        not_none_args = {k: v for k, v in args.items() if v is not None}

        app_logger.info(f"[ROLE][PARTIAL][UPDATE] not_none_args: {not_none_args}")

        for attr, value in not_none_args.items():
            setattr(role, attr, value)

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return self._to_domain_role(role)

    async def delete(self, id: str) -> None:
        app_logger.info(f"[ROLE][DELETE] role_id: {id}")
        await self.session.execute(delete(Role).where(Role.id == id))
        await self.session.commit()
