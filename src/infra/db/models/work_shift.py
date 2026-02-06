from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.infra.settings.base import Base


class WorkShift(Base):
    __tablename__ = "work_shifts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    work_day_id = Column(UUID(as_uuid=True), ForeignKey("work_days.id", ondelete="CASCADE"))

    start_time = Column(DateTime(timezone=True), nullable=False)

    end_time = Column(DateTime(timezone=True), nullable=False)

    work_day = relationship("WorkDay", back_populates="work_shifts")
