import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)

    users_roles = relationship("UserCompanyRole", back_populates="company")

    def __repr__(self):
        return f"<Company(id='{self.id}', name='{self.name}')>"
