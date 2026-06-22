import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest, MessageResponse, ResendOTPRequest,
    ResetPasswordRequest, TokenResponse, UserLogin, UserRegister,
    UserResponse, VerifyOTPRequest,
)
from app.services.auth import create_access_token, get_current_user, hash_password, verify_password
from app.services.email import generate_otp, send_otp_email, send_reset_email

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    otp     = generate_otp()
    otp_exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    new_user = User(
        name=payload.name, email=payload.email,
        password=hash_password(payload.password),
        otp_code=otp, otp_expires_at=otp_exp, is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    try:
        send_otp_email(to=new_user.email, name=new_user.name, otp=otp)
    except Exception:
        pass
    token = create_access_token({"sub": str(new_user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(new_user))


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found with this email")
    if user.is_verified:
        return MessageResponse(message="Email already verified")
    if not user.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP found. Please request a new one.")
    expires = user.otp_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one.")
    if payload.otp != user.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect OTP. Please try again.")
    user.is_verified    = True
    user.otp_code       = None
    user.otp_expires_at = None
    db.commit()
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-otp", response_model=MessageResponse)
def resend_otp(payload: ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found with this email")
    if user.is_verified:
        return MessageResponse(message="Email is already verified")
    otp     = generate_otp()
    otp_exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    user.otp_code       = otp
    user.otp_expires_at = otp_exp
    db.commit()
    try:
        send_otp_email(to=user.email, name=user.name, otp=otp)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP email.")
    return MessageResponse(message="OTP sent successfully. Check your email.")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        token     = secrets.token_urlsafe(32)
        token_exp = datetime.now(timezone.utc) + timedelta(minutes=15)
        user.reset_token            = token
        user.reset_token_expires_at = token_exp
        db.commit()
        try:
            send_reset_email(to=user.email, name=user.name, reset_token=token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send reset email.")
    return MessageResponse(message="If an account exists with this email, a reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")
    expires = user.reset_token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link has expired.")
    user.password               = hash_password(payload.new_password)
    user.reset_token            = None
    user.reset_token_expires_at = None
    db.commit()
    return MessageResponse(message="Password reset successfully. You can now log in.")


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    name: str = None,
    current_password: str = None,
    new_password: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if name:
        if not name.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name cannot be blank")
        current_user.name = name.strip()
    if new_password:
        if not current_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is required")
        if not verify_password(current_password, current_user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
        if len(new_password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be at least 8 characters")
        current_user.password = hash_password(new_password)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
