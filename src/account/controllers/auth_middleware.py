# app/middleware/auth_middleware.py
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from src.infra.settings.config import get_settings

settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ignorar endpoints públicos
        public_paths = ["/login", "/register", "/refresh", "/docs", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # extrair header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Token de acesso não fornecido"}, status_code=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                return JSONResponse({"detail": "Token expirado"}, status_code=401)

            # coloca user_id no state (disponível para endpoints)
            request.state.user_id = payload.get("sub")

        except JWTError:
            return JSONResponse({"detail": "Token inválido"}, status_code=401)

        return await call_next(request)
