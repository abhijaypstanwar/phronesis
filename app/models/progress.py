import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class Progress(Base):
    __tablename__ = "progress"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String, ForeignKey("users.id"), nullable=False)
    lesson_id    = Column(String, ForeignKey("lessons.id"), nullable=False)
    completed    = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    user         = relationship("User", back_populates="progress")
    lesson       = relationship("Lesson", back_populates="progress")
