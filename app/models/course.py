import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    __tablename__ = "courses"
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title         = Column(String, nullable=False)
    description   = Column(Text, nullable=True)
    price         = Column(Float, default=0.0)
    thumbnail_url = Column(String, nullable=True)
    is_published  = Column(Boolean, default=False)
    instructor_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    instructor    = relationship("User", back_populates="courses")
    lessons       = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments   = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
