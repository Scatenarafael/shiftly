from typing import Any, Optional

from src.infra.security import create_access_token, generate_refresh_token_raw, hash_refresh_token, verify_access_token
from src.interfaces.itoken_service import ITokenService


class JWTTokenService(ITokenService):
    def create_access_token(self, subject: str) -> str:
        return create_access_token(subject)

    def verify_access_token(self, token: str) -> Optional[dict[str, Any]]:
        return verify_access_token(token)

    def generate_refresh_token_raw(self) -> str:
        return generate_refresh_token_raw()

    def hash_refresh_token(self, token: str) -> str:
        return hash_refresh_token(token)
