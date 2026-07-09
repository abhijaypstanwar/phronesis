import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Text, Boolean
from app.database import Base

class StudyPlan(Base):
    __tablename__ = "study_plans"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String, nullable=False)
    course_id    = Column(String, nullable=False)
    plan_text    = Column(Text, nullable=False)
    target_date  = Column(String, nullable=True)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
