from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import delete, select

from src.account.domain.entities.user import User
from src.account.interfaces.iusers_repository import IUsersRepository
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersRepository(IUsersRepository):
    @classmethod
    async def list(cls) -> Optional[list[User]]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(User).order_by(User.created_at.desc()))  # type: ignore
                    users = result.scalars().all()
                    return users  # type: ignore
            except Exception as exception:
                raise exception

    @classmethod
    async def create(cls, first_name: str, last_name: str, email: str, password: str, active: bool) -> Optional[User]:
        async with DbConnectionHandler() as database:
            try:
                new_register = User(first_name=first_name, last_name=last_name, email=email, hashed_password=pwd_ctx.hash(password), active=active)

                app_logger.info(f"[USER][CREATE] new_register: (first_name: {new_register.first_name}, last_name: {new_register.last_name}, email: {new_register.email}, active: {new_register.active})")

                if not new_register:
                    raise ValueError("Could not create user")

                if database.session:
                    database.session.add(new_register)
                    await database.session.commit()
                    await database.session.refresh(new_register)
                    return new_register
            except Exception as exception:
                raise exception

    @classmethod
    async def get_by_id(cls, id: str) -> Optional[User]:
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[USER][GETBY][ID] not_none_args: {id}")
                if database.session:
                    user = await database.session.execute(select(User).filter(User.id == id))  # type: ignore
                    if not user:
                        raise LookupError("User not found!")
                    return user  # type: ignore
            except Exception as exception:
                app_logger.error(f"[USER][GETBY][ID] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[User]:
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[USER][GETBY][EMAIL] not_none_args: {email}")
                if database.session:
                    result = await database.session.execute(select(User).where(User.email == email))  # type: ignore
                    user = result.scalars().first()
                    if not user:
                        raise LookupError("User not found!")
                    return user
            except Exception as exception:
                app_logger.error(f"[USER][GETBY][EMAIL] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    async def partial_update_by_id(cls, id: str, first_name: str | None, last_name: str | None, email: str | None, hashed_password: str | None, active: bool | None) -> Optional[User]:
        async with DbConnectionHandler() as database:
            try:
                if database.session:
                    result = await database.session.execute(select(User).filter(User.id == id))  # type: ignore
                    user = result.scalars().first()
                    if not user:
                        raise ValueError("User not found")

                args = {"first_name": first_name, "last_name": last_name, "email": email, "hashed_password": hashed_password, "active": active}

                not_none_args = {k: v for k, v in args.items() if v is not None}

                app_logger.info(f"[USER][PARTIAL][UPDATE] not_none_args: {not_none_args}")

                for attr, value in not_none_args.items():
                    setattr(User, attr, value)

                if database.session:
                    database.session.add(user)
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[USER][PARTIAL][UPDATE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    async def delete(cls, id: str):
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[USER][DELETE] user_id: {id}")
                if database.session:
                    await database.session.execute(delete(User).where(User.id == id))
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[USER][DELETE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    def verify_password(cls, plain: str, hashed: str) -> bool:
        return pwd_ctx.verify(plain, hashed)
