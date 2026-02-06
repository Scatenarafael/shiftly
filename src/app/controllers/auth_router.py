# app/presentation/api/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.app.controllers.auth_config import AuthCookieSettings
from dataclasses import asdict

from src.app.controllers.schemas.pydantic.auth_schemas import LoginRequestBody, UserIdResponse
from src.app.controllers.schemas.pydantic.user_schemas import UserDetailResponse
from src.app.dependencies import (
    get_auth_cookie_settings,
    get_jwt_repository,
    get_refresh_token_expire_days,
    get_token_service,
    get_users_repository,
)
from src.domain.errors import InvalidCredentials, RefreshExpired, RefreshInvalid, RefreshNotFound, RefreshReuseDetected
from src.interfaces.ijwt_repository import IJWTRepository
from src.interfaces.itoken_service import ITokenService
from src.interfaces.iusers_repository import IUsersRepository
from src.usecases.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    users_repository: IUsersRepository = Depends(get_users_repository),
    jwt_repository: IJWTRepository = Depends(get_jwt_repository),
    token_service: ITokenService = Depends(get_token_service),
    refresh_token_expire_days: int = Depends(get_refresh_token_expire_days),
) -> AuthService:
    return AuthService(users_repository, jwt_repository, token_service, refresh_token_expire_days)


def _set_access_cookie(response: Response, access_token: str, settings: AuthCookieSettings):
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _set_refresh_cookie(response: Response, jti: str, raw_refresh: str, settings: AuthCookieSettings):
    # expected cookie format: "<jti>:<raw_refresh>"

    cookie_value = f"{jti}:{raw_refresh}"
    max_age = settings.refresh_token_expire_days * 24 * 3600
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=cookie_value,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=max_age,
        path="/",
    )


@router.post("/login", response_model=UserIdResponse)
async def login(
    response: Response,
    body: LoginRequestBody,
    auth_service: AuthService = Depends(get_auth_service),
    settings: AuthCookieSettings = Depends(get_auth_cookie_settings),
) -> UserIdResponse:
    try:
        result = await auth_service.login(body.email, body.password)
    except InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas") from exc

    # coloca access + refresh em cookies HttpOnly
    _set_access_cookie(response, result.access_token, settings)
    _set_refresh_cookie(response, result.refresh_jti, result.refresh_token, settings)

    # opcional: retornar user_id ou outros dados minimalistas
    return UserIdResponse(user_id=result.user_id)


@router.post("/refresh", response_model=UserIdResponse)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    settings: AuthCookieSettings = Depends(get_auth_cookie_settings),
) -> UserIdResponse:
    cookie = request.cookies.get(settings.refresh_cookie_name)

    if not cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token ausente")

    # parse cookie (formato jti:raw)
    try:
        jti, raw = cookie.split(":", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh cookie malformado") from exc

    try:
        new = await auth_service.rotate_refresh(raw, jti)
    except (RefreshNotFound, RefreshExpired, RefreshReuseDetected, RefreshInvalid) as e:
        # no caso de reutilização ou invalidação, limpamos cookie
        response.delete_cookie(settings.refresh_cookie_name, path="/")
        response.delete_cookie(settings.access_cookie_name, path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

    # sobrescreve cookies com novos tokens
    _set_access_cookie(response, new.access_token, settings)
    _set_refresh_cookie(response, new.refresh_jti, new.refresh_token, settings)

    return UserIdResponse(user_id=new.user_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    settings: AuthCookieSettings = Depends(get_auth_cookie_settings),
) -> Response:
    cookie = request.cookies.get(settings.refresh_cookie_name)
    if cookie:
        try:
            jti, raw = cookie.split(":", 1)
        except ValueError as e:
            jti, raw = None, None
        except Exception as e:
            jti, raw = None, None

        if jti and raw:
            await auth_service.logout_by_cookie(raw, jti)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    # sempre limpa cookies do cliente
    response.delete_cookie(settings.refresh_cookie_name, path="/")
    response.delete_cookie(settings.access_cookie_name, path="/")

    return response


@router.get("/me", response_model=UserDetailResponse)
async def return_user_by_access_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    settings: AuthCookieSettings = Depends(get_auth_cookie_settings),
):
    access = request.cookies.get(settings.access_cookie_name)

    try:
        if not access:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

        user = await auth_service.return_user_by_access_token(access)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find user for provided access token")

        return UserDetailResponse(**asdict(user))

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is not valid") from exc
