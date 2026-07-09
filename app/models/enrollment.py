import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String, ForeignKey("users.id"), nullable=False)
    course_id    = Column(String, ForeignKey("courses.id"), nullable=False)
    enrolled_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed    = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    user         = relationship("User", back_populates="enrollments")
    course       = relationship("Course", back_populates="enrollments")
