# app/presentation/middlewares/auth_middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.interfaces.itoken_service import ITokenService


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token_service: ITokenService, access_cookie_name: str, public_paths: list[str]):
        super().__init__(app)
        self.token_service = token_service
        self.access_cookie_name = access_cookie_name
        self.public_paths = public_paths

    async def dispatch(self, request: Request, call_next):
        # libera rotas públicas
        if any(request.url.path.startswith(p) for p in self.public_paths):
            return await call_next(request)

        # obter access token do cookie
        access_token = request.cookies.get(self.access_cookie_name)
        if not access_token:
            return JSONResponse({"detail": "Access token not found"}, status_code=status.HTTP_401_UNAUTHORIZED)

        payload = self.token_service.verify_access_token(access_token)
        if not payload:
            # token inválido ou expirado
            return JSONResponse({"detail": "Access token invalid or expired"}, status_code=status.HTTP_401_UNAUTHORIZED)

        # coloca user_id no state para uso nos endpoints
        request.state.user_id = payload.get("sub")
        return await call_next(request)
