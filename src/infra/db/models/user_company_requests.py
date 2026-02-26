import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.domain.entities.user_company_requests import UserCompanyRequestStatus
from src.infra.settings.base import Base


class UserCompanyRequest(Base):
    __tablename__ = "user_company_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))

    status = Column(
        SqlEnum(
            UserCompanyRequestStatus,
            name="user_company_request_status",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        default=UserCompanyRequestStatus.PENDING,
    )
    accepted = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User")
    company = relationship("Company")

    def __repr__(self):
        return f"<UserCompanyRequest(user_id='{self.user_id}', company_id='{self.company_id}', status='{self.status}', accepted='{self.accepted}')>"
