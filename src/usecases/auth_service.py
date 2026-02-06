import hmac
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.domain.errors import InvalidCredentials, RefreshExpired, RefreshInvalid, RefreshNotFound, RefreshReuseDetected
from src.interfaces.ijwt_repository import IJWTRepository
from src.interfaces.itoken_service import ITokenService
from src.interfaces.iusers_repository import IUsersRepository
from src.interfaces.types.user_types import UserDetailDTO
from src.usecases.users.mappers import to_user_detail


@dataclass(slots=True)
class AuthTokensDTO:
    access_token: str
    refresh_token: str
    refresh_jti: str
    user_id: str


class AuthService:
    def __init__(self, user_repo: IUsersRepository, token_repo: IJWTRepository, token_service: ITokenService, refresh_token_expire_days: int):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.token_service = token_service
        self.refresh_token_expire_days = refresh_token_expire_days

    def _new_jti(self) -> str:
        return str(uuid.uuid4())

    async def login(self, email: str, password: str) -> AuthTokensDTO:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.hashed_password or not self.user_repo.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Usuário ou senha inválidos")

        access = self.token_service.create_access_token(user.id)
        raw_refresh = self.token_service.generate_refresh_token_raw()
        refresh_hash = self.token_service.hash_refresh_token(raw_refresh)

        jti = self._new_jti()
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)

        await self.token_repo.save_refresh_token(
            jti=jti,
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
        )

        return AuthTokensDTO(access_token=access, refresh_token=raw_refresh, refresh_jti=jti, user_id=user.id)

    async def rotate_refresh(self, raw_refresh: str, jti: str) -> AuthTokensDTO:
        record = await self.token_repo.get_by_jti(jti)
        if not record:
            raise RefreshNotFound("Refresh token não encontrado")

        if record.revoked:
            await self.token_repo.revoke_all_for_user(record.user_id)
            raise RefreshReuseDetected("Refresh reutilizado. Sessões revogadas.")

        if not hmac.compare_digest(record.token_hash, self.token_service.hash_refresh_token(raw_refresh)):
            await self.token_repo.revoke_all_for_user(record.user_id)
            raise RefreshInvalid("Refresh inválido. Sessões revogadas.")

        if record.expires_at < datetime.now(timezone.utc):
            raise RefreshExpired("Refresh expirado")

        await self.token_repo.revoke_all_for_user(record.user_id)

        new_raw = self.token_service.generate_refresh_token_raw()
        new_hash = self.token_service.hash_refresh_token(new_raw)
        new_jti = self._new_jti()
        new_expires = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)

        await self.token_repo.save_refresh_token(
            jti=new_jti,
            user_id=record.user_id,
            token_hash=new_hash,
            expires_at=new_expires,
        )

        new_access = self.token_service.create_access_token(record.user_id)

        return AuthTokensDTO(access_token=new_access, refresh_token=new_raw, refresh_jti=new_jti, user_id=record.user_id)

    async def logout_by_cookie(self, raw_refresh: str, jti: str) -> bool:
        record = await self.token_repo.get_by_jti(jti)
        if record and hmac.compare_digest(record.token_hash, self.token_service.hash_refresh_token(raw_refresh)):
            await self.token_repo.revoke_token(record)
            return True
        return False

    async def return_user_by_access_token(self, access_token: str) -> UserDetailDTO:
        payload = self.token_service.verify_access_token(access_token)
        if not payload:
            raise InvalidCredentials("Token is not valid")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentials("Token is not valid")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentials("User not found")

        return to_user_detail(user)
