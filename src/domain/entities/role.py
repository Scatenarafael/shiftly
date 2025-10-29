import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)

    number_of_cooldown_days = Column(Integer, nullable=False, default=0)

    user_company_roles = relationship("UserCompanyRole", back_populates="role")

    work_days = relationship("WorkDay", back_populates="role", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<Role(id='{self.id}', name='{self.name}')>"
