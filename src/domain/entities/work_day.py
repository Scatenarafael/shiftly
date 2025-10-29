from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class WorkDay(Base):
    __tablename__ = "work_days"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"))

    weekday = Column(Integer, nullable=True)

    date = Column(DateTime(timezone=True), nullable=False)

    is_holiday = Column(Boolean, nullable=False, default=False)

    work_shifts = relationship("WorkShift", back_populates="work_day", cascade="all, delete-orphan", passive_deletes=True)
