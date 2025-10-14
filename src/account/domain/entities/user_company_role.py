import uuid

from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class UserCompanyRole(Base):
    __tablename__ = "user_company_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    is_owner = Column(Boolean, default=False)

    # relação com User (corrigido)
    user = relationship("User", back_populates="companies_roles")

    company = relationship("Company", back_populates="users")
    role = relationship("Role", back_populates="user_company_roles")
