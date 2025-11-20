from typing import Awaitable, List, Optional

from sqlalchemy import delete
from sqlalchemy.future import select

from src.domain.entities.role import Role
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger
from src.interfaces.iroles_repository import IRolesRepository


class RolesRepository(IRolesRepository):
    async def list(self) -> Awaitable[Optional[List[Role]]]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(Role))  # type: ignore
                    roles = result.scalars().all()
                    return roles  # type: ignore
            except Exception as exception:
                raise exception

    async def create(self, company_id: str, name: str, number_of_cooldown_days: int) -> Awaitable[Optional[Role]]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                new_register = Role(company_id=company_id, name=name, number_of_cooldown_days=number_of_cooldown_days)

                if not new_register:
                    raise ValueError("Could not create role")

                if database.session:
                    database.session.add(new_register)
                    await database.session.commit()
                    await database.session.refresh(new_register)
                    await database.session.commit()
                    return new_register
            except Exception as exception:
                app_logger.error(f"[ROLE][CREATE] Exception: {exception}")
                raise exception

    async def get_by_id(self, id: str) -> Awaitable[Optional[Role | None]]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[ROLE][GETBY][ID] not_none_args: {id}")
                if database.session:
                    result = await database.session.execute(select(Role).filter(Role.id == id))  # type: ignore
                    role = result.scalars().first()
                    app_logger.info(f"[ROLE][GETBY][ID] role: {role}")
                    if not role:
                        raise LookupError("Role not found!")
                    return role  # type: ignore
            except Exception as exception:
                app_logger.error(f"[ROLE][GETBY][ID] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    async def partial_update_by_id(self, id: str, name: str | None) -> Awaitable[Optional[Role]]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(Role).filter(Role.id == id))  # type: ignore
                    role = result.scalars().first()
                    if not role:
                        raise ValueError("Role not found")

                args = {"name": name}

                not_none_args = {k: v for k, v in args.items() if v is not None}

                app_logger.info(f"[ROLE][PARTIAL][UPDATE] not_none_args: {not_none_args}")

                for attr, value in not_none_args.items():
                    setattr(role, attr, value)

                if database.session:
                    database.session.add(role)
                    await database.session.commit()
                    await database.session.refresh(role)
                    return role  # type: ignore
            except Exception as exception:
                app_logger.error(f"[ROLE][PARTIAL][UPDATE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    async def delete(self, id: str) -> Awaitable[None]:  # type: ignore
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[ROLE][DELETE] ROLE_id: {id}")
                if database.session:
                    await database.session.execute(delete(Role).where(Role.id == id))
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[ROLE][DELETE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception
