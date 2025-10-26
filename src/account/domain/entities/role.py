import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)

    user_company_roles = relationship("UserCompanyRole", back_populates="role")

    def __repr__(self):
        return f"<Role(id='{self.id}', name='{self.name}')>"
