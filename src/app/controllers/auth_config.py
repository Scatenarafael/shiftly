from dataclasses import dataclass


@dataclass(slots=True)
class AuthCookieSettings:
    access_cookie_name: str
    refresh_cookie_name: str
    cookie_httponly: bool
    cookie_secure: bool
    cookie_samesite: str | None
    access_token_expire_minutes: int
    refresh_token_expire_days: int
