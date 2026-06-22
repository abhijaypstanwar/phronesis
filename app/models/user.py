import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, String
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id        = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email     = Column(String, nullable=False, unique=True, index=True)
    password  = Column(String, nullable=False)
    name      = Column(String, nullable=False)
    role      = Column(String, default="student")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    otp_code       = Column(String, nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)

    reset_token            = Column(String, nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    last_login = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
