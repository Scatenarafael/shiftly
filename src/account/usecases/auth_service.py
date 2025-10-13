# type: ignore
import hmac
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import inspect

from src.account.interfaces.ijwt_repository import IJWTRepository
from src.account.interfaces.iusers_repository import IUsersRepository
from src.infra.security import create_access_token, generate_refresh_token_raw, hash_refresh_token, verify_access_token
from src.infra.settings.config import get_settings
from src.infra.settings.logging_config import app_logger

settings = get_settings()


# Exceções específicas
class AuthError(Exception): ...


class InvalidCredentials(AuthError): ...


class RefreshNotFound(AuthError): ...


class RefreshReuseDetected(AuthError): ...


class RefreshExpired(AuthError): ...


class RefreshInvalid(AuthError): ...


def model_to_dict(model):
    """Convert a SQLAlchemy model instance to a dictionary."""
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}


class AuthService:
    def __init__(self, user_repo: IUsersRepository, token_repo: IJWTRepository):
        # instancing required repositories
        self.user_repo = user_repo
        self.token_repo = token_repo

    # creating new jti
    def _new_jti(self) -> str:
        return str(uuid.uuid4())

    # validating user and password, returning access and refresh tokens
    async def login(self, email: str, password: str):
        app_logger.debug(f"[AUTH SERVICE] [LOGIN] email: {email}")

        # Initial authentication
        user = await self.user_repo.get_by_email(email)

        user_json = user.to_dict() if user else None

        app_logger.debug(f"[AUTH SERVICE] [LOGIN] user_json: {user_json}")
        app_logger.debug(f"[AUTH SERVICE] [LOGIN] user_json.get(hashed_password): {user_json.get('hashed_password')}")

        if not user_json or not self.user_repo.verify_password(password, user_json.get("hashed_password")):
            app_logger.error("[AUTH SERVICE] [LOGIN] Could not authenticate user")
            raise InvalidCredentials("Usuário ou senha inválidos")

        # creating access token
        access = create_access_token(str(user_json.get("id")))
        app_logger.debug(f"[AUTH SERVICE] [LOGIN] access: {access}")

        # creating refresh token
        raw_refresh = generate_refresh_token_raw()
        refresh_hash = hash_refresh_token(raw_refresh)
        app_logger.debug(f"[AUTH SERVICE] [LOGIN] refresh_hash: {refresh_hash}")

        jti = self._new_jti()
        app_logger.debug(f"[AUTH SERVICE] [LOGIN] jti: {jti}")
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        app_logger.debug(f"[AUTH SERVICE] [LOGIN] expires_at: {expires_at}")

        await self.token_repo.save_refresh_token(
            jti=jti,
            user_id=str(user_json.get("id")),
            token_hash=refresh_hash,
            expires_at=expires_at,
        )

        return {"access_token": access, "refresh_token": raw_refresh, "refresh_jti": jti, "user_id": str(user_json.get("id"))}

    async def rotate_refresh(self, raw_refresh: str, jti: str):
        # refreshing token
        record_model = await self.token_repo.get_by_jti(jti)

        record = record_model.to_dict() if record_model else None

        if not record:
            raise RefreshNotFound("Refresh token não encontrado")

        if record.get("revoked"):
            # recicling detected → lets revolke this user chain
            await self.token_repo.revoke_all_for_user(str(record.get("user_id")))
            raise RefreshReuseDetected("Refresh reutilizado. Sessões revogadas.")

        # validates the hash securely
        if not hmac.compare_digest(record.get("token_hash"), hash_refresh_token(raw_refresh)):
            await self.token_repo.revoke_all_for_user(str(record.get("user_id")))
            raise RefreshInvalid("Refresh inválido. Sessões revogadas.")

        expires_at = datetime.fromisoformat(record["expires_at"])  # string -> datetime

        if expires_at < datetime.now(timezone.utc):
            raise RefreshExpired("Refresh expirado")

        # revokes old refresh token
        await self.token_repo.revoke_all_for_user(str(record.get("user_id")))
        # await self.token_repo.revoke_token(record_model, replaced_by=new_jti)

        # recicling should be done only if refresh_token is valid and not expired
        new_raw = generate_refresh_token_raw()
        new_hash = hash_refresh_token(new_raw)
        new_jti = self._new_jti()
        new_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # saving new refresh token
        await self.token_repo.save_refresh_token(
            jti=new_jti,
            user_id=record.get("user_id"),
            token_hash=new_hash,
            expires_at=new_expires,
        )

        # new access token
        new_access = create_access_token(str(record.get("user_id")))

        return {
            "access_token": new_access,
            "refresh_token": new_raw,
            "refresh_jti": new_jti,
            "user_id": str(record.get("user_id")),
        }

    async def logout_by_cookie(self, raw_refresh: str, jti: str) -> bool:
        rec = await self.token_repo.get_by_jti(jti)

        app_logger.info(f"[AUTH SERVICE] [LOGOUT BY COOKIE] rec: {rec}, raw_refresh: {raw_refresh}, jti: {jti}")

        if rec and hmac.compare_digest(rec.token_hash, hash_refresh_token(raw_refresh)):
            await self.token_repo.revoke_token(rec)
            return True
        return False

    async def return_user_by_access_token(self, access_token: str):
        app_logger.debug(f"[AUTH SERVICE] [RETURN USER BY ACCESS TOKEN] access_token: {access_token}")

        payload = verify_access_token(access_token)

        app_logger.debug(f"[AUTH SERVICE] [RETURN USER BY ACCESS TOKEN] payload: {payload}")

        if not payload:
            raise InvalidCredentials("Token is not valid")

        user_id = payload.get("sub")

        app_logger.debug(f"[AUTH SERVICE] [RETURN USER BY ACCESS TOKEN] user_id: {user_id}")

        if not user_id:
            raise InvalidCredentials("Token is not valid")

        user = await self.user_repo.get_by_id(user_id)

        app_logger.debug(f"[AUTH SERVICE] [RETURN USER BY ACCESS TOKEN] user: {user}")

        # rows = user.mappings().all()

        # for row in rows:
        #     user_from_row = row["User"]

        # if not user_from_row:
        #     raise InvalidCredentials("User not found")

        delattr(user, "hashed_password")  # remove hashed_password before returning
        # delattr(user_from_row, "hashed_password")  # remove hashed_password before returning

        return user
