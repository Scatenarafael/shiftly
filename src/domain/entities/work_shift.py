from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer

from src.infra.settings.base import Base


class WorkShift(Base):
    __tablename__ = "work_shifts"

    work_day_id = Column(UUID(as_uuid=True), ForeignKey("work_days.id", ondelete="CASCADE"))

    weekday = Column(Integer, nullable=True)

    start_time = Column(DateTime(timezone=True), nullable=False)

    end_time = Column(DateTime(timezone=True), nullable=False)
