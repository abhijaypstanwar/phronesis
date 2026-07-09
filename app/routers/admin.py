from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.auth import get_current_user, require_admin, hash_password

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/setup", response_model=UserResponse, status_code=201)
def setup_admin(name: str, email: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.role == "admin").first():
        raise HTTPException(status_code=409, detail="Admin already exists")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already taken")
    admin = User(name=name, email=email, password=hash_password(password), role="admin", is_verified=True)
    db.add(admin); db.commit(); db.refresh(admin)
    return UserResponse.model_validate(admin)

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return [UserResponse.model_validate(u) for u in db.query(User).order_by(User.created_at.desc()).all()]

@router.get("/users/active", response_model=List[UserResponse])
def get_active_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    users  = db.query(User).filter(User.is_active == True, User.last_login >= cutoff).order_by(User.last_login.desc()).all()
    return [UserResponse.model_validate(u) for u in users]

@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin": raise HTTPException(status_code=403, detail="Cannot deactivate admin")
    user.is_active = False; db.commit(); db.refresh(user)
    return UserResponse.model_validate(user)

@router.patch("/users/{user_id}/reactivate", response_model=UserResponse)
def reactivate_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True; db.commit(); db.refresh(user)
    return UserResponse.model_validate(user)

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin": raise HTTPException(status_code=403, detail="Cannot delete admin")
    db.delete(user); db.commit()
