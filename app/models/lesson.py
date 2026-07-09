import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Lesson(Base):
    __tablename__ = "lessons"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id    = Column(String, ForeignKey("courses.id"), nullable=False)
    title        = Column(String, nullable=False)
    content      = Column(Text, nullable=True)
    order        = Column(Integer, nullable=False)
    duration_min = Column(Integer, nullable=True)
    video_url    = Column(String, nullable=True)
    is_free      = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    course       = relationship("Course", back_populates="lessons")
    progress     = relationship("Progress", back_populates="lesson", cascade="all, delete-orphan")
