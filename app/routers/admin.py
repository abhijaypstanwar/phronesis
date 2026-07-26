from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.progress import Progress
from app.schemas.user import UserResponse
from app.services.auth import require_admin, hash_password

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

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    total_users       = db.query(User).filter(User.role != "admin").count()
    total_courses     = db.query(Course).filter(Course.is_published == True).count()
    total_enrollments = db.query(Enrollment).count()
    total_progress    = db.query(Progress).filter(Progress.completed == True).count()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    active_today = db.query(User).filter(User.is_active == True, User.last_login >= cutoff).count()
    return {
        "total_users":       total_users,
        "total_courses":     total_courses,
        "total_enrollments": total_enrollments,
        "lessons_completed": total_progress,
        "active_today":      active_today,
    }

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