import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Integer, Text
from app.database import Base

class QuizResult(Base):
    __tablename__ = "quiz_results"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, nullable=False)
    course_id   = Column(String, nullable=False)
    lesson_id   = Column(String, nullable=True)
    score       = Column(Integer, nullable=False)
    total       = Column(Integer, nullable=False)
    questions   = Column(Text, nullable=False)  # JSON string
    answers     = Column(Text, nullable=False)  # JSON string
    taken_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))