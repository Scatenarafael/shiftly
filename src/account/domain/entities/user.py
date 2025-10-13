import uuid
from typing import TypedDict

from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class UserDict(TypedDict):
    id: str
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    active: bool
    created_at: str | None


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name = Column(String, index=True)

    last_name = Column(String, index=True)

    email = Column(String, index=True, unique=True)

    hashed_password = Column(String)

    active = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user")

    companies_roles = relationship("UserCompanyRole", back_populates="company_role_user")

    def to_dict(self) -> UserDict:
        return {
            "id": str(getattr(self, "id")),
            "first_name": str(getattr(self, "first_name")),
            "last_name": str(getattr(self, "last_name")),
            "email": str(getattr(self, "email")),
            "hashed_password": str(getattr(self, "hashed_password")),
            "active": getattr(self, "active"),
            "created_at": self.created_at.isoformat() if str(self.created_at) else None,
        }
