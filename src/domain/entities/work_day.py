from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class WorkDay(Base):
    __tablename__ = "work_days"

    id = Column(Integer, primary_key=True, autoincrement=True)

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"))

    weekday = Column(Integer, nullable=True)

    date = Column(DateTime(timezone=True), nullable=False)

    is_holiday = Column(Boolean, nullable=False, default=False)

    role = relationship("Role", back_populates="work_days")

    work_shifts = relationship("WorkShift", back_populates="work_day", cascade="all, delete-orphan", passive_deletes=True)
