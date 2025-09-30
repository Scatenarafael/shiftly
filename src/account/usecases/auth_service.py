# app/usecases/auth_service.py
import hmac
import uuid
from datetime import datetime, timedelta, timezone

from src.infra.security import create_access_token, generate_refresh_token_raw, hash_refresh_token
from src.infra.settings.config import get_settings

settings = get_settings()


# Exceções específicas
class AuthError(Exception): ...


class InvalidCredentials(AuthError): ...


class RefreshNotFound(AuthError): ...


class RefreshReuseDetected(AuthError): ...


class RefreshExpired(AuthError): ...


class RefreshInvalid(AuthError): ...


class AuthService:
    def __init__(self, user_repo, token_repo):
        self.user_repo = user_repo
        self.token_repo = token_repo

    def _new_jti(self) -> str:
        return str(uuid.uuid4())

    def login(self, username: str, password: str):
        """Autenticação inicial"""
        user = self.user_repo.get_by_username(username)
        if not user or not self.user_repo.verify_password(password, user.password_hash):
            raise InvalidCredentials("Usuário ou senha inválidos")

        # access token curto
        access = create_access_token(user.id)

        # cria refresh opaco
        raw_refresh = generate_refresh_token_raw()
        refresh_hash = hash_refresh_token(raw_refresh)
        jti = self._new_jti()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        self.token_repo.save_refresh_token(
            jti=jti,
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
        )

        return {
            "access_token": access,
            "refresh_token": raw_refresh,
            "refresh_jti": jti,
        }

    def rotate_refresh(self, raw_refresh: str, jti: str):
        """Fluxo de rotação de refresh token"""
        record = self.token_repo.get_by_jti(jti)
        if not record:
            raise RefreshNotFound("Refresh token não encontrado")

        if record.revoked:
            # reutilização detectada → revoga cadeia desse usuário
            self.token_repo.revoke_chain_for_user(record.user_id)
            raise RefreshReuseDetected("Refresh reutilizado. Sessões revogadas.")

        # verificar hash com segurança
        if not hmac.compare_digest(record.token_hash, hash_refresh_token(raw_refresh)):
            self.token_repo.revoke_chain_for_user(record.user_id)
            raise RefreshInvalid("Refresh inválido. Sessões revogadas.")

        if record.expires_at < datetime.now(timezone.utc):
            raise RefreshExpired("Refresh expirado")

        # tudo ok → criar novo refresh e revogar o atual
        new_raw = generate_refresh_token_raw()
        new_hash = hash_refresh_token(new_raw)
        new_jti = self._new_jti()
        new_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # salva novo token
        self.token_repo.save_refresh_token(
            jti=new_jti,
            user_id=record.user_id,
            token_hash=new_hash,
            expires_at=new_expires,
        )

        # revoga atual e aponta para o novo
        self.token_repo.revoke_token(record.jti, replaced_by=new_jti)

        # novo access token
        new_access = create_access_token(record.user_id)

        return {
            "access_token": new_access,
            "refresh_token": new_raw,
            "refresh_jti": new_jti,
        }
