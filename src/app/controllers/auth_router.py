# app/presentation/api/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.app.repositories.jwt_repository import JWTRepository
from src.app.repositories.users_repository import UsersRepository
from src.infra.settings.config import get_settings
from src.infra.settings.logging_config import app_logger
from src.usecases.auth_service import AuthService, InvalidCredentials, RefreshExpired, RefreshInvalid, RefreshNotFound, RefreshReuseDetected

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    return AuthService(UsersRepository(), JWTRepository())


settings = get_settings()


def _set_access_cookie(response: Response, access_token: str):
    app_logger.info(f"[AUTH ROUTES][SET_COOKIE][ACCESS] access_token: {access_token}")
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _set_refresh_cookie(response: Response, jti: str, raw_refresh: str):
    app_logger.info(f"[AUTH ROUTES][SET_COOKIE][REFRESH] raw_refresh: {raw_refresh}")

    # expected cookie format: "<jti>:<raw_refresh>"

    cookie_value = f"{jti}:{raw_refresh}"
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    response.set_cookie(key=settings.REFRESH_COOKIE_NAME, value=cookie_value, httponly=settings.COOKIE_HTTPONLY, secure=settings.COOKIE_SECURE, samesite=settings.COOKIE_SAMESITE, max_age=max_age, path="/")


class LoginRequestBody(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(response: Response, body: LoginRequestBody, auth_service: AuthService = Depends(get_auth_service)):
    try:
        app_logger.info(f"[AUTH ROUTES] [LOGIN] email: {body.email}")
        result = await auth_service.login(body.email, body.password)
    except InvalidCredentials as exc:
        app_logger.error(f"[AUTH ROUTES] [LOGIN] [InvalidCredentials] exc: {exc}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas") from exc
    except Exception as e:
        app_logger.error(f"[AUTH ROUTES] [LOGIN] [Exception] e: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

    # coloca access + refresh em cookies HttpOnly
    _set_access_cookie(response, result["access_token"])
    _set_refresh_cookie(response, result["refresh_jti"], result["refresh_token"])

    # opcional: retornar user_id ou outros dados minimalistas
    return {"user_id": result["user_id"]}


@router.post("/refresh")
async def refresh(request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)

    app_logger.info(f"[AUTH ROUTES] [REFRESH] cookie: {cookie}")

    if not cookie:
        app_logger.error("[AUTH ROUTES] [REFRESH] no cookie found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token ausente")

    # parse cookie (formato jti:raw)
    try:
        jti, raw = cookie.split(":", 1)
    except ValueError as exc:
        # cookie malformado
        app_logger.error(f"[AUTH ROUTES] [REFRESH] [VALUE ERROR] exc: {exc}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh cookie malformado") from exc
    except Exception as e:
        app_logger.error(f"[AUTH ROUTES] [REFRESH] [EXCEPTION] e: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor") from e

    try:
        new = await auth_service.rotate_refresh(raw, jti)
    except (RefreshNotFound, RefreshExpired, RefreshReuseDetected, RefreshInvalid) as e:
        # no caso de reutilização ou invalidação, limpamos cookie
        app_logger.error(f"[AUTH ROUTES] [REFRESH] [RefreshNotFound, RefreshExpired, RefreshReuseDetected, RefreshInvalid] e: {e}")
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")
        response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

    # sobrescreve cookies com novos tokens
    _set_access_cookie(response, new["access_token"])
    _set_refresh_cookie(response, new["refresh_jti"], new["refresh_token"])

    return {"user_id": new["user_id"]}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    app_logger.info(f"[AUTH ROUTES] [LOGOUT] cookie: {cookie}")
    if cookie:
        try:
            jti, raw = cookie.split(":", 1)
        except ValueError as e:
            app_logger.error(f"[AUTH ROUTES] [LOGOUT] [ValueError] e: {e}")
            jti, raw = None, None
        except Exception as e:
            app_logger.error(f"[AUTH ROUTES] [LOGOUT] [EXCEPTION] e: {e}")
            jti, raw = None, None

        if jti and raw:
            await auth_service.logout_by_cookie(raw, jti)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    app_logger.info(f"[AUTH ROUTES] [LOGOUT] cookie.delete before - REFRESH_COOKIE_NAME: {settings.REFRESH_COOKIE_NAME} - ACCESS_COOKIE_NAME: {settings.ACCESS_COOKIE_NAME}")
    # sempre limpa cookies do cliente
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")
    response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
    app_logger.info("[AUTH ROUTES] [LOGOUT] cookie.delete after")

    return response


@router.get("/me")
async def return_user_by_access_token(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    access = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    try:
        if not access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

        user = await auth_service.return_user_by_access_token(access)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find user for provided access token")

        return user

    except Exception as e:
        app_logger.error(f"[AUTH ROUTES] [ME] [EXCEPTION] e: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is not valid") from e
