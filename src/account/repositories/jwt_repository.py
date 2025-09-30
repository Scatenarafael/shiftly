from datetime import datetime
from typing import Optional

from src.account.domain.entities.refresh_token import RefreshToken
from src.account.interfaces.ijwt_repository import IJWTRepository
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger


class JWTRepository(IJWTRepository):
    @classmethod
    def save_refresh_token(cls, jti: str, user_id: str, token_hash: str, expires_at: datetime) -> Optional[RefreshToken]:
        with DbConnectionHandler() as database:
            try:
                new_register = RefreshToken(id=jti, user_id=user_id, token_hash=token_hash, expires_at=expires_at)

                app_logger.info(f"[REFRESH TOKEN][SAVE] new_register: (id= {jti}, user_id= {user_id}, token_hash= {token_hash}, expires_at= {expires_at})")

                if not new_register:
                    raise ValueError("Could not save refresh_token")

                if database.session:
                    database.session.add(new_register)
                    database.session.commit()
                    database.session.refresh(new_register)
                    return new_register
            except Exception as exception:
                raise exception

    @classmethod
    def get_by_jti(cls, jti: str) -> Optional[RefreshToken]:
        with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][GETBY][JTI] jti: {jti}")
                if database.session:
                    rt = database.session.query(RefreshToken).filter(RefreshToken.id == jti).first()
                    if not rt:
                        raise LookupError("RefreshToken not found!")
                    return rt
            except Exception as exception:
                app_logger.error(f"[REFRESH TOKEN][GETBY][JTI] exception: {exception}")
                if database.session:
                    database.session.rollback()
                raise exception

    @classmethod
    def revoke_token(cls, token: RefreshToken, replaced_by: str | None = None):
        token.revoked = True  # type: ignore
        if replaced_by:
            token.replaced_by = replaced_by  # type: ignore

        with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][REVOKE] token: {token}, replaced_by: {replaced_by}")

                if not token:
                    raise ValueError("Could not save refresh_token")

                if database.session:
                    database.session.add(token)
                    database.session.commit()
                    return token
            except Exception as exception:
                raise exception

    @classmethod
    def delete_token(cls, token: RefreshToken):
        with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][DELETE] token: {token}")
                if database.session:
                    database.session.delete(token)
                    database.session.commit()
            except Exception as exception:
                app_logger.error(f"[REFRESH TOKEN][DELETE] exception: {exception}")
                if database.session:
                    database.session.rollback()
                raise exception

    @classmethod
    def revoke_all_for_user(cls, user_id: str):
        with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][REVOKEALL] user_id: {user_id}")
                if database.session:
                    database.session.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False).update({"revoked": True})  # noqa: E712
                    database.session.commit()
            except Exception as exception:
                app_logger.error(f"[REFRESH TOKEN][REVOKEALL] exception: {exception}")
                if database.session:
                    database.session.rollback()
                raise exception
