from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    @field_validator("password")
    @classmethod
    def pw_strength(cls, v):
        if len(v) < 8: raise ValueError("Password must be at least 8 characters")
        return v
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip(): raise ValueError("Name cannot be blank")
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    @field_validator("new_password")
    @classmethod
    def pw_strength(cls, v):
        if len(v) < 8: raise ValueError("Password must be at least 8 characters")
        return v

class ResendOTPRequest(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    phone: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
