from datetime import datetime
from typing import Optional

from sqlalchemy import select, update

from src.account.domain.entities.refresh_token import RefreshToken
from src.account.interfaces.ijwt_repository import IJWTRepository
from src.infra.settings.connection import DbConnectionHandler
from src.infra.settings.logging_config import app_logger


class JWTRepository(IJWTRepository):
    @classmethod
    async def save_refresh_token(cls, jti: str, user_id: str, token_hash: str, expires_at: datetime) -> Optional[RefreshToken]:
        async with DbConnectionHandler() as database:
            try:
                new_register = RefreshToken(id=jti, user_id=user_id, token_hash=token_hash, expires_at=expires_at)

                app_logger.info(f"[REFRESH TOKEN][SAVE] new_register: (id= {jti}, user_id= {user_id}, token_hash= {token_hash}, expires_at= {expires_at})")

                if not new_register:
                    raise ValueError("Could not save refresh_token")

                if database.session:
                    database.session.add(new_register)
                    await database.session.commit()
                    await database.session.refresh(new_register)
                    return new_register
            except Exception as exception:
                raise exception

    @classmethod
    async def get_by_jti(cls, jti: str) -> Optional[RefreshToken]:
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][GETBY][JTI] jti: {jti}")
                if database.session:
                    stmt = select(RefreshToken).where(RefreshToken.id == jti)
                    result = await database.session.scalars(stmt)
                    rt = result.first()
                    if not rt:
                        raise LookupError("RefreshToken not found!")
                    return rt
            except Exception as exception:
                app_logger.error(f"[REFRESH TOKEN][GETBY][JTI] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    async def revoke_token(cls, token: RefreshToken, replaced_by: str | None = None):
        token.revoked = True  # type: ignore
        if replaced_by:
            token.replaced_by = replaced_by  # type: ignore

        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][REVOKE] token: {token}, replaced_by: {replaced_by}")

                if not token:
                    raise ValueError("Could not save refresh_token")

                if database.session:
                    database.session.add(token)
                    await database.session.commit()
                    return token
            except Exception as exception:
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    async def delete_token(cls, token: RefreshToken):
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][DELETE] token: {token}")
                if database.session:
                    await database.session.delete(token)
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[REFRESH TOKEN][DELETE] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception

    @classmethod
    async def revoke_all_for_user(cls, user_id: str):
        async with DbConnectionHandler() as database:
            try:
                app_logger.info(f"[REFRESH TOKEN][REVOKEALL] user_id: {user_id}")
                if database.session:
                    stmt = (
                        update(RefreshToken)
                        .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)  # noqa: E712
                        .values(revoked=True)
                    )
                    await database.session.execute(stmt)
                    await database.session.commit()
            except Exception as exception:
                app_logger.error(f"[REFRESH TOKEN][REVOKEALL] exception: {exception}")
                if database.session:
                    await database.session.rollback()
                raise exception
