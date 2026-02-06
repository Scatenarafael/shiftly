from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.refresh_token import RefreshToken as DomainRefreshToken
from src.infra.db.models.refresh_token import RefreshToken
from src.infra.settings.logging_config import app_logger
from src.interfaces.ijwt_repository import IJWTRepository


class JWTRepository(IJWTRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain_refresh(model: RefreshToken) -> DomainRefreshToken:
        return DomainRefreshToken(
            id=str(model.id),
            user_id=str(model.user_id),
            token_hash=model.token_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            revoked=model.revoked,
            replaced_by=model.replaced_by,
        )

    async def save_refresh_token(self, jti: str, user_id: str, token_hash: str, expires_at: datetime) -> DomainRefreshToken:
        new_register = RefreshToken(id=jti, user_id=user_id, token_hash=token_hash, expires_at=expires_at)

        app_logger.info(f"[REFRESH TOKEN][SAVE] new_register: (id= {jti}, user_id= {user_id}, token_hash= {token_hash}, expires_at= {expires_at})")

        self.session.add(new_register)
        await self.session.commit()
        await self.session.refresh(new_register)
        return self._to_domain_refresh(new_register)

    async def get_by_jti(self, jti: str) -> Optional[DomainRefreshToken]:
        app_logger.info(f"[REFRESH TOKEN][GETBY][JTI] jti: {jti}")
        stmt = select(RefreshToken).where(RefreshToken.id == jti)
        result = await self.session.scalars(stmt)
        rt = result.first()
        if not rt:
            return None
        return self._to_domain_refresh(rt)

    async def revoke_token(self, token: DomainRefreshToken, replaced_by: str | None = None) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token.id)
            .values(revoked=True, replaced_by=replaced_by)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_token(self, token: DomainRefreshToken) -> None:
        db_token = await self.session.get(RefreshToken, token.id)
        if db_token:
            await self.session.delete(db_token)
            await self.session.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        app_logger.info(f"[REFRESH TOKEN][REVOKEALL] user_id: {user_id}")
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)  # noqa: E712
            .values(revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()
