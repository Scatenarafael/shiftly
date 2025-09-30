# app/core/security.py
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.infra.settings.config import get_settings

# Access token (JWT)

settings = get_settings()


def create_access_token(subject: str, expires_delta: int | None = None):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "iat": now, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# Refresh tokens (opaque)


def generate_refresh_token_raw():
    # gera um token opaco seguro + jti encodado dentro, mas vamos guardar jti separado no DB
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    # usar sha256 — armazenamos o hash no DB
    return hashlib.sha256(token.encode()).hexdigest()
