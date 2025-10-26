import uuid
from typing import TypedDict

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func, inspect
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
    replaced_by = Column(String, nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

    def to_dict(self) -> RefreshTokenDict:
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        # Convert UUID and datetime objects to strings
        if data.get("id"):
            data["id"] = str(data["id"])
        if data.get("user_id"):
            data["user_id"] = str(data["user_id"])
        if data.get("created_at") is not None:
            data["created_at"] = data["created_at"].isoformat()
        if data.get("expires_at") is not None:
            data["expires_at"] = data["expires_at"].isoformat()

        return data  # type: ignore

    def __repr__(self):
        return f"<RefreshToken(id='{self.id}', user_id='{self.user_id}')>"
