from typing import Any, Dict, Optional

from passlib.context import CryptContext

from src.account.domain.entities.user import User
from src.account.interfaces.iusers_repository import IUsersRepository
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersRepository(IUsersRepository):
    @classmethod
    def list(cls) -> Optional[list[User]]:
        with DbConnectionHandler() as database:
            try:
                if database.session:
                    users = database.session.query(User).order_by(User.created_at.desc()).all()
                    return users
            except Exception as exception:
                raise exception

    @classmethod
    def create(cls, first_name: str, last_name: str, email: str, hashed_password: str, active: bool) -> Optional[User]:
        with DbConnectionHandler() as database:
            try:
                new_register = User(first_name=first_name, last_name=last_name, email=email, hashed_password=hashed_password, active=active)

                app_logger.info(f"[USER][CREATE] new_register: (first_name: {new_register.first_name}, last_name: {new_register.last_name}, email: {new_register.email}, active: {new_register.active})")

                if not new_register:
                    raise ValueError("Could not create user")

                if database.session:
                    database.session.add(new_register)
                    database.session.commit()
                    database.session.refresh(new_register)
                    return new_register
            except Exception as exception:
                raise exception

    @classmethod
    def get_by_id(cls, id: str) -> Optional[Dict[str, Any]]:
        with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[USER][GETBY][ID] not_none_args: {id}")
                if database.session:
                    user = database.session.query(User).filter(User.id == id).first()
                    if not user:
                        raise LookupError("User not found!")
                    return {
                        "id": user.id,
                        "sent_to_server_status": user.sent_to_server_status,
                        "server_user_uuid": user.server_user_uuid,
                        "fuel": user.fuel,
                        "partner": user.partner,
                        "gauge": user.gauge,
                        "measurement_scan": user.measurement_scan,
                        "created_at": user.created_at,
                    }
            except Exception as exception:
                app_logger.error(f"[USER][GETBY][ID] exception: {exception}")
                if database.session:
                    database.session.rollback()
                raise exception

    @classmethod
    def partial_update_by_id(cls, id: str, first_name: str | None, last_name: str | None, email: str | None, hashed_password: str | None, active: bool | None) -> Optional[User]:
        with DbConnectionHandler() as database:
            try:
                if database.session:
                    user = database.session.query(User).filter(User.id == id).first()
                    if not user:
                        raise ValueError("User not found")

                args = {"first_name": first_name, "last_name": last_name, "email": email, "hashed_password": hashed_password, "active": active}

                not_none_args = {k: v for k, v in args.items() if v is not None}

                app_logger.info(f"[USER][PARTIAL][UPDATE] not_none_args: {not_none_args}")

                for attr, value in not_none_args.items():
                    setattr(User, attr, value)

                if database.session:
                    database.session.add(user)
                    database.session.commit()
            except Exception as exception:
                app_logger.error(f"[USER][PARTIAL][UPDATE] exception: {exception}")
                if database.session:
                    database.session.rollback()
                raise exception

    @classmethod
    def delete(cls, id: str):
        with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[USER][DELETE] user_id: {id}")
                if database.session:
                    database.session.query(User).filter(User.id == id).delete()
                    database.session.commit()
            except Exception as exception:
                app_logger.error(f"[USER][DELETE] exception: {exception}")
                if database.session:
                    database.session.rollback()
                raise exception

    @classmethod
    def verify_password(cls, plain: str, hashed: str) -> bool:
        return pwd_ctx.verify(plain, hashed)
