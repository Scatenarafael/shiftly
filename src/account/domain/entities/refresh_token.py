import uuid
from typing import TypedDict

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class RefreshTokenDict(TypedDict):
    id: str
    user_id: str
    token_hash: str
    created_at: str | None
    expires_at: str | None
    revoked: bool
    replaced_by: str | None


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    replaced_by = Column(String, nullable=True)  # jti of new token

    user = relationship("User", back_populates="refresh_tokens")

    def to_dict(self) -> RefreshTokenDict:
        return {
            "id": str(getattr(self, "id")),
            "user_id": str(getattr(self, "user_id")),
            "token_hash": getattr(self, "token_hash"),
            "created_at": self.created_at.isoformat() if str(self.created_at) else None,
            "expires_at": self.expires_at.isoformat() if str(self.expires_at) else None,
            "revoked": getattr(self, "revoked"),
            "replaced_by": getattr(self, "replaced_by"),
        }
